"""Eksploracja zbioru X/Twitter (PL, 2022): wolumen, ton, narracje anty-/pro-UA, trendy, zaangażowanie, peaki.

Dwie podstawy liczenia (świadomie rozdzielone):
- wpisy (wiersze): wszystko, co pojawiło się w strumieniu (z retweetami) -> „ile ludzie widzieli/przesyłali”,
- treści        : unikalne kaskady (retweety jednego wpisu liczone raz) -> „ile różnych rzeczy napisano”.
Udziały w czasie liczymy na treściach, bo jeden wiralowy wpis potrafi zmienić udział miesiąca o kilkanaście punktów.

Użycie:
    python -m pipeline.eda_twitter [--input ścieżka.csv] [--z 2.5]
Wyniki (bez treści postów i loginów):
    reports/eda_summary.json, reports/eda_numbers.tex (makra \\EdaXxx), reports/peaks_table.tex,
    reports/composition_table.tex, reports/monthly_table.tex, reports/eda_results.md, reports/figures/daily.pdf
"""
from __future__ import annotations

import argparse
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from pipeline import config  # noqa: E402
from pipeline.leadlag import power_peak_lag, power_xcorr  # noqa: E402
from pipeline.load_twitter import load_raw, normalize, quality_report  # noqa: E402
from pipeline.series import daily_series, detect_peaks, peak_table  # noqa: E402

BLUE, ORANGE, AQUA, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"
MONTHS = {3: "mar", 4: "kwi", 5: "maj", 6: "cze", 7: "lip", 8: "sie", 9: "wrz", 10: "paź", 11: "lis", 12: "gru"}


def fmt_int(v) -> str:
    return f"{int(v):,}".replace(",", "\\,")


def fmt_pct(v, nd=1) -> str:
    return f"{100 * v:.{nd}f}\\,\\%".replace(".", ",")


def fmt_num(v, nd=2) -> str:
    return f"{v:.{nd}f}".replace(".", "{,}").replace("-", "$-$")


def fmt_p(p) -> str:
    return "$p<0{,}001$" if p < 0.001 else f"$p={p:.3f}$".replace(".", "{,}")


def concentration(counts: pd.Series, top_frac: float = 0.01) -> dict:
    s = counts.sort_values(ascending=False)
    k = max(1, int(round(len(s) * top_frac)))
    return {"n": int(len(s)), "top1pct_share": float(s.head(k).sum() / s.sum()), "top10_share": float(s.head(10).sum() / s.sum())}


def two_prop(a: pd.Series, b: pd.Series) -> dict:
    """Test z dla dwóch proporcji (a, b: serie bool)."""
    n1, n2, x1, x2 = len(a), len(b), a.sum(), b.sum()
    p = (x1 + x2) / (n1 + n2)
    z = (x2 / n2 - x1 / n1) / np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return {"p1": float(x1 / n1), "p2": float(x2 / n2), "diff_pp": float(100 * (x2 / n2 - x1 / n1)),
            "z": float(z), "p": float(2 * stats.norm.sf(abs(z)))}


def weekly_shares(u: pd.DataFrame) -> pd.DataFrame:
    w = u.groupby(pd.Grouper(key="day", freq="W-SUN")).agg(
        n=("tweet_id", "size"), negative=("negative", "mean"), positive=("positive", "mean"),
        anti=("anti_ua_lexicon", "mean"), pro=("pro_ua_lexicon", "mean"),
        neg_anti=("neg_anti", "mean"), pos_pro=("pos_pro", "mean"))
    return w[w["n"] >= 30]   # tygodnie z mniej niż 30 treściami są zbyt zaszumione


