"""Losowanie warstwowe do gold standardu z limitem na klaster (dawniej reklamodawca; tu: konto źródłowe) i zapisem prawdopodobieństw włączenia.

Dlaczego zapis prawdopodobieństw: metody korygujące błąd klasyfikatora w analizie końcowej
(design-based supervised learning) wymagają, by próba z etykietami eksperckimi była losowana
ze znanymi prawdopodobieństwami [@egami2025dsl]. Warstwy należy definiować wyłącznie z cech znanych
PRZED annotacją (np. miesiąc, język, flaga z baseline'u słownikowego, predykcja instrumentu).

Dlaczego limit na reklamodawcę: ruch scamowy jest silnie skoncentrowany u nielicznych reklamodawców
(przykład: 10 największych = 56,1% reklam scamowych w raporcie Gen Digital [@gendigital2026]); bez limitu
gold standard odzwierciedlałby kilka kampanii.

Schemat (dwie fazy, prawdopodobieństwo włączenia = p1 * p2):
  Faza 1: w każdej komórce (warstwa x reklamodawca) zostaje min(cap, n_komórki) losowych reklam, p1 = m/n.
  Faza 2: w każdej warstwie losowanie proste n_h z N'_h reklam zachowanych, p2 = n_h / N'_h.

Użycie:
    python tools/sampling.py dane.csv --stratum stratum --advertiser advertiser_id --cap 5 \
        --n 30 --seed 42 --out proba.csv
    (--n może być liczbą lub JSON-em: '{"A": 50, "B": 20}')
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd


def stratified_sample(
    df: pd.DataFrame,
    stratum_col: str,
    n_per_stratum,
    advertiser_col: str | None = None,
    cap_per_advertiser: int | None = None,
    seed: int = 0,
) -> pd.DataFrame:
    """Zwraca próbę z kolumnami: inclusion_prob, weight (=1/inclusion_prob), stratum_N, stratum_N_capped, stratum_n."""
    rng = np.random.default_rng(seed)
    d = df.copy().reset_index(drop=True)
    d["_p1"] = 1.0
    d["_keep"] = True
    if advertiser_col and cap_per_advertiser:
        for _, g in d.groupby([stratum_col, advertiser_col]):
            n = len(g)
            if n > cap_per_advertiser:
                keep = rng.choice(g.index.to_numpy(), size=cap_per_advertiser, replace=False)
                d.loc[g.index, "_keep"] = False
                d.loc[keep, "_keep"] = True
                d.loc[g.index, "_p1"] = cap_per_advertiser / n
    n_full = d.groupby(stratum_col).size()
    frame = d[d["_keep"]]
    parts = []
    for s, g in frame.groupby(stratum_col):
        target = n_per_stratum[s] if isinstance(n_per_stratum, dict) else n_per_stratum
        n_h = int(min(target, len(g)))
        idx = rng.choice(g.index.to_numpy(), size=n_h, replace=False)
        sub = g.loc[idx].copy()
        sub["_p2"] = n_h / len(g)
        sub["stratum_N"] = int(n_full[s])
        sub["stratum_N_capped"] = len(g)
        sub["stratum_n"] = n_h
        parts.append(sub)
    res = pd.concat(parts)
    res["inclusion_prob"] = res["_p1"] * res["_p2"]
    res["weight"] = 1.0 / res["inclusion_prob"]
    return res.drop(columns=["_p1", "_p2", "_keep"]).reset_index(drop=True)


def summarize(sample: pd.DataFrame, stratum_col: str) -> pd.DataFrame:
    return (
        sample.groupby(stratum_col)
        .agg(N=("stratum_N", "first"), N_capped=("stratum_N_capped", "first"), n=("stratum_n", "first"),
             mean_inclusion_prob=("inclusion_prob", "mean"), sum_weights=("weight", "sum"))
        .reset_index()
    )


def horvitz_thompson_total(sample: pd.DataFrame, value_col: str) -> float:
    """Estymator Horvitza-Thompsona sumy wartości w populacji (wagi = 1/inclusion_prob)."""
    return float((sample[value_col] * sample["weight"]).sum())


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--stratum", required=True)
    p.add_argument("--advertiser")
    p.add_argument("--cap", type=int)
    p.add_argument("--n", required=True, help="liczba na warstwę albo JSON {warstwa: n}")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    df = pd.read_csv(a.csv)
    try:
        n = json.loads(a.n)
    except json.JSONDecodeError:
        n = int(a.n)
    s = stratified_sample(df, a.stratum, n, a.advertiser, a.cap, a.seed)
    s.to_csv(a.out, index=False)
    print(summarize(s, a.stratum).to_string(index=False))
    print(f"\nZapisano {len(s)} wierszy do {a.out}. Seed={a.seed} (zapisz w dzienniku uruchomień).")


if __name__ == "__main__":
    main()
