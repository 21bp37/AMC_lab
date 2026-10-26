"""Weryfikacja etykiet pro / anty: zgodność koderów, etykieta referencyjna i jakość słownika (oraz ewent. modelu językowego).

Wejście: proba_master.csv (z annotation_sample.py) i arkusze koderów (xlsx lub csv) z wypełnioną kolumną „etykieta”.
Etykiety: anty, pro, neutralne, nie_dotyczy, niejasne.

Co liczy:
 1. Zgodność koderów (każda para): % zgodności, kappa Cohena na 5 etykietach i na 3 (anty / pro / inne) z 95% CI
    (bootstrap po treściach) oraz alfa Krippendorffa dla wszystkich koderów. Osobno dla X i Telegrama.
 2. Etykieta referencyjna: większość głosów (przy 2 koderach: obaj się zgadzają). Spory trafiają do
    do_rozstrzygniecia.csv; po uzupełnieniu kolumny etykieta_final uruchom skrypt ponownie z --resolved.
 3. Jakość słownika względem etykiety referencyjnej, osobno X i Telegram (oraz strona kanału):
    precyzja, czułość, F1 dla klasy „anty” (X także „pro”) z wagami 1 / prawdopodobieństwo włączenia
    i przedziałem bootstrapowym w obrębie warstw; prevalence populacyjna (ile jest naprawdę vs ile łapie słownik).
 4. Reguła decyzyjna z karty M1: κ < próg → poprawiamy instrukcję i kodujemy nową próbę; precyzja < próg →
    Telegram: nie interpretujemy narracji (tylko wolumen tematu); X: przegląd błędów i nowa wersja słownika.
 5. Pliki: bledy_leksykonu.csv (fałszywe trafienia i braki z trafionymi słowami), etykiety_referencyjne.csv.

Model językowy jako trzeci koder albo jako oceniany klasyfikator:
  --classifier C   koder C NIE wchodzi do etykiety referencyjnej, tylko jest oceniany jak słownik (precyzja / czułość).
  (bez tej opcji wszyscy koderzy tworzą wzorzec, a oceniany jest tylko słownik)

Użycie:
  python -m pipeline.annotation_check --annotations annotation_work/anotacja_A.xlsx annotation_work/anotacja_B.xlsx
  python -m pipeline.annotation_check --annotations A.xlsx B.xlsx C.xlsx --classifier C
  python -m pipeline.annotation_check --annotations A.xlsx B.xlsx --resolved annotation_work/do_rozstrzygniecia.csv
"""
from __future__ import annotations

import argparse
import itertools
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import config
from pipeline.annotation_sample import ANNOT_DIR, LABELS

sys.path.insert(0, str(config.ROOT / "tools"))
import agreement as ag  # noqa: E402
import evaluation as ev  # noqa: E402

ALIASES = {
    "anty_ua": "anty", "anti": "anty", "antyukrainskie": "anty", "anty-ua": "anty", "negatywne": "anty",
    "pro_ua": "pro", "pro-ua": "pro", "proukrainskie": "pro", "pozytywne": "pro",
    "neutralna": "neutralne", "neutralny": "neutralne", "neutral": "neutralne",
    "nie_dotyczy": "nie_dotyczy", "niedotyczy": "nie_dotyczy", "nd": "nie_dotyczy", "n/d": "nie_dotyczy",
    "niejasna": "niejasne", "niejasny": "niejasne", "nie_wiem": "niejasne",
}


def norm_label(v) -> str | None:
    if v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == "":
        return None
    t = re.sub(r"[\s\-]+", "_", str(v).strip().lower())
    t = ALIASES.get(t, t)
    return t


def collapse3(l):
    return None if l is None else (l if l in ("anty", "pro") else "inne")


# --------------------------------------------------------------------------- wczytanie
def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        with pd.ExcelFile(path) as xl:                      # zamykamy plik (Windows blokuje otwarty xlsx)
            return xl.parse("Anotacja" if "Anotacja" in xl.sheet_names else xl.sheet_names[0], dtype=str)
    return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig", dtype=str)