def compute_stats(df: pd.DataFrame) -> dict:
    d = df[(df["day"] >= config.EFFECTIVE_START) & (df["day"] <= config.STUDY_END)].copy()
    d["neg_anti"] = d["negative"] & d["anti_ua_lexicon"]
    d["pos_pro"] = d["positive"] & d["pro_ua_lexicon"]
    u = d.drop_duplicates("cascade_key")                         # unikalne treści
    out = {}

    # 1. Skład: ton x leksykon (wpisy i treści)
    for name, base in {"rows": d, "contents": u}.items():
        out[f"composition_{name}"] = {
            "counts": pd.crosstab(base["stance_lex"], base["sentiment"]).to_dict(),
            "row_pct": pd.crosstab(base["stance_lex"], base["sentiment"], normalize="index").round(4).to_dict(),
            "stance_share": base["stance_lex"].value_counts(normalize=True).round(4).to_dict(),
            "n": int(len(base)),
            "neg_anti_share": float(base["neg_anti"].mean()), "pos_pro_share": float(base["pos_pro"].mean()),
            "neg_share": float(base["negative"].mean()), "pos_share": float(base["positive"].mean()),
            "anti_share": float(base["anti_ua_lexicon"].mean()), "pro_share": float(base["pro_ua_lexicon"].mean()),
            "neg_given_anti": float(base.loc[base["anti_ua_lexicon"], "negative"].mean()),
            "neutral_given_anti": float(base.loc[base["anti_ua_lexicon"], "sentiment"].eq("neutral").mean()),
            "pos_given_pro": float(base.loc[base["pro_ua_lexicon"], "positive"].mean()),
            "neg_given_pro": float(base.loc[base["pro_ua_lexicon"], "negative"].mean()),
            "anti_given_neg": float(base.loc[base["negative"], "anti_ua_lexicon"].mean()),
        }

    # 2. Miesięcznie (treści)
    m = u.groupby(u["day"].dt.to_period("M")).agg(
        n=("tweet_id", "size"), negative=("negative", "mean"), anti=("anti_ua_lexicon", "mean"),
        neg_anti=("neg_anti", "mean"), pro=("pro_ua_lexicon", "mean"), pos_pro=("pos_pro", "mean"))
    out["monthly_contents"] = {str(k): {c: float(v) for c, v in r.items()} for k, r in m.iterrows()}

    # 3. Trendy: korelacja Spearmana numeru tygodnia z udziałem (treści) + porównanie mar-kwi vs lis-gru
    w = weekly_shares(u)
    t = np.arange(len(w))
    out["weekly_trend"] = {c: dict(zip(("rho", "p"), map(float, stats.spearmanr(t, w[c]))))
                           for c in ["negative", "positive", "anti", "pro", "neg_anti", "pos_pro"]}
    out["n_weeks"] = int(len(w))
    early, late = u[u["day"] < "2022-05-01"], u[u["day"] >= "2022-11-01"]
    out["early_vs_late"] = {c: two_prop(early[c], late[c]) for c in ["negative", "anti_ua_lexicon", "neg_anti", "pro_ua_lexicon"]}

    # 4. Związki dzienne (wpisy)
    day = d.groupby("day").agg(n=("tweet_id", "size"), neg=("negative", "mean"), anti=("anti_ua_lexicon", "mean"),
                               pro=("pro_ua_lexicon", "mean"))
    sp = lambda a, b: dict(zip(("rho", "p"), map(float, stats.spearmanr(a, b))))  # noqa: E731
    out["daily_corr"] = {"volume_vs_neg": sp(day["n"], day["neg"]), "volume_vs_anti": sp(day["n"], day["anti"]),
                         "anti_vs_pro": sp(day["anti"], day["pro"]), "neg_vs_anti": sp(day["neg"], day["anti"])}

    # 5. Zaangażowanie oryginałów
    o = d[d["type"] == "original"]
    mw = lambda a, b: float(stats.mannwhitneyu(a, b).pvalue)  # noqa: E731
    out["engagement_originals"] = {
        "median_likes_by_sentiment": o.groupby("sentiment")["like_count"].median().to_dict(),
        "median_rt_by_stance": o.groupby("stance_lex")["retweet_count"].median().to_dict(),
        "n_by_sentiment": o["sentiment"].value_counts().to_dict(),
        "mwu_likes_pos_vs_neg_p": mw(o[o["positive"]]["like_count"], o[o["negative"]]["like_count"]),
        "mwu_likes_neg_vs_neutral_p": mw(o[o["negative"]]["like_count"], o[o["sentiment"] == "neutral"]["like_count"]),
        "mwu_rt_anti_vs_none_p": mw(o[o["stance_lex"] == "anti"]["retweet_count"], o[o["stance_lex"] == "brak"]["retweet_count"]),
    }
    out["neg_by_type"] = d.groupby("type")["negative"].mean().round(4).to_dict()
    out["_weekly"], out["_monthly"] = w, m
    return out


