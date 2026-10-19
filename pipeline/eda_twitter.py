"""Eksploracja zbioru X/Twitter (PL, 2022): szeregi dzienne, piki, koncentracja, jakość pomiaru.

Użycie:
    python -m pipeline.eda_twitter [--input ścieżka.csv] [--z 3.0]
Wyniki (odtwarzalne, wersjonowane w repozytorium, bez treści postów):
    reports/eda_summary.json        - wszystkie liczby z eksploracji
    reports/eda_numbers.tex         - te same liczby jako makra LaTeX (\\EdaXxx) dla karty M1
    reports/peaks_table.tex         - tabela pików
    reports/figures/daily.pdf       - wolumen dzienny i udział treści negatywnych
    data/processed/twitter_daily.csv (poza repozytorium)
"""
from __future__ import annotations

import argparse
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pipeline import config  # noqa: E402
from pipeline.load_twitter import load_raw, normalize, quality_report  # noqa: E402
from pipeline.leadlag import power_peak_lag  # noqa: E402
from pipeline.series import daily_series, detect_peaks, peak_table  # noqa: E402

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"


def fmt_int(v) -> str:
    return f"{int(v):,}".replace(",", "\\,")


def fmt_pct(v, nd=1) -> str:
    return f"{100 * v:.{nd}f}\\,\\%".replace(".", ",")


def concentration(counts: pd.Series, top_frac: float = 0.01) -> dict:
    s = counts.sort_values(ascending=False)
    k = max(1, int(round(len(s) * top_frac)))
    return {"n": int(len(s)), "top1pct_share": float(s.head(k).sum() / s.sum()), "top10_share": float(s.head(10).sum() / s.sum())}


