"""Eksploracja Telegrama (opisowa, BEZ testowania hipotezy) na przefiltrowanych plikach postów.

Wejście: pliki `data/telegram/posts_2022_part_*.csv` (id, peer_id, date, message, views, forwards; już przefiltrowane
na 2022 r. i temat „Ukraina + Polska”, zob. filtr_telegram.py) oraz `leiden_clusters.csv` (peer_id, side, cluster).
Dane mogą być NIEPEŁNE (tylko część z 8 plików): skrypt zawsze raportuje, które części i ile kanałów uwzględnił.

Co liczymy (wszystko opisowo; żadnych testów hipotezy):
- pokrycie: pliki, kanały, posty, zakres dat, udział kanałów bez etykiety strony,
- na stronę kanału (Pro-Russian / Pro-Ukrainian / unlabeled): posty, kanały, mediana postów dziennie,
  odsetek dni bez postu (czy szereg dzienny w ogóle da się zbudować), udział narracji anty-UA (szkic leksykonu RU/UK),
  mediany wyświetleń i przekazań, koncentracja na 10 największych kanałach, udział powtórzeń tego samego tekstu,
- trend udziału anty-UA w tygodniach (Spearman, opisowo), peaki w szeregu prorosyjskim,
- zestawienie wzrokowe z X (tydzień po tygodniu, bez korelacji i bez testu).

Użycie:
    python -m pipeline.eda_telegram [--posts 'data/telegram/posts_2022_part_*.csv'] [--clusters data/telegram/leiden_clusters.csv]
Wyniki (bez treści postów): reports/eda_telegram_section.tex (wstawiany do karty), reports/eda_telegram_results.md,
reports/eda_telegram_summary.json, reports/figures/telegram.pdf, data/processed/telegram_eda_daily.csv
"""
from __future__ import annotations

import argparse
import glob
import json
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from pipeline import config  # noqa: E402
from pipeline.eda_twitter import AQUA, BLUE, GRID, INK, MUTED, ORANGE, fmt_int, fmt_pct  # noqa: E402
from pipeline.series import detect_peaks  # noqa: E402

SIDES = ["Pro-Russian", "Pro-Ukrainian", "unlabeled"]   # w leiden_clusters.csv są tylko dwie strony
SIDE_PL = {"Pro-Russian": "prorosyjskie", "Pro-Ukrainian": "proukraińskie", "unlabeled": "bez etykiety"}


def load_posts(pattern: str) -> tuple[pd.DataFrame, list[int]]:
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"Brak plików pasujących do {pattern}. Najpierw uruchom filtr_telegram.py.")
    frames, parts = [], []
    for f in files:
        d = pd.read_csv(f, usecols=["id", "peer_id", "date", "message", "views", "forwards"], dtype={"message": "string"})
        m = re.search(r"part_(\d+)", f)
        d["part"] = int(m.group(1)) if m else 0
        parts.append(d["part"].iloc[0] if len(d) else 0)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True).drop_duplicates(["peer_id", "id"])
    return df, sorted(set(int(p) for p in parts))


def _norm_side(v) -> str:
    t = str(v).strip().lower()
    if "russ" in t or "ros" in t or t in ("ru", "pro-ru"):
        return "Pro-Russian"
    if "ukr" in t or t in ("ua", "pro-ua"):
        return "Pro-Ukrainian"
    return "unlabeled"


def _norm_id(x: pd.Series) -> pd.Series:
    """Ujednolica identyfikatory kanałów (Telegram bywa zapisywany jako -100XXXXXXXXXX)."""
    n = pd.to_numeric(x, errors="coerce")
    return n.where(n > -1_000_000_000_000, -n - 1_000_000_000_000).abs()


