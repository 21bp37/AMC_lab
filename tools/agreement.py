"""Miary zgodności annotatorów (nominalne).

Podstawy (szczegóły i status weryfikacji: 07_bibliografia.md):
- Krippendorff alpha i progi 0,80 / 0,667: [@krippendorff2004]
- Paradoks kappa przy niskiej prevalence: [@feinstein1990; @cicchetti1990; @byrt1993]
- Zalecenie raportowania prevalence oraz zgodności pozytywnej/negatywnej: [@chen2009]

Dane wejściowe CLI: CSV w formacie "długim" (jeden wiersz = jedna ocena jednego
annotatora dla jednej reklamy), zgodny z templates/annotation_sheet_template.csv.

Użycie:
    python tools/agreement.py arkusz.csv --unit creative_id --coder annotator_id \
        --vars celeb_mention scam_type --boot 1000
"""
from __future__ import annotations

import argparse
import itertools
import math
from collections import Counter
from typing import Iterable, Sequence

import numpy as np

NAN = float("nan")
MISSING = {None, "", "NA", "na", "nan", "NaN"}


def _clean(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    return None if v in MISSING else v


def cohen_kappa(a: Sequence, b: Sequence) -> float:
    """Kappa Cohena dla dwóch annotatorów; pary z brakami są pomijane.

    Zwraca NaN, gdy kappa jest nieokreślona (np. obaj użyli jednej kategorii).
    """
    pairs = [(_clean(x), _clean(y)) for x, y in zip(a, b)]
    pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return NAN
    po = sum(x == y for x, y in pairs) / n
    ca = Counter(x for x, _ in pairs)
    cb = Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / n**2
    if pe >= 1.0:
        return NAN
    return (po - pe) / (1 - pe)


def krippendorff_alpha(units: Iterable[Sequence]) -> float:
    """Alpha Krippendorffa dla danych nominalnych, dowolna liczba annotatorów, braki dozwolone.

    `units`: lista jednostek; każda jednostka to lista ocen (None = brak oceny).
    Implementacja przez macierz koincydencji; jednostki z <2 ocenami są pomijane.
    """
    o = Counter()
    for u in units:
        vals = [v for v in (_clean(x) for x in u) if v is not None]
        m = len(vals)
        if m < 2:
            continue
        for i, j in itertools.permutations(range(m), 2):
            o[(vals[i], vals[j])] += 1.0 / (m - 1)
    n_c = Counter()
    for (c, _k), w in o.items():
        n_c[c] += w
    n = sum(n_c.values())
    if n <= 1:
        return NAN
    disagree_o = sum(w for (c, k), w in o.items() if c != k)
    cats = list(n_c)
    disagree_e = sum(n_c[c] * n_c[k] for c in cats for k in cats if c != k)
    if disagree_e == 0:
        return NAN
    return 1.0 - (n - 1) * disagree_o / disagree_e


def alpha_binary_two_coders(a: float, b: float, c: float, d: float) -> float:
    """Alpha dla 2 annotatorów i zmiennej binarnej z tabeli 2x2 (szybka ścieżka do symulacji).

    a=(1,1), b=(1,0), c=(0,1), d=(0,0). Równoważne krippendorff_alpha() bez braków.
    """
    n_units = a + b + c + d
    n1 = 2 * a + b + c
    n0 = 2 * d + b + c
    denom = 2 * n1 * n0
    if denom == 0:
        return NAN
    return 1.0 - (2 * n_units - 1) * 2 * (b + c) / denom


def bootstrap_alpha_ci(units: Sequence[Sequence], boot: int = 1000, level: float = 0.95, seed: int = 0):
    """Przedział bootstrapowy dla alpha (resampling jednostek)."""
    rng = np.random.default_rng(seed)
    units = list(units)
    n = len(units)
    vals = []
    for _ in range(boot):
        idx = rng.integers(0, n, n)
        v = krippendorff_alpha([units[i] for i in idx])
        if not math.isnan(v):
            vals.append(v)
    if not vals:
        return (NAN, NAN)
    lo, hi = np.quantile(vals, [(1 - level) / 2, 1 - (1 - level) / 2])
    return (float(lo), float(hi))


def binary_agreement_stats(a: Sequence, b: Sequence, positive) -> dict:
    """Statystyki dla zmiennej binarnej: prevalence index, bias index, zgodność pozytywna/negatywna.

    Definicje: PI=(a-d)/N, BI=(b-c)/N [@byrt1993]; PA=2a/(2a+b+c), NA=2d/(2d+b+c) [@cicchetti1990].
    """
    pairs = [(_clean(x), _clean(y)) for x, y in zip(a, b)]
    pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return {}
    A = sum(1 for x, y in pairs if x == positive and y == positive)
    B = sum(1 for x, y in pairs if x == positive and y != positive)
    C = sum(1 for x, y in pairs if x != positive and y == positive)
    D = sum(1 for x, y in pairs if x != positive and y != positive)
    pa = 2 * A / (2 * A + B + C) if (2 * A + B + C) else NAN
    na = 2 * D / (2 * D + B + C) if (2 * D + B + C) else NAN
    return {
        "n": n,
        "observed_agreement": (A + D) / n,
        "prevalence_index": (A - D) / n,
        "bias_index": (B - C) / n,
        "positive_agreement": pa,
        "negative_agreement": na,
        "cells": {"a": A, "b": B, "c": C, "d": D},
    }


def interpret_alpha(alpha: float) -> str:
    """Interpretacja wg progów Krippendorffa [@krippendorff2004].

    Uwaga: autor zaleca dobierać próg do kosztu błędnych wniosków; progi są konwencją, nie prawem.
    """
    if alpha is None or (isinstance(alpha, float) and math.isnan(alpha)):
        return "nieokreślone"
    if alpha >= 0.80:
        return "wiarygodne (>=0,80)"
    if alpha >= 0.667:
        return "tylko wnioski wstępne (0,667-0,80)"
    return "niewystarczające (<0,667)"


def _units_from_long(df, unit_col: str, coder_col: str, var: str):
    coders = sorted(df[coder_col].dropna().unique())
    units = []
    for _, g in df.groupby(unit_col):
        row = {c: None for c in coders}
        for _, r in g.iterrows():
            row[r[coder_col]] = r[var]
        units.append([row[c] for c in coders])
    return units, coders


def report(df, unit_col: str, coder_col: str, variables: Sequence[str], boot: int = 1000, seed: int = 0) -> str:
    """Tabela Markdown: alpha + CI + średni kappa parami + prevalence dla każdej zmiennej."""
    lines = [
        "| zmienna | jednostek | alpha | 95% CI | kappa (śr. par) | najczęstsza kategoria | interpretacja |",
        "|---|---|---|---|---|---|---|",
    ]
    for var in variables:
        units, coders = _units_from_long(df, unit_col, coder_col, var)
        alpha = krippendorff_alpha(units)
        lo, hi = bootstrap_alpha_ci(units, boot=boot, seed=seed) if boot else (NAN, NAN)
        kappas = []
        for i, j in itertools.combinations(range(len(coders)), 2):
            k = cohen_kappa([u[i] for u in units], [u[j] for u in units])
            if not math.isnan(k):
                kappas.append(k)
        kappa = float(np.mean(kappas)) if kappas else NAN
        flat = [_clean(v) for u in units for v in u]
        flat = [v for v in flat if v is not None]
        top = Counter(flat).most_common(1)
        top_s = f"{top[0][0]} ({top[0][1] / len(flat):.0%})" if top else "-"
        lines.append(
            f"| {var} | {len(units)} | {alpha:.3f} | [{lo:.3f}; {hi:.3f}] | {kappa:.3f} | {top_s} | {interpret_alpha(alpha)} |"
        )
    return "\n".join(lines)


def main(argv=None):
    import pandas as pd

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--unit", default="creative_id")
    p.add_argument("--coder", default="annotator_id")
    p.add_argument("--vars", nargs="+", required=True)
    p.add_argument("--boot", type=int, default=1000)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    df = pd.read_csv(a.csv, dtype=str)
    print(report(df, a.unit, a.coder, a.vars, boot=a.boot, seed=a.seed))


if __name__ == "__main__":
    main()