def plot_daily(daily: pd.DataFrame, peaks: pd.DatetimeIndex, out) -> None:
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 3.6), sharex=True, height_ratios=[1.5, 1])
    for ax in (a1, a2):
        ax.axvspan(pd.Timestamp(config.STUDY_START), pd.Timestamp(config.EFFECTIVE_START), color=GRID, lw=0)
        ax.grid(axis="y", color=GRID, lw=0.6)
    a1.plot(daily.index, daily["rows"], color=BLUE, lw=1.2, label="wszystkie wiersze")
    a1.plot(daily.index, daily["cascades"], color=ORANGE, lw=1.2, label="różne kaskady (treści)")
    a1.scatter(peaks, daily.loc[peaks, "cascades"], s=16, color=ORANGE, edgecolor="white", lw=0.8, zorder=3, label="pik (kaskady)")
    a1.set_ylabel("liczba / dzień")
    a1.legend(frameon=False, loc="upper right", ncols=3)
    roll = daily[["negative", "rows", "anti_lex"]].rolling(7, min_periods=4).sum()
    a2.plot(daily.index, roll["negative"] / roll["rows"], color=BLUE, lw=1.2, label="sentyment negatywny")
    a2.plot(daily.index, roll["anti_lex"] / roll["rows"], color=ORANGE, lw=1.2, label="leksykon narracji anty-UA")
    a2.set_ylabel("udział (7 dni)")
    a2.set_ylim(0, 1)
    a2.legend(frameon=False, loc="upper right", ncols=2)
    a2.text(pd.Timestamp(config.EFFECTIVE_START), 0.88, " zbiór niekompletny do 3.03", color=MUTED, fontsize=6.5)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def write_tex(summary: dict, peaks: pd.DataFrame) -> None:
    q, c = summary["quality"], summary["concentration"]
    m = {
        "NRows": fmt_int(q["n_rows"]), "NRt": fmt_int(q["n_by_type"].get("retweet", 0)),
        "NReply": fmt_int(q["n_by_type"].get("reply", 0)), "NOrig": fmt_int(q["n_by_type"].get("original", 0)),
        "NAuthors": fmt_int(q["n_authors"]), "NCascades": fmt_int(q["n_cascades"]),
        "NDays": fmt_int(q["n_days"]), "NBeforeEff": fmt_int(q["rows_before_effective_start"]),
        "MedDaily": fmt_int(q["median_daily_rows_effective"]),
        "ShareTrunc": fmt_pct(q["share_truncated_rt"]), "ShareBothOrig": fmt_pct(q["share_topic_both_original"]),
        "ShareNeg": fmt_pct(q["sentiment_dist"].get("negative", 0)), "ShareNeu": fmt_pct(q["sentiment_dist"].get("neutral", 0)),
        "SharePos": fmt_pct(q["sentiment_dist"].get("positive", 0)),
        "ShareScoreHigh": fmt_pct(q["share_sentiment_score_gt_0_95"]), "ShareLex": fmt_pct(q["share_anti_ua_lexicon"]),
        "TopOnePctAuthors": fmt_pct(c["authors"]["top1pct_share"]), "TopTenSources": fmt_pct(c["rt_sources"]["top10_share"]),
        "NPeaks": fmt_int(len(peaks)), "NPeaksRows": fmt_int(summary["n_peaks_rows"]), "NPeaksNeg": fmt_int(summary["n_peaks_neg_authored"]), "NPeaksOverlap": fmt_int(summary["peaks_overlap_rows_cascades"]), "PeakMedTopSrc": fmt_pct(summary["peaks_median_top_source_share"]),
        "NPeaksSingleSrc": fmt_int(summary["peaks_single_source_majority"]),
        "NRuDomain": fmt_int(summary["ru_domain_links"]), "NTme": fmt_int(summary["telegram_links"]),
        "NegShareRetweet": fmt_pct(summary["neg_by_type"]["retweet"]), "NegShareReply": fmt_pct(summary["neg_by_type"]["reply"]),
        "NegShareOrig": fmt_pct(summary["neg_by_type"]["original"]),
        "PowerHalf": fmt_pct(summary["power_peak_lag"]["0.5"], 0), "PowerHigh": fmt_pct(summary["power_peak_lag"]["0.8"], 0),
        "LexNeg": fmt_pct(summary["neg_share_given_lexicon"]["lex"]), "NoLexNeg": fmt_pct(summary["neg_share_given_lexicon"]["no_lex"]),
        "CorrNegLex": f"{summary['corr_daily_negshare_lexshare']:.2f}".replace(".", ","),
    }
    lines = ["% Wygenerowane przez python -m pipeline.eda_twitter. Nie edytować ręcznie."]
    lines += [f"\\newcommand{{\\Eda{k}}}{{{v}}}" for k, v in m.items()]
    (config.REPORTS / "eda_numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    rows = ["% Wygenerowane przez python -m pipeline.eda_twitter.", "\\begin{tabular}{@{}lrrrl@{}}", "\\toprule",
            "Dzień & Wiersze & Top konto & Negat. & Kontekst \\\\", "\\midrule"]
    for _, r in peaks.sort_values("n", ascending=False).head(8).iterrows():
        ev = r["event"].split(" (")[0] if r["event"] else "--"
        rows.append(f"{r['day']} & {fmt_int(r['n'])} & {fmt_pct(r['top_source_share'], 0)} & "
                    f"{fmt_pct(r['negative_share'], 0)} & {ev} \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    (config.REPORTS / "peaks_table.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")


def run(path: str, z: float) -> dict:
    df = normalize(load_raw(path))
    config.REPORTS.mkdir(exist_ok=True)
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    config.PROCESSED.mkdir(parents=True, exist_ok=True)

    daily = daily_series(df, config.STUDY_START, config.STUDY_END)
    daily.to_csv(config.PROCESSED / "twitter_daily.csv")
    eff = daily.loc[config.EFFECTIVE_START:]
    # Seria główna = liczba różnych kaskad (treści); `rows` jest zdominowane przez pojedyncze wiralowe RT
    peaks_rows = detect_peaks(eff["rows"], z=z)
    peaks = detect_peaks(eff["cascades"], z=z)
    ptab = peak_table(df, eff["rows"], peaks, config.EVENTS)
    peaks_cascades = peaks
    peaks_neg = detect_peaks(eff["negative_authored"], z=z)

    dom = df["domains"].dropna().str.lower().str.split().explode()
    ru = dom.str.contains(r"\b(?:rt\.com|sputnik|ria\.ru|tass\.|lenta\.ru|rg\.ru|pravda\.ru|iz\.ru)", regex=True)
    summary = {
        "quality": quality_report(df),
        "concentration": {
            "authors": concentration(df["author"].value_counts()),
            "rt_sources": concentration(df.loc[df["type"] == "retweet", "source_author"].value_counts()),
        },
        "neg_by_type": df.groupby("type")["negative"].mean().round(4).to_dict(),
        "lexicon_by_narrative": {c[4:]: float(df[c].mean()) for c in df.columns if c.startswith("nar_")},
        "neg_share_given_lexicon": {"lex": float(df.loc[df["anti_ua_lexicon"], "negative"].mean()),
                                    "no_lex": float(df.loc[~df["anti_ua_lexicon"], "negative"].mean())},
        "corr_daily_negshare_lexshare": float(eff["negative_share"].corr(eff["anti_lex_share"])),
        "n_peaks_rows": int(len(peaks_rows)),
        "peak_sensitivity": {str(zz): {c: int(len(detect_peaks(eff[c], z=zz))) for c in ["rows", "cascades", "negative_authored", "anti_lex"]}
                             for zz in (2.0, 2.5, 3.0)}, "n_peaks_cascades": int(len(peaks_cascades)), "n_peaks_neg_authored": int(len(peaks_neg)),
        "peaks_overlap_rows_cascades": int(len(set(peaks_rows) & set(peaks_cascades))),
        "peaks_median_top_source_share": float(ptab["top_source_share"].median()) if len(ptab) else float("nan"),
        "peaks_single_source_majority": int((ptab["top_source_share"] > 0.5).sum()) if len(ptab) else 0,
        "peaks": ptab.drop(columns=["top_source"]).assign(day=ptab["day"].astype(str)).to_dict(orient="records"),  # bez loginów
        "peaks_cascades": [str(p.date()) for p in peaks_cascades],
        "peaks_neg_authored": [str(p.date()) for p in peaks_neg],
        "ru_domain_links": int(ru.sum()),
        "telegram_links": int(dom.str.contains(r"t\.me|telegram", regex=True).sum()),
        "monthly_rows": {str(k): int(v) for k, v in daily["rows"].resample("MS").sum().items()},
        "nodexl_groups_top5": df["nodexl_group"].value_counts().head(5).to_dict(),
        "params": {"z": z, "window": 15, "sep": 3, "lexicon_version": config.LEXICON_VERSION,
                   "effective_start": config.EFFECTIVE_START},
    }
    # Moc testu dopasowania pików przy liczbie pików obserwowanej w X (symulacja, opóźnienie 3 dni)
    summary["power_peak_lag"] = {str(f): power_peak_lag(max(len(peaks), 1), lag=3, follow=f, reps=100, z=z)["power"]
                                 for f in (0.5, 0.8)}
    plot_daily(daily, peaks, config.FIGURES / "daily.pdf")
    write_tex(summary, ptab)
    (config.REPORTS / "eda_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="EDA X/Twitter")
    ap.add_argument("--input", default=str(config.RAW_TWITTER))
    ap.add_argument("--z", type=float, default=2.5)
    args = ap.parse_args()
    s = run(args.input, args.z)
    print(json.dumps({k: v for k, v in s.items() if k not in ("peaks",)}, ensure_ascii=False, indent=2, default=str)[:4000])


if __name__ == "__main__":
    main()