def attach_sides(df: pd.DataFrame, clusters_csv: str) -> tuple[pd.DataFrame, dict]:
    cl = pd.read_csv(clusters_csv)
    id_col = next((c for c in ("peer_id", "channel_id", "id", "channel") if c in cl.columns), cl.columns[0])
    side_col = next((c for c in ("side", "label", "stance", "camp") if c in cl.columns), None)
    if side_col is None:
        raise SystemExit(f"W {clusters_csv} nie znalazłem kolumny strony (side/label/stance). Kolumny: {list(cl.columns)}")
    cl = cl.assign(_id=_norm_id(cl[id_col]), _side=cl[side_col].map(_norm_side)).dropna(subset=["_id"]).drop_duplicates("_id")
    out = df.assign(_id=_norm_id(df["peer_id"])).merge(cl[["_id", "_side"]], on="_id", how="left")
    out["side"] = out["_side"].fillna("unlabeled")
    out = out.drop(columns=["_id", "_side"])
    diag = {"clusters_columns": list(cl.columns[:-2]), "clusters_side_values": cl[side_col].value_counts().head(8).to_dict(),
            "clusters_rows": int(len(cl)), "post_channels_in_clusters": float(out.loc[out["side"] != "unlabeled", "peer_id"].nunique() / max(out["peer_id"].nunique(), 1)),
            "id_column": id_col, "side_column": side_col}
    return out, diag


