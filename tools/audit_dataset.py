"""Audyt tabeli dostarczonej przez inżyniera danych (bez dostępu do sieci; działa wyłącznie na pliku CSV).

Wyniki wpisujemy do rejestru placeholderów (00): P01, P02, P03, P05, P06, P10, P11.

Użycie:
    python tools/audit_dataset.py dane.csv [--advertiser advertiser_id] [--lang language]

Raport w Markdown na stdout. Kolumny wymagane wg 03_specyfikacja_interfejsu_dane.md.
"""
from __future__ import annotations

import argparse

import pandas as pd

REQUIRED = ["ad_id", "creative_id", "advertiser_id", "platform", "retrieval_date", "ad_text", "language",
            "creative_available", "source_name", "source_version"]
CONDITIONAL = ["delivery_start", "delivery_stop", "reach_total", "dest_url", "dest_domain", "creative_path", "source_removed_flag", "frame_source"]


def concentration(counts: pd.Series) -> dict:
    """Udział 10 największych, indeks Herfindahla (HHI) i efektywna liczba klastrów 1/HHI."""
    s = counts / counts.sum()
    hhi = float((s**2).sum())
    return {"n_clusters": int(len(counts)), "top10_share": float(s.sort_values(ascending=False).head(10).sum()),
            "hhi": hhi, "effective_clusters": 1 / hhi if hhi else float("nan"), "largest_share": float(s.max())}


def audit(df: pd.DataFrame, advertiser_col: str = "advertiser_id", lang_col: str = "language") -> dict:
    out = {"n_rows": len(df)}
    out["missing_required_columns"] = [c for c in REQUIRED if c not in df.columns]
    out["present_conditional_columns"] = [c for c in CONDITIONAL if c in df.columns]
    reach_cols = [c for c in df.columns if c.startswith("reach_")]
    out["reach_columns"] = reach_cols
    out["reach_nonnull_share"] = {c: float(df[c].notna().mean()) for c in reach_cols}
    if "ad_id" in df:
        out["duplicate_ad_id"] = int(df["ad_id"].duplicated().sum())
    if "creative_id" in df:
        out["n_unique_creatives"] = int(df["creative_id"].nunique())
    if advertiser_col in df:
        out["n_advertisers"] = int(df[advertiser_col].nunique())
        out["advertiser_missing_share"] = float(df[advertiser_col].isna().mean())
        out["concentration"] = concentration(df[advertiser_col].value_counts())
    for c in ("delivery_start", "delivery_stop", "retrieval_date"):
        if c in df:
            d = pd.to_datetime(df[c], errors="coerce")
            out[c] = {"min": str(d.min())[:10], "max": str(d.max())[:10], "missing_share": float(d.isna().mean())}
    if "delivery_start" in df and "delivery_stop" in df:
        st = pd.to_datetime(df["delivery_start"], errors="coerce")
        sp = pd.to_datetime(df["delivery_stop"], errors="coerce")
        out["open_ended_share"] = float((st.notna() & sp.isna()).mean())  # brak końca emisji: reklama aktywna albo brak danych (cenzurowanie prawostronne)
        dur = (sp - st).dt.days.dropna()
        out["negative_duration_rows"] = int((dur < 0).sum())
        dur = dur[dur >= 0]
        out["closed_duration_days"] = ({"n": int(len(dur)), "p25": float(dur.quantile(.25)), "median": float(dur.median()),
                                         "p75": float(dur.quantile(.75)), "max": float(dur.max())} if len(dur) else {"n": 0})
    if lang_col in df:
        out["language_share"] = df[lang_col].value_counts(normalize=True).round(4).head(10).to_dict()
    for c in ("dest_url", "dest_domain"):
        if c in df:
            out[f"{c}_nonnull_share"] = float(df[c].notna().mean())
    if "creative_available" in df:
        out["creative_available_share"] = float(df["creative_available"].astype(str).str.lower().isin(["1", "true", "yes", "tak"]).mean())
    out["missing_share_by_column"] = df.isna().mean().round(4).to_dict()
    return out


def format_report(a: dict) -> str:
    L = ["# Audyt danych", f"- wierszy: {a['n_rows']}"]
    L.append(f"- brakujące kolumny wymagane: {a['missing_required_columns'] or 'brak'}")
    L.append(f"- obecne kolumny warunkowe: {a['present_conditional_columns'] or 'brak'}")
    L.append(f"- kolumny zasięgu: {a['reach_columns'] or 'brak (wyświetlenia/zasięg niedostępne: dzienna intensywność niemierzalna, D6)'}")
    if "duplicate_ad_id" in a:
        L.append(f"- zduplikowane ad_id: {a['duplicate_ad_id']}")
    if "n_unique_creatives" in a:
        L.append(f"- unikatowych kreacji: {a['n_unique_creatives']}")
    if "concentration" in a:
        c = a["concentration"]
        L.append(f"- reklamodawców: {c['n_clusters']}; udział 10 największych: {c['top10_share']:.1%}; największy: {c['largest_share']:.1%}; "
                 f"HHI: {c['hhi']:.4f}; efektywna liczba klastrów: {c['effective_clusters']:.1f}  → P02, P11, D7")
    if a.get("advertiser_missing_share", 0) > 0:
        L.append(f"- reklamy bez identyfikatora reklamodawcy: {a['advertiser_missing_share']:.1%} (poza klastrami; sprawdź, czy dotyczą reklam usuniętych)  → R23")
    for k in ("delivery_start", "delivery_stop", "retrieval_date"):
        if k in a:
            L.append(f"- {k}: {a[k]['min']} do {a[k]['max']}, braki {a[k]['missing_share']:.1%}  → P03")
    if "open_ended_share" in a:
        L.append(f"- reklamy bez daty końca emisji (aktywne albo brak danych; cenzurowanie prawostronne): {a['open_ended_share']:.1%}; "
                 f"wiersze z ujemnym czasem emisji: {a['negative_duration_rows']}  → P28, D6")
        L.append(f"- czas emisji reklam zakończonych (dni): {a['closed_duration_days']}  (opis; bez korekty cenzurowania; liczone jako stop − start, czyli o 1 mniej niż czas życia L w tools/outcomes.py)")
    if "language_share" in a:
        L.append(f"- języki: {a['language_share']}  → P10, D8")
    for k in ("dest_url_nonnull_share", "dest_domain_nonnull_share"):
        if k in a:
            L.append(f"- {k}: {a[k]:.1%}  → P05")
    if "creative_available_share" in a:
        L.append(f"- kreacje dostępne: {a['creative_available_share']:.1%}  → P04, D1")
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv"); p.add_argument("--advertiser", default="advertiser_id"); p.add_argument("--lang", default="language")
    a = p.parse_args(argv)
    # identyfikatory jako tekst: długie identyfikatory liczbowe tracą precyzję przy wczytaniu jako float
    id_cols = {c: str for c in ("ad_id", "creative_id", "advertiser_id", a.advertiser)}
    print(format_report(audit(pd.read_csv(a.csv, dtype=id_cols), a.advertiser, a.lang)))


if __name__ == "__main__":
    main()