def plot_overview(daily: pd.DataFrame, w: pd.DataFrame, peaks: pd.DatetimeIndex, ptab: pd.DataFrame, out) -> None:
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})
    fig, axes = plt.subplots(3, 1, figsize=(7.0, 4.7), sharex=True, height_ratios=[1.15, 1, 1])
    a1, a2, a3 = axes
    for ax in axes:
        ax.grid(axis="y", color=GRID, lw=0.6)
    eff = daily.loc[config.EFFECTIVE_START:]
    # Peaki wykrywamy na liczbie RÓŻNYCH treści dziennie, względem lokalnej mediany - i to samo rysujemy.
    base = np.expm1(np.log1p(eff["cascades"].astype(float)).rolling(15, center=True, min_periods=7).median())
    a1.plot(eff.index, base, color=MUTED, lw=1.0, ls="--", label="tło: 15-dniowa mediana")
    a1.plot(eff.index, eff["cascades"], color=BLUE, lw=0.9, label="różne treści / dzień")
    a1.scatter(peaks, eff.loc[peaks, "cascades"], s=20, color=ORANGE, edgecolor="white", lw=0.8, zorder=3, label="peak")
    for _, r in ptab.iterrows():
        if r["event"]:
            d0 = pd.Timestamp(r["day"])
            a1.annotate(r["event"].split(" (")[0], (d0, eff.loc[d0, "cascades"]), xytext=(5, -2),
                        textcoords="offset points", fontsize=6.5, color=INK)
    a1.set_title("A. Ile różnych treści dziennie (retweety jednego wpisu liczone raz)")
    a1.set_ylabel("treści / dzień")
    a1.set_ylim(0, 520)
    a1.legend(frameon=False, loc="upper right", ncols=1, fontsize=7)

    a2.plot(w.index, w["negative"], color=BLUE, lw=1.4, marker="o", ms=2.5, label="negatywne (wobec kogokolwiek)")
    a2.plot(w.index, w["positive"], color=AQUA, lw=1.4, marker="o", ms=2.5, label="pozytywne")
    a2.set_ylim(0, 0.8)
    a2.set_title("B. Ton wszystkich treści według modelu sentymentu (tygodniowo)")
    a2.set_ylabel("udział treści")
    a2.legend(frameon=False, loc="upper left", ncols=2)

    a3.plot(w.index, w["anti"], color=ORANGE, lw=1.4, label="narracja anty-UA")
    a3.plot(w.index, w["neg_anti"], color=ORANGE, lw=1.1, ls="--", label="anty-UA i ton negatywny")
    a3.plot(w.index, w["pro"], color=AQUA, lw=1.4, label="treść pro-UA")
    a3.plot(w.index, w["pos_pro"], color=AQUA, lw=1.1, ls="--", label="pro-UA i ton pozytywny")
    a3.set_ylim(0, 0.3)
    a3.set_title("C. Narracje o Ukraińcach według leksykonów (tygodniowo)")
    a3.set_ylabel("udział treści")
    a3.legend(frameon=False, loc="upper left", ncols=2)
    for ax in (a2, a3):
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
    a3.set_xlim(pd.Timestamp(config.EFFECTIVE_START), pd.Timestamp(config.STUDY_END))
    a3.xaxis.set_major_locator(mdates.MonthLocator())
    a3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: MONTHS.get(mdates.num2date(v).month, "")))
    fig.tight_layout(h_pad=0.6)
    fig.savefig(out)
    plt.close(fig)


