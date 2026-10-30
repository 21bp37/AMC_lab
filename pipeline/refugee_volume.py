"""Wariant hipotezy na WOLUMENIE TEMATU „o uchodźcach / Ukraińcach w Polsce” (bez oceny narracji).

Dlaczego: słowniki i score postawy (anty) nie spełniły progów walidacji (reports/M_codebook_gold_standard.tex),
a karta M1 przewiduje wtedy słabszą wersję hipotezy: korelacja natężenia TEMATU w X z natężeniem w kanałach prorosyjskich
(kontrola: proukraińskie). To NIE jest test „negatywnych treści”; mówi o wspólnej uwadze do tematu.

Dwa kroki (Telegram jest ciężki, więc szeregi zapisujemy raz):
  python -m pipeline.refugee_volume build --posts "data/telegram/posts_2022_part_*.csv" --clusters data/telegram/leiden_clusters.csv
  python -m pipeline.refugee_volume test

Reguła decyzyjna jest ta sama co w METODY.md §4 (kryteria a, b, c), zamrożona przed uruchomieniem na pełnych danych.
Warianty (odporność): bez 2.06.2022, bez dni wydarzeń ±1, z kopiami (nie tylko unikalne teksty), bez filtra (cały temat UA+PL),
udziały zamiast liczności, filtr v0.3 (Telegram) zamiast v0.4.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import config, leadlag, refugee_gate

SIDE_KEY = {"Pro-Russian": "ru", "Pro-Ukrainian": "ua"}
OUT_DAILY = config.PROCESSED / "refugee_volume_daily.csv"
SPIKE_DAY = "2022-06-02"      # największy dzień w prorosyjskim Telegramie po filtrze (karta, codebook §4)


def index() -> pd.DatetimeIndex:
    return pd.date_range(config.EFFECTIVE_START, config.STUDY_END, freq="D")


# --------------------------------------------------------------------------- budowa szeregów
def x_series(tw: pd.DataFrame, idx: pd.DatetimeIndex) -> pd.DataFrame:
    """X: dziennie liczba RÓŻNYCH treści (kaskad) w oknie: wszystkie i „o uchodźcach” (bramka v0.4 na tekście bez „RT @”)."""
    d = tw[(tw["day"] >= idx[0]) & (tw["day"] <= idx[-1])].copy()
    d["about"] = d["clean_text"].map(refugee_gate.x_about)
    d["strict"] = d["clean_text"].map(refugee_gate.x_about_strict)
    out = pd.DataFrame({
        "x_all": d.groupby("day")["cascade_key"].nunique(),
        "x_about": d[d["about"]].groupby("day")["cascade_key"].nunique(),
        "x_about_rows": d[d["about"]].groupby("day").size(),
        "x_about_strict": d[d["strict"]].groupby("day")["cascade_key"].nunique(),
    }).reindex(idx).fillna(0).astype(int)
    out.index.name = "day"
    return out


def tg_series(df: pd.DataFrame, idx: pd.DatetimeIndex) -> pd.DataFrame:
    """Telegram (posty już po filtrze Ukraina+Polska, kolumny: day, side, message, copy_key; opcjonalnie is_refugee = v0.3).
    Na stronę: temat (bez filtra), o uchodźcach v0.4 (unikalne teksty i z kopiami), o uchodźcach v0.3 (unikalne)."""
    d = df[df["side"].isin(SIDE_KEY)].copy()
    d["about"] = d["message"].fillna("").map(refugee_gate.telegram_about)
    d["strict"] = d["message"].fillna("").map(refugee_gate.telegram_about_strict)
    cols = {}
    for side, k in SIDE_KEY.items():
        s = d[d["side"] == side]
        a = s[s["about"]]
        cols[f"tg_{k}_topic"] = s.groupby("day")["copy_key"].nunique()
        cols[f"tg_{k}_about"] = a.groupby("day")["copy_key"].nunique()
        cols[f"tg_{k}_about_rows"] = a.groupby("day").size()
        cols[f"tg_{k}_about_strict"] = s[s["strict"]].groupby("day")["copy_key"].nunique()
        if "is_refugee" in s:
            cols[f"tg_{k}_about_v03"] = s[s["is_refugee"]].groupby("day")["copy_key"].nunique()
    out = pd.DataFrame(cols).reindex(idx).fillna(0).astype(int)
    out.index.name = "day"
    return out


def peak_dump(tw: pd.DataFrame, tg: pd.DataFrame, d: pd.DataFrame, n_days: int = 3, top: int = 20) -> pd.DataFrame:
    """Najczęstsze treści „o uchodźcach” w szczytowych dniach (X: kaskady wg liczby wpisów; Telegram RU: teksty wg liczby kopii),
    żeby ocenić ręcznie, czy szczyty to prawdziwy temat uchodźczy, czy szum bramki. Dni: top `n_days` szeregu + 9.05 i 2.06."""
    extra = [pd.Timestamp("2022-05-09"), pd.Timestamp(SPIKE_DAY)]
    rows = []
    t = tw.copy()
    t["about"] = t["clean_text"].map(refugee_gate.x_about)
    t["strict"] = t["clean_text"].map(refugee_gate.x_about_strict)
    days = list(dict.fromkeys(list(d["x_about"].nlargest(n_days).index) + extra))
    for day in days:
        s = t[(t["day"] == day) & t["about"]]
        g = s.groupby("cascade_key").agg(n=("clean_text", "size"), strict=("strict", "max"), text=("clean_text", "first"))
        for _, r in g.sort_values("n", ascending=False).head(top).iterrows():
            rows.append({"platforma": "X", "dzień": day.date(), "n": int(r["n"]), "ścisła": bool(r["strict"]), "tekst": r["text"][:300]})
    g0 = tg[tg["side"] == "Pro-Russian"].copy()
    g0["about"] = g0["message"].fillna("").map(refugee_gate.telegram_about)
    g0["strict"] = g0["message"].fillna("").map(refugee_gate.telegram_about_strict)
    days = list(dict.fromkeys(list(d["tg_ru_about"].nlargest(n_days).index) + extra))
    for day in days:
        s = g0[(g0["day"] == day) & g0["about"]]
        g = s.groupby("copy_key").agg(n=("message", "size"), strict=("strict", "max"), text=("message", "first"))
        for _, r in g.sort_values("n", ascending=False).head(top).iterrows():
            rows.append({"platforma": "Telegram RU", "dzień": day.date(), "n": int(r["n"]), "ścisła": bool(r["strict"]), "tekst": str(r["text"])[:300]})
    return pd.DataFrame(rows)


def build(tw: pd.DataFrame, tg: pd.DataFrame) -> pd.DataFrame:
    idx = index()
    return pd.concat([x_series(tw, idx), tg_series(tg, idx)], axis=1)


# --------------------------------------------------------------------------- warianty
def smooth_days(s: pd.Series, days, window: int = 7) -> pd.Series:
    """Zastępuje wskazane dni medianą okolicznych dni (±window, bez nich samych); zachowuje ciągły indeks dla różnicowania."""
    out = s.astype(float).copy()
    bad = pd.DatetimeIndex(days)
    for d in bad:
        if d not in out.index:
            continue
        nb = s.loc[d - pd.Timedelta(days=window): d + pd.Timedelta(days=window)].drop(bad, errors="ignore")
        if len(nb):
            out.loc[d] = float(nb.median())
    return out


def event_days(margin: int = 1) -> list[pd.Timestamp]:
    days = []
    for k in config.EVENTS:
        c = pd.Timestamp(k)
        days += [c + pd.Timedelta(days=i) for i in range(-margin, margin + 1)]
    return days


def _share(a: pd.Series, b: pd.Series) -> pd.Series:
    r = a / b.replace(0, np.nan)
    return r.fillna(r.median() if r.notna().any() else 0.0)


def variants(d: pd.DataFrame) -> dict[str, tuple[pd.Series, pd.Series, pd.Series]]:
    """Nazwa -> (X_RU, X_UA, Y). Wszystkie na wspólnym indeksie dni."""
    v = {"główny: unikalne, bramka v0.4": (d["tg_ru_about"], d["tg_ua_about"], d["x_about"]),
         "z kopiami (nie tylko unikalne)": (d["tg_ru_about_rows"], d["tg_ua_about_rows"], d["x_about_rows"]),
         "bez filtra (cały temat UA+PL)": (d["tg_ru_topic"], d["tg_ua_topic"], d["x_all"]),
         "udziały (o uchodźcach / temat)": (_share(d["tg_ru_about"], d["tg_ru_topic"]),
                                            _share(d["tg_ua_about"], d["tg_ua_topic"]), _share(d["x_about"], d["x_all"]))}
    if "x_about_strict" in d:
        v["ścisła bramka (tylko rzeczownik uchodźczy)"] = (d["tg_ru_about_strict"], d["tg_ua_about_strict"], d["x_about_strict"])
    if "tg_ru_about_v03" in d:
        v["Telegram: filtr v0.3"] = (d["tg_ru_about_v03"], d["tg_ua_about_v03"], d["x_about"])
    base = v["główny: unikalne, bramka v0.4"]
    for name, days in (("bez 2.06.2022", [pd.Timestamp(SPIKE_DAY)]), ("bez dni wydarzeń ±1", event_days(1))):
        v[name] = tuple(smooth_days(s, days) for s in base)
    return v


def run_tests(d: pd.DataFrame, n_perm: int = 1000, seed: int = 0) -> dict:
    res = {}
    for name, (ru, ua, y) in variants(d).items():
        r = leadlag.test_hypothesis(ru, ua, y, n_perm=n_perm, seed=seed)
        res[name] = {"supported": r["supported"], "criteria": r["criteria"],
                     "r_ru": r["main_ru"]["r_best"], "lag_ru": r["main_ru"]["best_lag"], "p_ru": r["main_ru"]["p_perm_max_abs_r"],
                     "r_ua": r["main_ua"]["r_best"], "p_ua": r["main_ua"]["p_perm_max_abs_r"],
                     "weekly_rho": r["weekly_ru"]["rho_changes"], "weekly_p": r["weekly_ru"]["p_perm_one_sided"],
                     "ru_minus_ua": r["ru_minus_ua"]["diff"], "ru_minus_ua_ci": r["ru_minus_ua"]["ci95"]}
    return res


def density(d: pd.DataFrame) -> dict:
    from pipeline.telegram_refugee import density_verdict
    out = {}
    for col in ("x_about", "x_about_strict", "tg_ru_about", "tg_ru_about_strict", "tg_ua_about", "tg_ua_about_strict"):
        if col not in d:
            continue
        s = d[col]
        w = s.resample("W-SUN").sum()
        st = {"median_day": float(s.median()), "zero_days": float((s == 0).mean()), "mean_week": float(w.mean())}
        out[col] = {**st, "n": int(s.sum()), "peak_day": str(s.idxmax().date()), "peak_n": int(s.max()),
                    "verdict": density_verdict(st)}
    return out


def results_md(res: dict, dens: dict) -> str:
    f = lambda x: "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"
    L = ["# Wariant: wolumen tematu „o uchodźcach” (bramka v0.4), X vs Telegram", "",
         "Mierzy wspólną uwagę do tematu, NIE negatywne treści ani narrację. Reguła: (a) p<0,05 dla RU, (b) test tygodniowy ten sam znak, "
         "(c) RU>UA (przedział różnicy bez 0). Kopie i dni wydarzeń sprawdzane w wariantach.", "",
         "## Gęstość szeregów", "", "| szereg | n | mediana/dzień | dni z zerem | peak | werdykt |", "|---|---|---|---|---|---|"]
    for k, s in dens.items():
        L.append(f"| {k} | {s['n']} | {s['median_day']:.0f} | {100 * s['zero_days']:.0f}% | {s['peak_day']} ({s['peak_n']}) | {s['verdict']} |")
    L += ["", "## Test hipotezy", "", "| wariant | r RU (k) | p RU | r UA | p UA | tyg. ρ | RU−UA [95%] | a | b | c | H |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in res.items():
        c = r["criteria"]
        ci = r["ru_minus_ua_ci"]
        L.append(f"| {k} | {f(r['r_ru'])} ({r['lag_ru']}) | {f(r['p_ru'])} | {f(r['r_ua'])} | {f(r['p_ua'])} | {f(r['weekly_rho'])} | "
                 f"{f(r['ru_minus_ua'])} [{f(ci[0])}; {f(ci[1])}] | {'+' if c['a_main_p_lt_005'] else '–'} | "
                 f"{'+' if c['b_weekly_same_sign'] else '–'} | {'+' if c['c_ru_gt_ua'] else '–'} | {'TAK' if r['supported'] else 'nie'} |")
    L += ["", "Interpretacja: korelacja nie dowodzi wpływu; wspólny bodziec (wydarzenia) jest głównym zagrożeniem, stąd wariant bez dni wydarzeń."]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- CLI
def cmd_build(a) -> None:
    from pipeline import load_twitter, telegram_refugee
    tw = load_twitter.normalize(load_twitter.load_raw(a.twitter))
    tg = telegram_refugee.load(a.posts, a.clusters)
    d = build(tw, tg)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(a.out)
    pk = Path(a.out).with_name("refugee_volume_peaks.csv")
    peak_dump(tw, tg, d).to_csv(pk, index=False, encoding="utf-8-sig")
    print(f"Zapisano {pk} (najczęstsze treści w szczytach, do przejrzenia ręcznego)")
    print(f"Zapisano {a.out}: {len(d)} dni, kolumny: {', '.join(d.columns)}")


def cmd_test(a) -> None:
    d = pd.read_csv(a.daily, index_col="day", parse_dates=True)
    res, dens = run_tests(d, n_perm=a.n_perm), density(d)
    out = Path(a.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(results_md(res, dens), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"density": dens, "tests": res}, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(results_md(res, dens))
    print(f"Zapisano {out}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="szeregi dzienne z pełnych danych (wolne, raz)")
    b.add_argument("--twitter", default=str(config.RAW_TWITTER))
    b.add_argument("--posts", default=str(config.ROOT / "data" / "telegram" / "posts_2022_part_*.csv"))
    b.add_argument("--clusters", default=str(config.ROOT / "data" / "telegram" / "leiden_clusters.csv"))
    b.add_argument("--out", default=str(OUT_DAILY))
    b.set_defaults(fn=cmd_build)
    t = sub.add_parser("test", help="test hipotezy + warianty z zapisanych szeregów (szybki)")
    t.add_argument("--daily", default=str(OUT_DAILY))
    t.add_argument("--report", default=str(config.REPORTS / "wolumen_uchodzcy_wyniki.md"))
    t.add_argument("--n-perm", type=int, default=1000)
    t.set_defaults(fn=cmd_test)
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):      # konsola Windows (cp1250) nie ma znaków typu ρ
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    a.fn(a)


if __name__ == "__main__":
    main()