def prepare(df: pd.DataFrame, clusters_csv: str) -> pd.DataFrame:
    ts = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df = df.assign(ts=ts).dropna(subset=["ts"])
    df["day"] = df["ts"].dt.tz_convert("Europe/Warsaw").dt.tz_localize(None).dt.normalize()
    df = df[(df["day"] >= config.EFFECTIVE_START) & (df["day"] <= config.STUDY_END)].copy()
    msg = df["message"].fillna("")
    # kontrola spójności z filtrem pobierania: temat = Ukraina ORAZ Polska
    df = df[msg.str.contains(config.TELEGRAM_UA, regex=True) & msg.str.contains(config.TELEGRAM_PL, regex=True)].copy()
    msg = df["message"].fillna("")
    df["is_anti"] = msg.str.contains(config.TELEGRAM_ANTI_UA, regex=True)
    df["copy_key"] = msg.str.lower().str.replace(r"\s+", " ", regex=True).str.strip().str[:80]
    df, diag = attach_sides(df, clusters_csv)
    df.attrs["diag"] = diag
    for c in ("views", "forwards"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def daily_by_side(df: pd.DataFrame) -> pd.DataFrame:
    idx = pd.date_range(config.EFFECTIVE_START, config.STUDY_END, freq="D")
    out = {}
    for s in SIDES:
        d = df[df["side"] == s]
        out[(s, "n")] = d.groupby("day").size().reindex(idx).fillna(0).astype(int)
        out[(s, "anti")] = d[d["is_anti"]].groupby("day").size().reindex(idx).fillna(0).astype(int)
    res = pd.DataFrame(out)
    res.index.name = "day"
    return res


def weekly_trend(d: pd.DataFrame, min_n: int = 10) -> dict:
    if d.empty:
        return {"n_weeks": 0, "rho": None, "p": None}
    w = d.assign(week=d["day"].dt.to_period("W-SUN").dt.start_time).groupby("week").agg(n=("is_anti", "size"), a=("is_anti", "sum"))
    w = w[w["n"] >= min_n]
    if len(w) < 8:
        return {"n_weeks": int(len(w)), "rho": None, "p": None}
    rho, p = stats.spearmanr(np.arange(len(w)), w["a"] / w["n"])
    return {"n_weeks": int(len(w)), "rho": float(rho), "p": float(p)}


def side_stats(df: pd.DataFrame, daily: pd.DataFrame) -> dict:
    out = {}
    for s in SIDES:
        d = df[df["side"] == s]
        n_days = len(daily)
        series = daily[(s, "n")]
        top10 = d["peer_id"].value_counts().head(10).sum() / len(d) if len(d) else np.nan
        out[s] = {
            "posts": int(len(d)), "channels": int(d["peer_id"].nunique()),
            "median_daily": float(series.median()), "mean_daily": float(series.mean()),
            "zero_days_share": float((series == 0).sum() / n_days),
            "anti_posts": int(d["is_anti"].sum()), "anti_share": float(d["is_anti"].mean()) if len(d) else None,
            "median_views": float(d["views"].median()) if len(d) else None,
            "median_forwards": float(d["forwards"].median()) if len(d) else None,
            "top10_channel_share": float(top10) if len(d) else None,
            "copy_share": float(d.duplicated("copy_key", keep="first").mean()) if len(d) else None,
            "trend_anti_weekly": weekly_trend(d),
        }
    return out


def peaks_ru(df: pd.DataFrame, daily: pd.DataFrame, z: float = 2.5) -> pd.DataFrame:
    x = daily[("Pro-Russian", "n")]
    if (x > 0).sum() < 30:
        return pd.DataFrame()
    pk = detect_peaks(x, z=z)
    ev = {pd.Timestamp(k): v for k, v in config.EVENTS.items()}
    rows = []
    for d in pk:
        day = df[(df["day"] == d) & (df["side"] == "Pro-Russian")]
        ch = day["peer_id"].value_counts()
        near = [f"{v} ({(d - k).days:+d} d)" for k, v in ev.items() if abs((d - k).days) <= 3]
        rows.append({"day": d.date(), "n": int(x.loc[d]), "top_channel_share": float(ch.iloc[0] / len(day)) if len(day) else np.nan,
                     "anti_share": float(day["is_anti"].mean()) if len(day) else np.nan, "event": "; ".join(near)})
    return pd.DataFrame(rows)


def plot(daily: pd.DataFrame, df: pd.DataFrame, x_daily: pd.DataFrame | None, peaks: pd.DataFrame, out) -> None:
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 4.4), sharex=True, constrained_layout=True)
    cols = {"Pro-Russian": ORANGE, "Pro-Ukrainian": BLUE}
    raw = daily[("Pro-Russian", "n")]
    ax[0].plot(raw.index, raw, color=ORANGE, lw=0.5, alpha=0.35)
    for s, c in cols.items():
        x = daily[(s, "n")]
        ax[0].plot(x.index, x.rolling(7, min_periods=1).mean(), color=c, lw=1.2, label=f"{SIDE_PL[s]} (śr. 7 dni)")
    if len(peaks):
        pd_ = pd.to_datetime(peaks["day"])
        ax[0].scatter(pd_, raw.loc[pd_].values, s=14, color=ORANGE, edgecolor=INK, zorder=3, label="peak: surowa liczba z dnia")
        for d in pd_:
            ax[0].annotate(d.strftime("%d.%m"), (d, raw.loc[d]), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=6, color=INK)
    ymax = float(raw.max()) if len(raw) else 1.0
    for k, v in config.EVENTS.items():
        t = pd.Timestamp(k)
        if daily.index[0] <= t <= daily.index[-1]:
            ax[0].axvline(t, color=MUTED, lw=0.7, ls=":")
            ax[0].text(t, 0.97, v + " ", rotation=90, va="top", ha="right", fontsize=6, color=MUTED, transform=ax[0].get_xaxis_transform())
    ax[0].set_ylabel("posty o UA+PL / dzień")
    ax[0].set_ylim(0, ymax * 1.15)
    ax[0].legend(frameon=False, fontsize=6, ncol=3, loc="lower left", bbox_to_anchor=(0.03, 1.0))
    ax[0].text(-0.005, 1.02, "A", transform=ax[0].transAxes, fontweight="bold", color=INK)
    for s, c in {"Pro-Russian": ORANGE, "Pro-Ukrainian": BLUE}.items():
        d = df[df["side"] == s]
        if d.empty:
            continue
        w = d.assign(week=d["day"].dt.to_period("W-SUN").dt.start_time).groupby("week").agg(n=("is_anti", "size"), a=("is_anti", "sum"))
        w = w[w["n"] >= 10]
        ax[1].plot(w.index, 100 * w["a"] / w["n"], color=c, lw=1.2, marker="o", ms=2.5, label=SIDE_PL[s])
    ax[1].set_ylabel("% postów z narracją\nanty-UA (tydzień, n≥10)")
    ax[1].legend(frameon=False, fontsize=7, loc="upper left")
    ax[1].text(0.0, 1.02, "B", transform=ax[1].transAxes, fontweight="bold", color=INK)
    wr = daily[("Pro-Russian", "n")].resample("W-SUN").sum()
    ax[2].plot(wr.index, wr / max(wr.max(), 1), color=ORANGE, lw=1.2, label="Telegram prorosyjski: posty (UA+PL)")
    if x_daily is not None:
        wx = x_daily["anti_contents"].loc[config.EFFECTIVE_START:].resample("W-SUN").sum()
        ax[2].plot(wx.index, wx / max(wx.max(), 1), color=BLUE, lw=1.2, label="X: różne treści z narracją anty-UA")
    ax[2].set_ylabel("tygodniowo, skala\ndo maksimum")
    ax[2].legend(frameon=False, fontsize=7, loc="upper left")
    ax[2].text(0.0, 1.02, "C", transform=ax[2].transAxes, fontweight="bold", color=INK)
    ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%m.%y"))
    for a in ax:
        a.grid(color=GRID, lw=0.5)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.savefig(out)
    plt.close(fig)


