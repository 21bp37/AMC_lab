"""Ewaluacja instrumentu względem gold standardu: P/R/F1 per klasa, macierz pomyłek, CI przez bootstrap klastrowy.

Założenia metodyczne:
- Obserwacje (reklamy) są skorelowane w obrębie reklamodawcy, więc przedziały ufności liczymy
  bootstrapem po klastrach (reklamodawcach), a nie po reklamach [@cameron2015].
- Gold standard losowany warstwowo ma nierówne prawdopodobieństwa włączenia; metryki "populacyjne"
  liczymy z wagami 1/inclusion_prob (kolumna `weight` z tools/sampling.py).
- Zawsze raportuj prevalence razem z precision: precision zależy od częstości zjawiska.
- Metryki klasyfikatora to NIE to samo co poprawność wniosku końcowego: patrz estimators.py i [@egami2025dsl].

Użycie:
    python tools/evaluation.py proba_z_predykcjami.csv --true gold --pred model --label tak \
        --cluster advertiser_id --weight weight --boot 1000
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def confusion(y_true, y_pred, labels=None, weights=None) -> pd.DataFrame:
    y_true = pd.Series(list(y_true)); y_pred = pd.Series(list(y_pred))
    w = pd.Series(np.ones(len(y_true)) if weights is None else np.asarray(weights, dtype=float))
    labels = labels or sorted(set(y_true) | set(y_pred))
    m = pd.DataFrame(0.0, index=labels, columns=labels)
    for t, p, wi in zip(y_true, y_pred, w):
        m.loc[t, p] += wi
    m.index.name = "prawda \\ predykcja"
    return m


def prf(y_true, y_pred, label, weights=None) -> dict:
    yt = np.asarray(list(y_true)) == label
    yp = np.asarray(list(y_pred)) == label
    w = np.ones(len(yt)) if weights is None else np.asarray(weights, dtype=float)
    tp = float(np.sum(w * (yt & yp))); fp = float(np.sum(w * (~yt & yp))); fn = float(np.sum(w * (yt & ~yp)))
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) and not np.isnan(prec + rec) else float("nan")
    return {"precision": prec, "recall": rec, "f1": f1, "support": int(yt.sum()), "prevalence": float(np.sum(w * yt) / np.sum(w))}


def cluster_bootstrap_prf(df: pd.DataFrame, true_col: str, pred_col: str, label, cluster_col: str | None = None,
                          weight_col: str | None = None, boot: int = 1000, seed: int = 0, level: float = 0.95) -> dict:
    """Bootstrap po klastrach (lub po wierszach, gdy brak kolumny klastra). Zwraca estymaty punktowe i CI."""
    rng = np.random.default_rng(seed)
    d = df.reset_index(drop=True)
    point = prf(d[true_col], d[pred_col], label, d[weight_col] if weight_col else None)
    groups = [g.index.to_numpy() for _, g in d.groupby(cluster_col)] if cluster_col else [np.array([i]) for i in range(len(d))]
    k = len(groups)
    draws = {m: [] for m in ("precision", "recall", "f1", "prevalence")}
    for _ in range(boot):
        pick = rng.integers(0, k, k)
        idx = np.concatenate([groups[i] for i in pick])
        s = d.loc[idx]
        r = prf(s[true_col], s[pred_col], label, s[weight_col] if weight_col else None)
        for m in draws:
            if not np.isnan(r[m]):
                draws[m].append(r[m])
    q = [(1 - level) / 2, 1 - (1 - level) / 2]
    out = {"n_rows": len(d), "n_clusters": k, "support": point["support"]}
    for m in draws:
        lo, hi = np.quantile(draws[m], q) if draws[m] else (np.nan, np.nan)
        out[m] = (point[m], float(lo), float(hi))
    return out


def format_report(res: dict, label) -> str:
    lines = [f"Klasa: {label}; wierszy: {res['n_rows']}; klastrów: {res['n_clusters']}; pozytywów w gold: {res['support']}",
             "| metryka | estymata | 95% CI |", "|---|---|---|"]
    for m in ("precision", "recall", "f1", "prevalence"):
        e, lo, hi = res[m]
        lines.append(f"| {m} | {e:.3f} | [{lo:.3f}; {hi:.3f}] |")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv"); p.add_argument("--true", required=True); p.add_argument("--pred", required=True)
    p.add_argument("--label", required=True); p.add_argument("--cluster"); p.add_argument("--weight")
    p.add_argument("--boot", type=int, default=1000); p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    df = pd.read_csv(a.csv, dtype={a.true: str, a.pred: str})
    print(confusion(df[a.true], df[a.pred], weights=df[a.weight] if a.weight else None).round(2).to_string())
    print()
    print(format_report(cluster_bootstrap_prf(df, a.true, a.pred, a.label, a.cluster, a.weight, a.boot, a.seed), a.label))


if __name__ == "__main__":
    main()