def load_coder(path: Path, name: str) -> pd.DataFrame:
    d = read_table(path)
    d.columns = [str(c).strip().lower() for c in d.columns]
    for need in ("id", "etykieta"):
        if need not in d.columns:
            raise SystemExit(f"{path.name}: brak kolumny „{need}” (są: {list(d.columns)})")
    d = d.dropna(subset=["id"]).copy()
    d["id"] = d["id"].str.strip()
    if d["id"].duplicated().any():
        raise SystemExit(f"{path.name}: powtórzone id: {d.loc[d['id'].duplicated(), 'id'].tolist()[:5]}")
    d["label"] = d["etykieta"].map(norm_label)
    bad = d[d["label"].notna() & ~d["label"].isin(LABELS)]
    if len(bad):
        raise SystemExit(f"{path.name}: nieznane etykiety {sorted(bad['label'].unique())} w wierszach {bad['id'].tolist()[:8]}. "
                         f"Dozwolone: {LABELS}")
    out = pd.DataFrame({"label": d["label"].to_numpy()}, index=d["id"].to_numpy())
    out["tlumaczenie"] = d["tlumaczenie"].to_numpy() if "tlumaczenie" in d.columns else None
    out["komentarz"] = d["komentarz"].fillna("").to_numpy() if "komentarz" in d.columns else ""
    out.columns = [f"{name}__{c}" for c in out.columns]
    return out


# --------------------------------------------------------------------------- zgodność
def kappa_ci(a, b, boot: int, seed: int = 0):
    a = np.array(a, dtype=object); b = np.array(b, dtype=object)
    k = ag.cohen_kappa(a, b)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(boot):
        i = rng.integers(0, len(a), len(a))
        v = ag.cohen_kappa(a[i], b[i])
        if not math.isnan(v):
            vals.append(v)
    lo, hi = np.quantile(vals, [0.025, 0.975]) if len(vals) > 20 else (float("nan"), float("nan"))
    return k, float(lo), float(hi)


def agreement_table(L: pd.DataFrame, coders: list[str], platform_of: pd.Series, boot: int) -> tuple[pd.DataFrame, dict]:
    rows, min_k3 = [], {}
    for plat in ["Wszystko", "X", "Telegram"]:
        sel = L.index if plat == "Wszystko" else L.index[platform_of.reindex(L.index) == plat]
        if len(sel) == 0:
            continue
        for a, b in itertools.combinations(coders, 2):
            m = L.loc[sel, [a, b]].dropna()
            if len(m) < 5:
                continue
            k5 = kappa_ci(m[a], m[b], boot)
            k3 = kappa_ci(m[a].map(collapse3), m[b].map(collapse3), boot)
            rows.append({"zbior": plat, "para": f"{a}-{b}", "n": len(m), "zgodnosc": float((m[a] == m[b]).mean()),
                         "kappa5": k5, "kappa3": k3})
            if plat != "Wszystko" and not math.isnan(k3[0]):
                min_k3[plat] = min(min_k3.get(plat, 9.0), k3[0])
        units = [[(None if pd.isna(v) else v) for v in L.loc[i, coders]] for i in sel]
        alpha = ag.krippendorff_alpha(units)
        lo, hi = ag.bootstrap_alpha_ci(units, boot=min(boot, 500))
        rows.append({"zbior": plat, "para": "alfa (wszyscy)", "n": len(units), "zgodnosc": float("nan"),
                     "kappa5": (alpha, lo, hi), "kappa3": None})
    return pd.DataFrame(rows), min_k3