def _tex_table(ss: dict) -> str:
    rows = []
    for s in SIDES:
        v = ss[s]
        if v["posts"] == 0:
            rows.append(f"{SIDE_PL[s]} & 0 & 0 & -- & -- & -- & -- \\\\")
            continue
        rows.append(f"{SIDE_PL[s]} & {fmt_int(v['channels'])} & {fmt_int(v['posts'])} & {v['median_daily']:.0f} & "
                    f"{fmt_pct(v['zero_days_share'], 0)} & {fmt_pct(v['anti_share'])} & {fmt_pct(v['top10_channel_share'], 0)} \\\\")
    return ("\\begin{tabular}{@{}lrrrrrr@{}}\\toprule\n"
            "Strona kanału & kanały & posty & mediana/dzień & dni bez postu & anty-UA & top-10 kanałów \\\\\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")


def section_tex(s: dict) -> str:
    cov, ss = s["coverage"], s["sides"]
    ru, ua = ss["Pro-Russian"], ss["Pro-Ukrainian"]
    parts = ", ".join(str(p) for p in cov["parts"])
    if ru["posts"] == 0:
        verdict = "W próbie nie ma postów z kanałów prorosyjskich, więc szeregu $X^{RU}_t$ nie da się zbudować."
    elif ru["zero_days_share"] > 0.5:
        verdict = (f"Szereg prorosyjski jest rzadki ({fmt_pct(ru['zero_days_share'], 0)} dni bez postu), więc analizę prowadzimy "
                   "na agregacji tygodniowej, a szereg dzienny traktujemy jako pomocniczy.")
    else:
        verdict = (f"Szereg prorosyjski ma medianę {ru['median_daily']:.0f} postów dziennie i {fmt_pct(ru['zero_days_share'], 0)} dni bez postu, "
                   "więc szereg dzienny da się zbudować.")
    tr = ru["trend_anti_weekly"]
    pl = sorted(s.get("peaks_ru", []), key=lambda r: -r["n"])[:6]
    peaks_txt = "" if not pl else " (" + "; ".join(
        f"{r['day'][8:10]}.{r['day'][5:7]}: {fmt_int(r['n'])} postów" + (f", {r['event'].split(' (')[0]}" if r["event"] else "") for r in pl) + ")"
    trend = ("" if tr["rho"] is None else
             f" Trend udziału anty-UA w kanałach prorosyjskich (Spearman, {tr['n_weeks']} tyg. z $n\\ge10$): "
             f"$\\rho={str(round(tr['rho'], 2)).replace('.', '{,}')}$ "
             f"($p={str(round(tr['p'], 3)).replace('.', '{,}')}$), w X: $\\rho=\\EdaTrAntiRho$ (\\EdaTrAntiP); "
             "zgodnego trendu rocznego więc nie widać, co nie przesądza o korelacji \\emph{zmian} dzień do dnia (sekcja~6).")
    return (
        "\\section{Wstępna eksploracja Telegrama (dane niepełne, opisowo)}\n"
        f"\\textbf{{Pokrycie.}} Uwzględniono pliki postów nr {parts} z 8 (kolejne pliki zmienią liczby, nie metodę; to \\emph{{nie}} jest próba losowa kanałów). Po filtrze (Ukraina i Polska, 4.03--31.12.2022): {fmt_int(cov['n_posts'])} postów z {fmt_int(cov['n_channels'])} kanałów; "
        f"{fmt_pct(cov['unlabeled_share'], 0)} postów pochodzi z kanałów bez etykiety strony. "
        "\\textbf{Uwaga o temacie:} filtr „Ukraina i Polska” łapie głównie wojnę i geopolitykę (np. Przewodów), a nie uchodźców; filtr uchodźczy (rosyjskie i ukraińskie odpowiedniki słów „uchodźca” i „Ukraińcy w Polsce”) dodajemy w następnym etapie. "
        "\n\n"
        "\\begin{center}\\footnotesize\\setlength{\\tabcolsep}{3pt}\n" + _tex_table(ss) + "\n\\end{center}\n"
        "{\\footnotesize\\textbf{Tab. 3.} Posty o Ukrainie i Polsce według strony kanału; „anty-UA” = udział postów trafionych szkicem "
        "leksykonu RU/UK (v0.1, niezwalidowany); „top-10 kanałów” = udział 10 najaktywniejszych kanałów w postach strony.}\\\\[2pt]\n"
        f"{verdict}{trend} Powtórzony tekst (te same 80 znaków w innym poście) dotyczy {fmt_pct(ru['copy_share'] or 0, 0)} postów prorosyjskich; "
        f"peaków w szeregu prorosyjskim: {s['n_peaks_ru']}{peaks_txt}.\n\n"
        "{\\centering\\includegraphics[width=0.8\\linewidth]{figures/telegram.pdf}\\par}\n"
        "{\\footnotesize\\textbf{Rys. 2.} A: dzienna liczba postów według strony (linie: średnia 7 dni; cienka linia i kropki: surowa liczba w kanałach prorosyjskich; kropkowane: wydarzenia z listy); B: tygodniowy udział narracji anty-UA; "
        "C: zestawienie wzrokowe tygodniowych liczb z Telegramu prorosyjskiego i z X, każda skalowana do swojego maksimum "
        "(bez korelacji i bez testu; hipotezy w M1 nie testujemy).\\par}\n"
    )


