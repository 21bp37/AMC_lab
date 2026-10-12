"""Estymacja częstości zjawiska z niedoskonałym instrumentem + próbą z etykietami eksperckimi.

Zasada (wniosek z literatury): traktowanie predykcji modelu tak, jakby były obserwacjami bez błędu, prowadzi do
obciążenia i nieprawidłowych przedziałów ufności nawet przy dokładności > 90% [@egami2025dsl]. Rozwiązanie autorów
(DSL) łączy predykcje na całym zbiorze z mniejszą próbą etykiet eksperckich losowaną ze znanymi prawdopodobieństwami.

CO TU JEST, A CZEGO NIE MA (uczciwie):
- Jest wersja UPROSZCZONA dla prostego parametru (częstość/prevalence): estymator różnicowy
  theta = mean(pred na całej ramce) + (1/N) * suma_w_próbie( w_i * (gold_i - pred_i) ),  w_i = 1/inclusion_prob.
  Przy poprawnych wagach jest nieobciążony niezależnie od jakości modelu; jakość modelu wpływa tylko na wariancję.
- NIE ma pełnego DSL dla regresji (to, czego potrzebuje analiza końcowa z kowariatami). Do tego użyj implementacji
  autorów po przeczytaniu pracy (status: DO WDROŻENIA, patrz 05_gold_standard_i_walidacja.md).
- Przedział ufności: bootstrap klastrowy po reklamodawcach z zachowaniem wag; to przybliżenie dla próby dwufazowej.

Wejście: ramka `pop` o wszystkich rekordach ramki, kolumny: pred (0/1), gold (0/1 lub NaN poza próbą),
weight (1/inclusion_prob dla rekordów w próbie, NaN poza), cluster (opcjonalnie).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def naive_prevalence(pop: pd.DataFrame) -> float:
    return float(pop["pred"].mean())


def difference_estimate(pop: pd.DataFrame) -> float:
    n = len(pop)
    s = pop[pop["gold"].notna() & pop["weight"].notna()]
    resid = float(((s["gold"] - s["pred"]) * s["weight"]).sum())
    return float(pop["pred"].mean() + resid / n)


def bootstrap_ci(pop: pd.DataFrame, cluster_col: str | None = "cluster", boot: int = 500, seed: int = 0, level: float = 0.95):
    """CI bootstrapowy (po klastrach, jeśli podano) dla estymatora różnicowego; zwraca (estymata, lo, hi)."""
    rng = np.random.default_rng(seed)
    d = pop.reset_index(drop=True)
    groups = [g.index.to_numpy() for _, g in d.groupby(cluster_col)] if cluster_col and cluster_col in d else [np.array([i]) for i in range(len(d))]
    k = len(groups)
    vals = []
    for _ in range(boot):
        idx = np.concatenate([groups[i] for i in rng.integers(0, k, k)])
        vals.append(difference_estimate(d.loc[idx]))
    lo, hi = np.quantile(vals, [(1 - level) / 2, 1 - (1 - level) / 2])
    return difference_estimate(d), float(lo), float(hi)


def prevalence_from_sens_spec(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Korekta częstości przy ZAŁOŻONEJ czułości i swoistości (analiza wrażliwości, nie estymacja).

    Z tożsamości q = theta*sens + (1-theta)*(1-spec) wynika theta = (q - (1-spec)) / (sens - (1-spec)).
    Poprawne tylko gdy sens + spec > 1. Wynik obcinamy do [0,1]. Używaj z zakresem wartości (CI z walidacji),
    a nie z jedną liczbą.
    """
    denom = sensitivity - (1 - specificity)
    if denom <= 0:
        return float("nan")
    return float(min(1.0, max(0.0, (observed_rate - (1 - specificity)) / denom)))