# --------------------------------------------------------------------------- wzorzec
def majority(labels: list):
    vals = [v for v in labels if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if len(vals) < 2:
        return None
    lab, cnt = Counter(vals).most_common(1)[0]
    return lab if cnt > len(vals) / 2 else None


def apply_resolved(ref: pd.Series, path: Path | None) -> pd.Series:
    if path is None:
        return ref
    r = read_table(path)
    r.columns = [str(c).strip().lower() for c in r.columns]
    idc = "item_id" if "item_id" in r.columns else "id"
    if idc not in r.columns or "etykieta_final" not in r.columns:
        raise SystemExit(f"{path.name}: potrzebne kolumny item_id (lub id) i etykieta_final")
    r["lab"] = r["etykieta_final"].map(norm_label)
    bad = r[r["lab"].notna() & ~r["lab"].isin(LABELS)]
    if len(bad):
        raise SystemExit(f"{path.name}: nieznane etykiety {sorted(bad['lab'].unique())}")
    ref = ref.copy()
    for i, lab in zip(r[idc], r["lab"]):
        if lab is not None and i in ref.index:
            ref.loc[i] = lab
    return ref


# --------------------------------------------------------------------------- jakość klasyfikatora
def strat_boot(d: pd.DataFrame, true_col: str, pred_col: str, boot: int, seed: int = 0) -> dict:
    """Precyzja / czułość / F1 / prevalence z wagami; CI z bootstrapu w obrębie warstw (próba jest warstwowa)."""
    point = ev.prf(d[true_col], d[pred_col], True, d["weight"])
    rng = np.random.default_rng(seed)
    groups = [g.index.to_numpy() for _, g in d.groupby("stratum")]
    draws = {m: [] for m in ("precision", "recall", "f1", "prevalence")}
    for _ in range(boot):
        idx = np.concatenate([rng.choice(g, len(g), replace=True) for g in groups])
        s = d.loc[idx]
        r = ev.prf(s[true_col], s[pred_col], True, s["weight"])
        for m in draws:
            if not math.isnan(r[m]):
                draws[m].append(r[m])
    out = {"support": point["support"], "flagged": int(d[pred_col].sum()), "n": len(d)}
    for m in draws:
        lo, hi = np.quantile(draws[m], [0.025, 0.975]) if len(draws[m]) > 20 else (float("nan"),) * 2
        out[m] = (point[m], float(lo), float(hi))
    return out


def f(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def fci(t, nd=2):
    return f"{f(t[0], nd)} [{f(t[1], nd)}; {f(t[2], nd)}]"


def md_table(df: pd.DataFrame) -> list[str]:
    cols = list(df.columns)
    return ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)] + \
           ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]


def top_words(rows: pd.DataFrame, prefix: str | None) -> Counter:
    c = Counter()
    for h in rows["lex_hits"].fillna(""):
        seen = set()
        for tok in h.split("; "):
            if not tok:
                continue
            name, _, word = tok.partition(":")
            if (prefix is None and not name.startswith("pro_")) or (prefix and name.startswith(prefix)):
                seen.add(word.lower())
        c.update(seen)
    return c


def filter_eval(D: pd.DataFrame, boot: int, seed: int = 0) -> list[dict]:
    """Precyzja i czułość filtra uchodźczego z etykiet referencyjnych (on_topic = anty / pro / neutralne)."""
    if "refugee_filter" not in D.columns:
        return []
    t = D[(D["platform"] == "Telegram") & D["refugee_filter"].isin(["tak", "nie"])].copy()
    if len(t) < 10 or t["refugee_filter"].nunique() < 2:
        return []
    t["passed"] = t["refugee_filter"].eq("tak")
    t["on"] = t["ref"].isin(["anty", "pro", "neutralne"])
    t["unclear"] = t["ref"].eq("niejasne")

    def est(x):
        w = x["weight"]
        tp = float((w * (x["passed"] & x["on"])).sum()); pas = float((w * x["passed"]).sum()); rej = float((w * ~x["passed"]).sum())
        fn = float((w * (~x["passed"] & (x["on"] | x["unclear"]))).sum())
        return (tp / pas if pas else float("nan"), fn / rej if rej else float("nan"), tp / (tp + fn) if (tp + fn) else float("nan"))

    out = []
    rng = np.random.default_rng(seed)
    for name, d in [("razem", t)] + [(s, t[t["side"] == s]) for s in ("Pro-Russian", "Pro-Ukrainian")]:
        d = d.reset_index(drop=True)
        if d["passed"].sum() < 3 or (~d["passed"]).sum() < 3:
            continue
        groups = [g.index.to_numpy() for _, g in d.groupby("stratum")]
        point = est(d)
        draws = [[], [], []]
        for _ in range(boot):
            idx = np.concatenate([rng.choice(g, len(g), replace=True) for g in groups])
            for lst, v in zip(draws, est(d.loc[idx])):
                if not math.isnan(v):
                    lst.append(v)
        ci = [tuple(np.quantile(x, [0.025, 0.975])) if len(x) > 20 else (float("nan"),) * 2 for x in draws]
        out.append({"name": name, "n_pass": int(d["passed"].sum()), "n_rej": int((~d["passed"]).sum()),
                    "precision": (point[0], *ci[0]), "miss": (point[1], *ci[1]), "recall": (point[2], *ci[2])})
    return out