def write_tex(s: dict, peaks: pd.DataFrame, monthly: pd.DataFrame) -> None:
    q, c = s["quality"], s["concentration"]
    cr, cc = s["composition_rows"], s["composition_contents"]
    tr, el, dc, en = s["weekly_trend"], s["early_vs_late"], s["daily_corr"], s["engagement_originals"]
    m = {
        "NRows": fmt_int(q["n_rows"]), "NRt": fmt_int(q["n_by_type"].get("retweet", 0)),
        "NReply": fmt_int(q["n_by_type"].get("reply", 0)), "NOrig": fmt_int(q["n_by_type"].get("original", 0)),
        "NAuthors": fmt_int(q["n_authors"]), "NCascades": fmt_int(q["n_cascades"]), "NContents": fmt_int(cc["n"]),
        "NDays": fmt_int(q["n_days"]), "NBeforeEff": fmt_int(q["rows_before_effective_start"]),
        "MedDaily": fmt_int(q["median_daily_rows_effective"]),
        "ShareTrunc": fmt_pct(q["share_truncated_rt"]), "ShareBothOrig": fmt_pct(q["share_topic_both_original"]),
        "ShareScoreHigh": fmt_pct(q["share_sentiment_score_gt_0_95"]),
        "TopOnePctAuthors": fmt_pct(c["authors"]["top1pct_share"]), "TopTenSources": fmt_pct(c["rt_sources"]["top10_share"]),
        "NPeaks": fmt_int(len(peaks)), "NPeaksRows": fmt_int(s["n_peaks_rows"]), "NPeaksOverlap": fmt_int(s["peaks_overlap_rows_cascades"]),
        "NRuDomain": fmt_int(s["ru_domain_links"]), "NTme": fmt_int(s["telegram_links"]),
        "NegShareRetweet": fmt_pct(s["neg_by_type"]["retweet"]), "NegShareReply": fmt_pct(s["neg_by_type"]["reply"]),
        "PowerHalf": fmt_pct(s["power_peak_lag"]["0.5"], 0), "PowerHigh": fmt_pct(s["power_peak_lag"]["0.8"], 0),
        "PowerNull": fmt_pct(s["power_xcorr"]["0.0"], 0), "PowerRhoLow": fmt_pct(s["power_xcorr"]["0.2"], 0),
        "PowerRhoHigh": fmt_pct(s["power_xcorr"]["0.3"], 0),
        "CNeg": fmt_pct(cc["neg_share"]), "CPos": fmt_pct(cc["pos_share"]), "CAnti": fmt_pct(cc["anti_share"]),
        "CPro": fmt_pct(cc["pro_share"]), "CNegAnti": fmt_pct(cc["neg_anti_share"]), "CPosPro": fmt_pct(cc["pos_pro_share"]),
        "CNegGivenAnti": fmt_pct(cc["neg_given_anti"]), "CNeuGivenAnti": fmt_pct(cc["neutral_given_anti"]),
        "CPosGivenPro": fmt_pct(cc["pos_given_pro"]), "CNegGivenPro": fmt_pct(cc["neg_given_pro"]),
        "CAntiGivenNeg": fmt_pct(cc["anti_given_neg"]),
        "RNeg": fmt_pct(cr["neg_share"]), "RNegAnti": fmt_pct(cr["neg_anti_share"]), "RPosPro": fmt_pct(cr["pos_pro_share"]),
        "NWeeks": fmt_int(s["n_weeks"]),
        "TrNegRho": fmt_num(tr["negative"]["rho"]), "TrNegP": fmt_p(tr["negative"]["p"]),
        "TrAntiRho": fmt_num(tr["anti"]["rho"]), "TrAntiP": fmt_p(tr["anti"]["p"]),
        "TrNegAntiRho": fmt_num(tr["neg_anti"]["rho"]), "TrNegAntiP": fmt_p(tr["neg_anti"]["p"]),
        "TrProRho": fmt_num(tr["pro"]["rho"]), "TrProP": fmt_p(tr["pro"]["p"]),
        "TrPosRho": fmt_num(tr["positive"]["rho"]), "TrPosP": fmt_p(tr["positive"]["p"]),
        "ElNegA": fmt_pct(el["negative"]["p1"]), "ElNegB": fmt_pct(el["negative"]["p2"]), "ElNegP": fmt_p(el["negative"]["p"]),
        "ElAntiA": fmt_pct(el["anti_ua_lexicon"]["p1"]), "ElAntiB": fmt_pct(el["anti_ua_lexicon"]["p2"]),
        "ElAntiP": fmt_p(el["anti_ua_lexicon"]["p"]),
        "ElNegAntiA": fmt_pct(el["neg_anti"]["p1"]), "ElNegAntiB": fmt_pct(el["neg_anti"]["p2"]), "ElNegAntiP": fmt_p(el["neg_anti"]["p"]),
        "ElProA": fmt_pct(el["pro_ua_lexicon"]["p1"]), "ElProB": fmt_pct(el["pro_ua_lexicon"]["p2"]),
        "ElProP": fmt_p(el["pro_ua_lexicon"]["p"]),
        "CorVolNegRho": fmt_num(dc["volume_vs_neg"]["rho"]), "CorVolNegP": fmt_p(dc["volume_vs_neg"]["p"]),
        "CorAntiProRho": fmt_num(dc["anti_vs_pro"]["rho"]), "CorAntiProP": fmt_p(dc["anti_vs_pro"]["p"]),
        "CorNegAntiRho": fmt_num(dc["neg_vs_anti"]["rho"]), "CorNegAntiP": fmt_p(dc["neg_vs_anti"]["p"]),
        "LikesPos": fmt_int(en["median_likes_by_sentiment"].get("positive", 0)),
        "LikesNeg": fmt_int(en["median_likes_by_sentiment"].get("negative", 0)),
        "LikesNeu": fmt_int(en["median_likes_by_sentiment"].get("neutral", 0)),
        "LikesPosNegP": fmt_p(en["mwu_likes_pos_vs_neg_p"]), "LikesNegNeuP": fmt_p(en["mwu_likes_neg_vs_neutral_p"]),
        "RtAnti": fmt_int(en["median_rt_by_stance"].get("anti", 0)), "RtNone": fmt_int(en["median_rt_by_stance"].get("brak", 0)),
        "RtAntiP": fmt_p(en["mwu_rt_anti_vs_none_p"]),
    }
    lines = ["% Wygenerowane przez python -m pipeline.eda_twitter. Nie edytować ręcznie."]
    lines += [f"\\newcommand{{\\Eda{k}}}{{{v}}}" for k, v in m.items()]
    (config.REPORTS / "eda_numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    rows = ["% Wygenerowane przez python -m pipeline.eda_twitter.", "\\begin{tabular}{@{}lrrrl@{}}", "\\toprule",
            "Dzień & Wpisy & Top konto & Negat. & Kontekst \\\\", "\\midrule"]
    for _, r in peaks.sort_values("n", ascending=False).head(8).iterrows():
        ev = r["event"].split(" (")[0] if r["event"] else "--"
        rows.append(f"{r['day']} & {fmt_int(r['n'])} & {fmt_pct(r['top_source_share'], 0)} & "
                    f"{fmt_pct(r['negative_share'], 0)} & {ev} \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    (config.REPORTS / "peaks_table.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

    pct = pd.DataFrame(cc["row_pct"]).fillna(0)
    share = cc["stance_share"]
    names = {"anti": "narracja anty-UA", "pro": "treść pro-UA", "mieszane": "oba leksykony", "brak": "żaden leksykon"}
    t = ["% Wygenerowane przez python -m pipeline.eda_twitter.", "\\begin{tabular}{@{}lrrrr@{}}", "\\toprule",
         "Treści (unikalne) & Udział & Negat. & Neutr. & Pozyt. \\\\", "\\midrule"]
    for k in ["anti", "pro", "mieszane", "brak"]:
        if k in pct.index:
            t.append(f"{names[k]} & {fmt_pct(share.get(k, 0))} & {fmt_pct(pct.loc[k, 'negative'], 0)} & "
                     f"{fmt_pct(pct.loc[k, 'neutral'], 0)} & {fmt_pct(pct.loc[k, 'positive'], 0)} \\\\")
    t.append(f"\\midrule razem & 100\\,\\% & {fmt_pct(cc['neg_share'], 0)} & "
             f"{fmt_pct(1 - cc['neg_share'] - cc['pos_share'], 0)} & {fmt_pct(cc['pos_share'], 0)} \\\\")
    t += ["\\bottomrule", "\\end{tabular}"]
    (config.REPORTS / "composition_table.tex").write_text("\n".join(t) + "\n", encoding="utf-8")

    t = ["% Wygenerowane przez python -m pipeline.eda_twitter.", "\\begin{tabular}{@{}l" + "r" * len(monthly) + "@{}}",
         "\\toprule", " & " + " & ".join(MONTHS[p.month] for p in monthly.index) + " \\\\", "\\midrule"]
    labs = {"n": "treści (liczba)", "negative": "negatywne", "anti": "anty-UA", "neg_anti": "anty-UA i negat.",
            "pro": "pro-UA", "pos_pro": "pro-UA i pozyt."}
    for col, lab in labs.items():
        vals = [fmt_int(v) if col == "n" else f"{100 * v:.0f}" for v in monthly[col]]
        t.append(f"{lab} & " + " & ".join(vals) + " \\\\")
    t += ["\\bottomrule", "\\end{tabular}"]
    (config.REPORTS / "monthly_table.tex").write_text("\n".join(t) + "\n", encoding="utf-8")


def _pct(v, nd=1) -> str:
    return f"{100 * v:.{nd}f}%".replace(".", ",")


def _p(p) -> str:
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def _r(v) -> str:
    return f"{v:.2f}".replace(".", ",")


def write_results_md(s: dict) -> None:
    """reports/eda_results.md: wszystkie liczby z eksploracji z nazwą miary, podstawą liczenia i testem.

    Definicje miar i testów: reports/METODY.md (statyczny opis), ten plik jest generowany.
    """
    q, cc, cr = s["quality"], s["composition_contents"], s["composition_rows"]
    tr, el, dc, en = s["weekly_trend"], s["early_vs_late"], s["daily_corr"], s["engagement_originals"]
    L = ["# Wyniki eksploracji X/Twitter (generowane)", "",
         "Plik generuje `python -m pipeline.eda_twitter`; nie edytować ręcznie. Definicje miar, podstaw liczenia "
         "i testów: `reports/METODY.md` (numery sekcji w nawiasach §).", "",
         f"Parametry: okno {s['params']['effective_start']}–2022-12-31, próg peaku z = {s['params']['z']}, "
         f"okno mediany {s['params']['window']} dni, separacja ±{s['params']['sep']} dni, leksykony v{s['params']['lexicon_version']}.", "",
         "## 1. Zbiór (§1)", "",
         "| Miara | Wartość |", "|---|---|",
         f"| wpisy (wiersze) | {q['n_rows']:,} |".replace(",", " "),
         f"| w tym oryginały / odpowiedzi / retweety | {q['n_by_type'].get('original', 0)} / {q['n_by_type'].get('reply', 0)} / {q['n_by_type'].get('retweet', 0)} |",
         f"| konta (autorzy wierszy) | {q['n_authors']} |",
         f"| unikalne treści (kaskady) w oknie | {cc['n']} |",
         f"| wpisy przed {s['params']['effective_start']} (okres niekompletny) | {q['rows_before_effective_start']} |",
         f"| mediana wpisów na dzień w oknie | {q['median_daily_rows_effective']:.0f} |",
         f"| retweety z uciętym tekstem („…”) | {_pct(q['share_truncated_rt'])} |",
         f"| oryginały+odpowiedzi zawierające obie frazy doboru dosłownie | {_pct(q['share_topic_both_original'])} |",
         f"| etykiety sentymentu z pewnością > 0,95 | {_pct(q['share_sentiment_score_gt_0_95'])} |",
         f"| udział 10 najczęściej retweetowanych kont we wszystkich retweetach (§2.5) | {_pct(s['concentration']['rt_sources']['top10_share'])} |",
         f"| udział 1% najaktywniejszych kont we wszystkich wpisach (§2.5) | {_pct(s['concentration']['authors']['top1pct_share'])} |",
         f"| linki do rosyjskich mediów państwowych / do Telegrama | {s['ru_domain_links']} / {s['telegram_links']} |", "",
         "## 2. Skład: ton × leksykon (§2.3–2.4)", "",
         "Podstawa: unikalne treści w oknie. Odsetek w wierszu = udział tonu w danej grupie leksykonu.", "",
         "| Grupa leksykonu | Udział treści | Negatywne | Neutralne | Pozytywne |", "|---|---|---|---|---|"]
    pct = pd.DataFrame(cc["row_pct"]).fillna(0)
    names = {"anti": "tylko anty-UA", "pro": "tylko pro-UA", "mieszane": "oba leksykony", "brak": "żaden leksykon"}
    for k in ["anti", "pro", "mieszane", "brak"]:
        if k in pct.index:
            L.append(f"| {names[k]} | {_pct(cc['stance_share'].get(k, 0))} | {_pct(pct.loc[k, 'negative'], 0)} | "
                     f"{_pct(pct.loc[k, 'neutral'], 0)} | {_pct(pct.loc[k, 'positive'], 0)} |")
    L += ["", "| Miara (unikalne treści) | Wartość | To samo na wpisach z RT |", "|---|---|---|",
          f"| ton negatywny | {_pct(cc['neg_share'])} | {_pct(cr['neg_share'])} |",
          f"| ton pozytywny | {_pct(cc['pos_share'])} | {_pct(cr['pos_share'])} |",
          f"| leksykon anty-UA (w tym „oba”) | {_pct(cc['anti_share'])} | {_pct(cr['anti_share'])} |",
          f"| leksykon pro-UA (w tym „oba”) | {_pct(cc['pro_share'])} | {_pct(cr['pro_share'])} |",
          f"| anty-UA **i** ton negatywny | {_pct(cc['neg_anti_share'])} | {_pct(cr['neg_anti_share'])} |",
          f"| pro-UA **i** ton pozytywny | {_pct(cc['pos_pro_share'])} | {_pct(cr['pos_pro_share'])} |",
          f"| P(anty-UA \\| negatywne) | {_pct(cc['anti_given_neg'])} | {_pct(cr['anti_given_neg'])} |",
          f"| P(neutralne \\| anty-UA) | {_pct(cc['neutral_given_anti'])} | {_pct(cr['neutral_given_anti'])} |",
          f"| P(negatywne \\| pro-UA) | {_pct(cc['neg_given_pro'])} | {_pct(cr['neg_given_pro'])} |", "",
          "## 3. Trendy w czasie (§3.1, §3.2)", "",
          f"Trend: korelacja rang Spearmana ρ między numerem tygodnia a udziałem (unikalne treści; liczba tygodni z ≥ 30 treściami: {s['n_weeks']}"
          "), p dwustronne.", "",
          "| Udział treści | ρ | p |", "|---|---|---|"]
    labs = {"negative": "ton negatywny", "positive": "ton pozytywny", "anti": "anty-UA", "pro": "pro-UA",
            "neg_anti": "anty-UA i negatywne", "pos_pro": "pro-UA i pozytywne"}
    for k, lab in labs.items():
        L.append(f"| {lab} | {_r(tr[k]['rho'])} | {_p(tr[k]['p'])} |")
    L += ["", "Porównanie okresów: test z dla dwóch proporcji (pooled), unikalne treści, III–IV 2022 vs XI–XII 2022.", "",
          "| Udział treści | III–IV | XI–XII | różnica (pp) | z | p |", "|---|---|---|---|---|---|"]
    for k, lab in {"negative": "ton negatywny", "anti_ua_lexicon": "anty-UA", "neg_anti": "anty-UA i negatywne",
                   "pro_ua_lexicon": "pro-UA"}.items():
        e = el[k]
        L.append(f"| {lab} | {_pct(e['p1'])} | {_pct(e['p2'])} | {e['diff_pp']:+.1f} | {e['z']:.2f} | {_p(e['p'])} |".replace(".", ","))
    L += ["", "## 4. Związki dzienne (§3.1)", "",
          "Korelacja rang Spearmana po dniach okna (podstawa: wpisy z retweetami), p dwustronne.", "",
          "| Para zmiennych (dziennie) | ρ | p |", "|---|---|---|",
          f"| liczba wpisów vs udział negatywnych | {_r(dc['volume_vs_neg']['rho'])} | {_p(dc['volume_vs_neg']['p'])} |",
          f"| liczba wpisów vs udział anty-UA | {_r(dc['volume_vs_anti']['rho'])} | {_p(dc['volume_vs_anti']['p'])} |",
          f"| udział anty-UA vs udział pro-UA | {_r(dc['anti_vs_pro']['rho'])} | {_p(dc['anti_vs_pro']['p'])} |",
          f"| udział negatywnych vs udział anty-UA | {_r(dc['neg_vs_anti']['rho'])} | {_p(dc['neg_vs_anti']['p'])} |", "",
          "## 5. Zaangażowanie oryginałów (§3.3)", "",
          "Podstawa: tylko oryginały (bez retweetów i odpowiedzi); liczniki z chwili pobrania. Test U Manna–Whitneya, dwustronny.", "",
          "| Porównanie | Mediana A | Mediana B | p |", "|---|---|---|---|",
          f"| polubienia: pozytywne (A) vs negatywne (B) | {en['median_likes_by_sentiment'].get('positive', 0):.0f} | "
          f"{en['median_likes_by_sentiment'].get('negative', 0):.0f} | {_p(en['mwu_likes_pos_vs_neg_p'])} |",
          f"| polubienia: negatywne (A) vs neutralne (B) | {en['median_likes_by_sentiment'].get('negative', 0):.0f} | "
          f"{en['median_likes_by_sentiment'].get('neutral', 0):.0f} | {_p(en['mwu_likes_neg_vs_neutral_p'])} |",
          f"| retweety: anty-UA (A) vs żaden leksykon (B) | {en['median_rt_by_stance'].get('anti', 0):.0f} | "
          f"{en['median_rt_by_stance'].get('brak', 0):.0f} | {_p(en['mwu_rt_anti_vs_none_p'])} |", "",
          "## 6. Peaki (§2.6)", "",
          f"Seria: liczba różnych treści dziennie. Liczba peaków przy z = 2 / 2,5 / 3: "
          f"{s['peak_sensitivity']['2.0']['cascades']} / {s['peak_sensitivity']['2.5']['cascades']} / {s['peak_sensitivity']['3.0']['cascades']}. "
          f"Peaki tej serii pokrywają się z peakami serii wpisów z RT w {s['peaks_overlap_rows_cascades']} z {s['n_peaks_rows']} dni.", "",
          "| Dzień | Wpisy | Udział top konta | Udział top kaskady | Negatywne | Wydarzenie (±3 dni) |", "|---|---|---|---|---|---|"]
    for r in sorted(s["peaks"], key=lambda r: -r["n"]):
        L.append(f"| {r['day']} | {r['n']} | {_pct(r['top_source_share'], 0)} | {_pct(r['top_cascade_share'], 0)} | "
                 f"{_pct(r['negative_share'], 0)} | {r['event'] or '–'} |")
    L += ["", "## 7. Moc testów (§4.4)", "",
          "Test główny (korelacja dziennych przyrostów log(1+x), opóźnienia 0–7 dni, jednostronnie, 303 dni, 199 permutacji, "
          "100 powtórzeń symulacji, prawdziwe opóźnienie 2 dni):", "",
          "| Prawdziwa korelacja ρ | Odsetek wyników z p < 0,05 |", "|---|---|",
          f"| 0 (brak efektu; powinno być ≈ 5%) | {_pct(s['power_xcorr']['0.0'], 0)} |",
          f"| 0,2 | {_pct(s['power_xcorr']['0.2'], 0)} |",
          f"| 0,3 | {_pct(s['power_xcorr']['0.3'], 0)} |", "",
          f"Analiza uzupełniająca (dopasowanie peaków, {s['n_peaks_cascades']} peaków, opóźnienie 3 dni): moc "
          f"{_pct(s['power_peak_lag']['0.5'], 0)} przy 50% peaków z poprzednikiem na Telegramie, "
          f"{_pct(s['power_peak_lag']['0.8'], 0)} przy 80%.", ""]
    (config.REPORTS / "eda_results.md").write_text("\n".join(L), encoding="utf-8")


def run(path: str, z: float) -> dict:
    df = normalize(load_raw(path))
    for p in (config.REPORTS, config.FIGURES, config.PROCESSED):
        p.mkdir(parents=True, exist_ok=True)

    daily = daily_series(df, config.STUDY_START, config.STUDY_END)
    daily.to_csv(config.PROCESSED / "twitter_daily.csv")
    eff = daily.loc[config.EFFECTIVE_START:]
    # Seria główna peaków = liczba różnych kaskad (treści); `rows` jest zdominowane przez pojedyncze wiralowe RT
    peaks_rows = detect_peaks(eff["rows"], z=z)
    peaks = detect_peaks(eff["cascades"], z=z)
    ptab = peak_table(df, eff["rows"], peaks, config.EVENTS)

    dom = df["domains"].dropna().str.lower().str.split().explode()
    ru = dom.str.contains(r"\b(?:rt\.com|sputnik|ria\.ru|tass\.|lenta\.ru|rg\.ru|pravda\.ru|iz\.ru)", regex=True)
    st = compute_stats(df)
    summary = {
        "quality": quality_report(df),
        "concentration": {
            "authors": concentration(df["author"].value_counts()),
            "rt_sources": concentration(df.loc[df["type"] == "retweet", "source_author"].value_counts()),
        },
        **{k: v for k, v in st.items() if not k.startswith("_")},
        "n_peaks_rows": int(len(peaks_rows)), "n_peaks_cascades": int(len(peaks)),
        "peaks_overlap_rows_cascades": int(len(set(peaks_rows) & set(peaks))),
        "peak_sensitivity": {str(zz): {c: int(len(detect_peaks(eff[c], z=zz))) for c in ["rows", "cascades", "neg_anti", "anti_lex"]}
                             for zz in (2.0, 2.5, 3.0)},
        "peaks": ptab.drop(columns=["top_source"]).assign(day=ptab["day"].astype(str)).to_dict(orient="records"),  # bez loginów
        "ru_domain_links": int(ru.sum()),
        "telegram_links": int(dom.str.contains(r"t\.me|telegram", regex=True).sum()),
        "params": {"z": z, "window": 15, "sep": 3, "lexicon_version": config.LEXICON_VERSION,
                   "effective_start": config.EFFECTIVE_START},
    }
    # Moc testu głównego hipotezy (korelacja dziennych przyrostów, k = 0..7, jednostronnie; 303 dni, symulacja)
    summary["power_xcorr"] = {str(r): power_xcorr(r, reps=100) for r in (0.0, 0.2, 0.3)}
    # Moc analizy uzupełniającej (dopasowanie peaków) przy liczbie peaków obserwowanej w X
    summary["power_peak_lag"] = {str(f): power_peak_lag(max(len(peaks), 1), lag=3, follow=f, reps=100, z=z)["power"]
                                 for f in (0.5, 0.8)}
    plot_overview(daily, st["_weekly"], peaks, ptab, config.FIGURES / "daily.pdf")
    write_tex(summary, ptab, st["_monthly"])
    write_results_md(summary)
    (config.REPORTS / "eda_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="EDA X/Twitter")
    ap.add_argument("--input", default=str(config.RAW_TWITTER))
    ap.add_argument("--z", type=float, default=2.5)
    args = ap.parse_args()
    s = run(args.input, args.z)
    keys = ["composition_contents", "weekly_trend", "early_vs_late", "daily_corr", "engagement_originals", "peak_sensitivity"]
    print(json.dumps({k: s[k] for k in keys}, ensure_ascii=False, indent=1, default=str)[:7000])


if __name__ == "__main__":
    main()