def results_md(s: dict, peaks: pd.DataFrame) -> str:
    cov, ss = s["coverage"], s["sides"]
    L = ["# Eksploracja Telegrama (opisowa; dane mogą być niepełne)", "",
         f"- Pliki postów uwzględnione: {cov['parts']} (z 8)",
         f"- Posty po filtrze (UA+PL, {config.EFFECTIVE_START}..{config.STUDY_END}): {cov['n_posts']}, kanały: {cov['n_channels']}",
         f"- Zakres dat: {cov['first_day']} .. {cov['last_day']}; udział postów z kanałów bez etykiety: {cov['unlabeled_share']:.1%}",
         f"- Unikalne teksty (80 znaków): {cov['unique_texts']}", "", "| strona | kanały | posty | mediana/dzień | dni bez postu | anty-UA | wyśw. (mediana) | przek. (mediana) | top-10 kanałów | powtórzenia |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k in SIDES:
        v = ss[k]
        if v["posts"] == 0:
            L.append(f"| {k} | 0 | 0 | | | | | | | |")
            continue
        L.append(f"| {k} | {v['channels']} | {v['posts']} | {v['median_daily']:.0f} | {v['zero_days_share']:.0%} | {v['anti_share']:.1%} | "
                 f"{v['median_views']:.0f} | {v['median_forwards']:.0f} | {v['top10_channel_share']:.0%} | {v['copy_share']:.0%} |")
    L += ["", "## Trend udziału anty-UA (Spearman, tygodnie z n>=10, opisowo)"]
    for k in SIDES:
        t = ss[k]["trend_anti_weekly"]
        L.append(f"- {k}: " + ("za mało tygodni" if t["rho"] is None else f"rho={t['rho']:.2f}, p={t['p']:.3f}, tygodni={t['n_weeks']}"))
    L += ["", "## Peaki w szeregu prorosyjskim (z>2.5)", ""]
    L.append("brak (za mało dni z postami)" if peaks.empty else "```\n" + peaks.to_string(index=False) + "\n```")
    return "\n".join(L) + "\n"


def run(posts: str, clusters: str, twitter_daily: str, z: float) -> dict:
    raw, parts = load_posts(posts)
    df = prepare(raw, clusters)
    for p in (config.REPORTS, config.FIGURES, config.PROCESSED):
        p.mkdir(parents=True, exist_ok=True)
    daily = daily_by_side(df)
    daily.columns = [f"{a}__{b}" for a, b in daily.columns]
    daily.to_csv(config.PROCESSED / "telegram_eda_daily.csv")
    daily.columns = pd.MultiIndex.from_tuples([tuple(c.split("__")) for c in daily.columns])
    ss = side_stats(df, daily)
    pk = peaks_ru(df, daily, z=z)
    x_daily = None
    try:
        x_daily = pd.read_csv(twitter_daily, index_col=0, parse_dates=True)
    except FileNotFoundError:
        pass
    diag = df.attrs.get("diag", {})
    summary = {
        "diagnostics": diag,
        "coverage": {"parts": parts, "n_posts": int(len(df)), "n_channels": int(df["peer_id"].nunique()),
                     "first_day": str(df["day"].min().date()) if len(df) else None, "last_day": str(df["day"].max().date()) if len(df) else None,
                     "unlabeled_share": float((df["side"] == "unlabeled").mean()) if len(df) else 0.0,
                     "unique_texts": int(df["copy_key"].nunique())},
        "sides": ss, "n_peaks_ru": int(len(pk)),
        "peaks_ru": [] if pk.empty else pk.assign(day=pk["day"].astype(str)).to_dict(orient="records"), "params": {"z": z, "anti_lexicon": "TELEGRAM_ANTI_UA v0.1"},
        "twitter_comparison_included": x_daily is not None,
    }
    plot(daily, df, x_daily, pk, config.FIGURES / "telegram.pdf")
    (config.REPORTS / "eda_telegram_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (config.REPORTS / "eda_telegram_section.tex").write_text(
        "% Wygenerowane przez python -m pipeline.eda_telegram. Nie edytować ręcznie.\n" + section_tex(summary), encoding="utf-8")
    (config.REPORTS / "eda_telegram_results.md").write_text(results_md(summary, pk), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Opisowa eksploracja Telegrama (bez testu hipotezy)")
    ap.add_argument("--posts", default=str(config.ROOT / "data" / "telegram" / "posts_2022_part_*.csv"))
    ap.add_argument("--clusters", default=str(config.ROOT / "data" / "telegram" / "leiden_clusters.csv"))
    ap.add_argument("--twitter-daily", default=str(config.PROCESSED / "twitter_daily.csv"))
    ap.add_argument("--z", type=float, default=2.5)
    a = ap.parse_args()
    s = run(a.posts, a.clusters, a.twitter_daily, a.z)
    d = s["diagnostics"]
    print("Etykiety stron: kolumna", d.get("side_column"), "wartości", d.get("clusters_side_values"), "| kanały z postów znalezione w pliku etykiet:",
          f"{d.get('post_channels_in_clusters', 0):.0%}")
    if d.get("post_channels_in_clusters", 0) < 0.05:
        print("UWAGA: prawie żaden kanał z postów nie ma etykiety strony; sprawdź format peer_id w pliku etykiet (wklej mi head).")
    print(json.dumps({"coverage": s["coverage"], "posts_by_side": {k: v["posts"] for k, v in s["sides"].items()},
                      "n_peaks_ru": s["n_peaks_ru"]}, ensure_ascii=False, indent=2))
    print("Zapisano reports/eda_telegram_section.tex, eda_telegram_results.md, figures/telegram.pdf")


if __name__ == "__main__":
    main()