# --------------------------------------------------------------------------- główny przebieg
def run(master_csv: Path, ann_paths: list[Path], names: list[str] | None, classifiers: list[str], resolved: Path | None,
        out: Path, boot: int, kappa_min: float, prec_min: float, recall_min: float = 0.5, refilter=None) -> str:
    master = pd.read_csv(master_csv, encoding="utf-8-sig", dtype={"item_id": str}).set_index("item_id")
    refilter_note = ""
    if refilter is not None:
        new = refilter(master)                               # DataFrame indexed by item_id: refugee_filter (tak / nie), refugee_hits
        master.loc[new.index, "refugee_filter"] = new["refugee_filter"]
        master.loc[new.index, "refugee_hits"] = new["refugee_hits"]
        refilter_note = (f"Filtr uchodźczy PRZELICZONY aktualnymi regułami ({len(new)} postów Telegrama), na tych samych etykietach. "
                         "Wagi zostają z losowania (domena filtra jest podzbiorem warstw), ale to jest ocena na zbiorze, na którym poprawiano listę: zawyżona.")
    names = names or [re.sub(r"^anotacja_", "", p.stem) for p in ann_paths]
    if len(set(names)) != len(names):
        raise SystemExit(f"Powtórzone nazwy koderów: {names}")
    coded = [load_coder(p, n) for p, n in zip(ann_paths, names)]
    wide = pd.concat(coded, axis=1)
    unknown = [i for i in wide.index if i not in master.index]
    if unknown:
        raise SystemExit(f"Id spoza próby: {unknown[:5]} (zły plik master?)")
    L = wide[[f"{n}__label" for n in names]].copy()
    L.columns = names
    L = L.reindex(master.index)
    missing = L.isna().sum()
    classifiers = [c for c in classifiers if c in names]
    ref_coders = [n for n in names if n not in classifiers]
    if len(ref_coders) < 2:
        raise SystemExit("Do etykiety referencyjnej potrzeba co najmniej dwóch koderów (poza --classifier).")
    plat = master["platform"]

    lines = ["# Weryfikacja etykiet pro / anty", "",
             f"Treści w próbie: {len(master)} (X {int((plat == 'X').sum())}, Telegram {int((plat == 'Telegram').sum())}). "
             f"Koderzy wzorca: {', '.join(ref_coders)}" + (f"; oceniani jak klasyfikator: {', '.join(classifiers)}" if classifiers else "") + ".",
             "Braki etykiet: " + ", ".join(f"{n}: {int(missing[n])}" for n in names) + ".", ""]
    if refilter_note:
        lines += ["> " + refilter_note, ""]

    # 1. zgodność
    agr, min_k3 = agreement_table(L, ref_coders, plat, boot)
    lines += ["## 1. Zgodność koderów", "",
              "κ Cohena: 0 = zgodność losowa, 1 = pełna. κ5 = pięć etykiet, κ3 = anty / pro / inne. Przedziały: 95%, bootstrap po treściach. "
              "Próba jest celowo wzbogacona w rzadkie klasy, więc κ dotyczy tej próby, nie populacji.", ""]
    tab = pd.DataFrame({"zbiór": agr["zbior"], "para": agr["para"], "n": agr["n"],
                        "% zgodności": agr["zgodnosc"].map(lambda v: "–" if math.isnan(v) else f"{100 * v:.0f}%"),
                        "κ5 / alfa": agr["kappa5"].map(fci),
                        "κ3": agr["kappa3"].map(lambda t: "" if t is None else fci(t))})
    lines += md_table(tab) + [""]
    pooled = L[ref_coders]
    lab_counts = pd.DataFrame({n: pooled[n].value_counts() for n in ref_coders}).reindex(LABELS).fillna(0).astype(int)
    lines += ["Rozkład etykiet u koderów:", ""] + md_table(lab_counts.reset_index().rename(columns={"index": "etykieta"})) + [""]
    if "tlumaczenie" in wide.columns.str.split("__").str[1].tolist():
        tcols = [f"{n}__tlumaczenie" for n in ref_coders]
        weak = (wide[tcols].apply(lambda s: s.str.lower().eq("słabe")).any(axis=1)).sum()
        lines += [f"Tłumaczenia oznaczone jako „słabe” przez któregokolwiek kodera: {int(weak)}.", ""]

    # 2. wzorzec
    ref = L[ref_coders].apply(lambda r: majority(list(r)), axis=1)
    ref = apply_resolved(ref, resolved)
    disputed = master.index[ref.isna()]
    q = master.loc[disputed, ["platform", "text_pl", "text_original"]].copy()
    for n in names:
        q[f"etykieta_{n}"] = L.loc[disputed, n]
    q["komentarze"] = [" | ".join(f"{n}: {wide.at[i, f'{n}__komentarz']}" for n in names
                                  if i in wide.index and str(wide.at[i, f'{n}__komentarz']).strip()) for i in disputed]
    q["etykieta_final"] = ""
    out.mkdir(parents=True, exist_ok=True)
    target = out / "do_rozstrzygniecia.csv"
    if resolved is not None and Path(resolved).resolve() == target.resolve():
        target = out / "do_rozstrzygniecia_pozostale.csv"          # nie nadpisujemy pliku, z którego właśnie wczytaliśmy rozstrzygnięcia
    if len(q) or target.name == "do_rozstrzygniecia.csv":
        q.reset_index().to_csv(target, index=False, encoding="utf-8-sig")
    lines += ["## 2. Etykieta referencyjna", "",
              f"Ustalona dla {int(ref.notna().sum())} z {len(ref)} treści; do rozstrzygnięcia: {len(disputed)} "
              f"(plik do_rozstrzygniecia.csv: uzupełnij etykieta_final i uruchom ponownie z --resolved). "
              "Nierozstrzygnięte treści są pomijane w ocenie słownika.", ""]
    dist = master.assign(ref=ref).dropna(subset=["ref"])
    ct = pd.crosstab([dist["platform"], dist["stratum"]], dist["ref"]).reindex(columns=LABELS, fill_value=0)
    ct.insert(0, "N w populacji", dist.groupby(["platform", "stratum"])["stratum_N"].first())
    ct["n"] = ct[LABELS].sum(axis=1)
    lines += ["Etykieta referencyjna w warstwach próby (liczby treści):", ""] + md_table(ct.reset_index()) + [""]
    pd.DataFrame({"item_id": ref.index, "etykieta_ref": ref.to_numpy()}).to_csv(out / "etykiety_referencyjne.csv", index=False)

    # 3. klasyfikatory
    D = master.assign(ref=ref).dropna(subset=["ref"]).copy()
    D["y_anty"] = D["ref"].eq("anty")
    D["y_pro"] = D["ref"].eq("pro")
    lex = D["lexicon_label"]
    D["lex_anty"] = np.where(D["platform"] == "X", lex.isin(["anti", "mieszane"]), lex.eq("anti"))
    D["lex_pro"] = np.where(D["platform"] == "X", lex.isin(["pro", "mieszane"]), False)
    for c in classifiers:
        D[f"{c}_anty"] = L.loc[D.index, c].eq("anty")
        D[f"{c}_pro"] = L.loc[D.index, c].eq("pro")

    lines += ["## 3. Jakość klasyfikatorów względem etykiety referencyjnej", "",
              "Wagi = 1 / prawdopodobieństwo włączenia, więc precyzja, czułość i prevalence dotyczą populacji treści, z której losowaliśmy "
              "(unikalne treści X w oknie; unikalne teksty Telegrama po filtrze Ukraina+Polska). CI: bootstrap w obrębie warstw. "
              "Czułość opiera się na rzadkich trafieniach w warstwie „brak / inne”, więc jej przedział jest zwykle szeroki.", ""]
    verdict, res_rows, fp_tables = [], [], {}
    specs = [("X", "anty", None, False), ("X", "pro", None, False), ("Telegram", "anty", None, False),
             ("Telegram", "anty", "Pro-Russian", False), ("Telegram", "anty", "Pro-Ukrainian", False),
             ("Telegram", "anty", None, True), ("Telegram", "anty", "Pro-Russian", True), ("Telegram", "anty", "Pro-Ukrainian", True)]
    for plat_name, cls, side, filt in specs:
        d = D[D["platform"] == plat_name]
        if filt:
            d = d[d["refugee_filter"].eq("tak")] if "refugee_filter" in d.columns else d.iloc[0:0]
        if side:
            d = d[d["side"] == side]
        if len(d) < 10:
            continue
        d = d.reset_index()
        for who, pred in [("słownik", f"lex_{cls}")] + [(c, f"{c}_{cls}") for c in classifiers]:
            if pred == "lex_pro" and plat_name == "Telegram":
                continue
            r = strat_boot(d, f"y_{cls}", pred, boot)
            res_rows.append({"zbiór": plat_name + (f" / {side}" if side else "") + (" / po filtrze uchodźczym" if filt else ""),
                             "klasa": cls, "klasyfikator": who,
                             "n": r["n"], "oznaczone": r["flagged"], "prawdziwe": r["support"],
                             "precyzja": fci(r["precision"]), "czułość": fci(r["recall"]), "F1": f(r["f1"][0]),
                             "prevalence (wzorzec)": f(r["prevalence"][0], 3)})
            if who == "słownik" and not side:
                verdict.append((plat_name + (" po filtrze uchodźczym" if filt else ""), cls, r))
    lines += md_table(pd.DataFrame(res_rows)) + [""]

    if "refugee_filter" in D.columns:
        fe_err = D[(D["platform"] == "Telegram") & ((D["refugee_filter"].eq("tak") & ~D["ref"].isin(["anty", "pro", "neutralne"])) |
                                                    (D["refugee_filter"].eq("nie") & D["ref"].isin(["anty", "pro", "neutralne", "niejasne"])))].copy()
        fe_err["typ"] = np.where(fe_err["refugee_filter"].eq("tak"), "FP", "FN")
        if len(fe_err):
            fe_err.reset_index()[["item_id", "typ", "side", "ref", "refugee_hits", "text_pl", "text_original"]].to_csv(
                out / "bledy_filtra.csv", index=False, encoding="utf-8-sig")
    # 3b. filtr uchodźczy oceniany tymi samymi etykietami (nie_dotyczy = poza tematem)
    fe = filter_eval(D, boot)
    if fe:
        lines += ["## 3b. Filtr uchodźczy RU/UK (Telegram), ocena z tych samych etykiet", "",
                  "Post „o uchodźcach” = etykieta referencyjna anty / pro / neutralne; „nie_dotyczy” = poza tematem; „niejasne” liczymy na niekorzyść filtra "
                  "(wśród przepuszczonych jak poza tematem, wśród odrzuconych jak możliwy brak). Wagi i bootstrap w warstwach jak wyżej.", ""]
        lines += md_table(pd.DataFrame([{"zbiór": x["name"], "oceniono (przep. / odrz.)": f"{x['n_pass']} / {x['n_rej']}",
                                         "precyzja": fci(x["precision"]), "pominięte wśród odrzuconych": fci(x["miss"]),
                                         "czułość": fci(x["recall"])} for x in fe])) + [""]
    else:
        lines += ["## 3b. Filtr uchodźczy", "", "(brak w próbie postów Telegrama z oboma wynikami filtra, pomijam)", ""]

    # macierze pomyłek
    for plat_name in ["X", "Telegram"]:
        d = D[D["platform"] == plat_name]
        if d.empty:
            continue
        d = d.assign(lex=np.where(d["lex_anty"] & d["lex_pro"], "słownik: oba", np.where(d["lex_anty"], "słownik: anty",
                     np.where(d["lex_pro"], "słownik: pro", "słownik: brak"))))
        m = pd.crosstab(d["lex"], d["ref"]).reindex(columns=LABELS, fill_value=0)
        lines += [f"Słownik a etykieta referencyjna, {plat_name} (liczby w próbie, bez wag):", ""] + md_table(m.reset_index()) + [""]

    # błędy
    err = []
    for cls in ("anty", "pro"):
        pred = D[f"lex_{cls}"]
        for typ, mask in ((f"FP_{cls}", pred & ~D[f"y_{cls}"]), (f"FN_{cls}", ~pred & D[f"y_{cls}"])):
            e = D[mask].copy()
            e["typ"] = typ
            err.append(e)
    E = pd.concat(err) if err else pd.DataFrame()
    if len(E):
        cols = ["typ", "platform", "stratum", "ref", "lex_hits", "text_pl", "text_original"]
        E.reset_index()[["item_id"] + cols].to_csv(out / "bledy_leksykonu.csv", index=False, encoding="utf-8-sig")
        lines += [f"Fałszywe trafienia i braki słownika: bledy_leksykonu.csv ({len(E)} wierszy). Słowa najczęściej stojące za fałszywymi trafieniami „anty”:", ""]
        rows = []
        for plat_name in ["X", "Telegram"]:
            dd = D[(D["platform"] == plat_name) & D["lex_anty"]]
            fp_w = top_words(dd[~dd["y_anty"]], None)
            tp_w = top_words(dd[dd["y_anty"]], None)
            for w, c in fp_w.most_common(8):
                rows.append({"zbiór": plat_name, "słowo": w, "fałszywe": c, "trafne": tp_w.get(w, 0)})
        lines += (md_table(pd.DataFrame(rows)) if rows else ["(brak)"]) + [""]

    # 4. werdykt
    lines += ["## 4. Wnioski według reguły z karty M1", "",
              f"Progi (do zmiany w wywołaniu): κ3 ≥ {kappa_min}, precyzja ≥ {prec_min}. Przy ~100 treściach przedziały są szerokie, więc "
              "traktuj to jako sygnał, nie dowód.", ""]
    for plat_name in ["X", "Telegram"]:
        k = min_k3.get(plat_name)
        if k is None:
            continue
        if k < kappa_min:
            lines.append(f"- **{plat_name}: κ3 = {f(k)} < {kappa_min}.** Kategorie nie są jednoznaczne dla koderów: popraw instrukcję "
                         "(przykłady przypadków granicznych), zakoduj nową próbę i dopiero wtedy oceniaj słownik.")
        else:
            lines.append(f"- {plat_name}: κ3 = {f(k)} ≥ {kappa_min}, zgodność koderów wystarczająca do porównań ze słownikiem.")
    for x in fe:
        if x["name"] != "razem":
            continue
        pr, rc = x["precision"][0], x["recall"][0]
        lines.append(f"- Filtr uchodźczy: precyzja {fci(x['precision'])}" + (f" < {prec_min}: zawęź rdzenie dające fałszywe trafienia (typ FP w bledy_filtra.csv)" if pr < prec_min else f" ≥ {prec_min}: OK")
                     + f"; czułość {fci(x['recall'])}" + (f" < {recall_min}: dopisz brakujące rdzenie (typ FN w bledy_filtra.csv)" if rc < recall_min else f" ≥ {recall_min}: OK") + ".")
    for plat_name, cls, r in verdict:
        if cls != "anty":
            continue
        p = r["precision"][0]
        if math.isnan(p):
            lines.append(f"- {plat_name}: brak oznaczonych przez słownik treści „anty” w etykiecie referencyjnej, precyzja nieokreślona.")
        elif p < prec_min:
            todo = ("**nie interpretujemy narracji z Telegramu**, testujemy tylko wolumen tematu" if "Telegram" in plat_name else
                    "przejrzyj bledy_leksykonu.csv, popraw słownik (v0.3 z wpisem w changelogu) i zwaliduj na NOWEJ próbie")
            lines.append(f"- **{plat_name}: precyzja „anty” = {fci(r['precision'])} < {prec_min}:** {todo}.")
        else:
            lines.append(f"- {plat_name}: precyzja „anty” = {fci(r['precision'])} ≥ {prec_min}; raportuj udziały razem z tą precyzją.")
    if classifiers:
        lines.append("- Porównanie słownika z modelem: patrz tabela w sekcji 3 (wiersze kolumny „klasyfikator”). Wyraźnie lepszy model "
                     "(wyższa precyzja i czułość, rozłączne przedziały) uzasadnia zamianę; podobne wyniki: zostaje słownik jako główny, model jako kontrola.")
    report = "\n".join(lines) + "\n"
    (out / "wyniki_anotacji.md").write_text(report, encoding="utf-8")
    return report


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--master", default=str(ANNOT_DIR / "proba_master.csv"))
    ap.add_argument("--annotations", nargs="+", required=True, help="arkusze koderów (xlsx / csv)")
    ap.add_argument("--names", nargs="+", help="nazwy koderów (domyślnie z nazwy pliku anotacja_<nazwa>)")
    ap.add_argument("--classifier", nargs="*", default=[], help="kodery oceniani jak klasyfikator (nie tworzą wzorca)")
    ap.add_argument("--resolved", help="CSV / XLSX z kolumnami item_id i etykieta_final (rozstrzygnięte spory)")
    ap.add_argument("--out", default=str(ANNOT_DIR))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--kappa-min", type=float, default=0.4)
    ap.add_argument("--precision-min", type=float, default=0.7)
    ap.add_argument("--recall-min", type=float, default=0.5, help="próg czułości filtra uchodźczego")
    ap.add_argument("--refilter", action="store_true",
                    help="przelicz filtr uchodźczy aktualnymi regułami na pełnych tekstach z danych (wolne, ok. minut) i oceń go na tych samych etykietach; "
                         "użyj z osobnym --out, żeby nie nadpisać pierwszego raportu")
    ap.add_argument("--posts", default=str(config.ROOT / "data" / "telegram" / "posts_2022_part_*.csv"))
    ap.add_argument("--clusters", default=str(config.ROOT / "data" / "telegram" / "leiden_clusters.csv"))
    args = ap.parse_args(argv)
    from pipeline.annotation_sample import use_utf8_console
    use_utf8_console()
    rep = run(Path(args.master), [Path(p) for p in args.annotations], args.names, args.classifier,
              Path(args.resolved) if args.resolved else None, Path(args.out), args.boot, args.kappa_min, args.precision_min, args.recall_min,
              refilter=(__import__("pipeline.telegram_refugee", fromlist=["x"]).reflag_fn(args.posts, args.clusters) if args.refilter else None))
    print(rep)
    print(f"Zapisano w {args.out}: wyniki_anotacji.md, do_rozstrzygniecia.csv, etykiety_referencyjne.csv, bledy_leksykonu.csv")


if __name__ == "__main__":
    main()
