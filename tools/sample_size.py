"""Planowanie liczebności gold standardu z szerokości przedziałów ufności.

Uzasadnienie podejścia: dla badań zgodności annotatorów liczebność dobiera się przez oczekiwaną
szerokość przedziału ufności współczynnika zgodności [@donner1987; @rotondi2012], a nie przez
stałą regułę kciuka. Dla metryk klasyfikatora (recall, precision) analogicznie: o precyzji decyduje
liczba przypadków pozytywnych w danej komórce, nie łączne n.

Uwaga (jawnie): progi typu "co najmniej X pozytywów na komórkę" NIE pochodzą z literatury, tylko z wyboru
docelowej szerokości przedziału; ta funkcja pozwala ten wybór uzasadnić liczbowo.

Podkomendy:
    python tools/sample_size.py wilson --k 40 --n 50
    python tools/sample_size.py positives --p 0.8 0.9 --npos 20 30 50 100
    python tools/sample_size.py need --p 0.8 --halfwidth 0.10
    python tools/sample_size.py alpha-sim --n 100 150 200 --prev 0.1 0.3 --acc 0.95 0.9
    python tools/sample_size.py deff --icc 0.1 --m 20
"""
from __future__ import annotations

import argparse
import math

import numpy as np

from agreement import alpha_binary_two_coders

Z95 = 1.959963984540054


def wilson_ci(k: int, n: int, z: float = Z95):
    """Przedział Wilsona dla proporcji."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (centre - half, centre + half)


def wilson_halfwidth(p: float, n: int, z: float = Z95) -> float:
    """Połowa szerokości przedziału Wilsona dla oczekiwanej proporcji p przy n obserwacjach."""
    k = round(p * n)
    lo, hi = wilson_ci(k, n, z)
    return (hi - lo) / 2


def n_needed(p: float, halfwidth: float, z: float = Z95, n_max: int = 100000) -> int:
    """Najmniejsze n, przy którym połowa szerokości przedziału Wilsona <= halfwidth."""
    lo, hi = 1, n_max
    if wilson_halfwidth(p, hi) > halfwidth:
        return n_max
    while lo < hi:
        mid = (lo + hi) // 2
        if wilson_halfwidth(p, mid) <= halfwidth:
            hi = mid
        else:
            lo = mid + 1
    return lo


def positives_table(ps=(0.7, 0.8, 0.9), npos=(20, 30, 50, 75, 100, 150)):
    """Tabela: połowa szerokości 95% CI recallu przy zadanej liczbie pozytywów w gold standardzie."""
    rows = []
    for n in npos:
        rows.append((n, *[wilson_halfwidth(p, n) for p in ps]))
    return rows


def simulate_alpha(n_units: int, prevalence: float, coder_accuracy: float, reps: int = 300, boot: int = 400, seed: int = 0):
    """Symulacja: oczekiwane alpha i połowa szerokości 95% CI dla 2 annotatorów i zmiennej binarnej.

    Model optymistyczny (błędy annotatorów niezależne); realne błędy są skorelowane, więc traktuj wynik jako
    dolną granicę niepewności. Bootstrap jednostek = losowanie wielomianowe z tabeli 2x2.
    """
    rng = np.random.default_rng(seed)
    alphas, halfw = [], []
    for _ in range(reps):
        truth = rng.random(n_units) < prevalence
        c1 = np.where(rng.random(n_units) < coder_accuracy, truth, ~truth)
        c2 = np.where(rng.random(n_units) < coder_accuracy, truth, ~truth)
        a = int(np.sum(c1 & c2)); b = int(np.sum(c1 & ~c2)); c = int(np.sum(~c1 & c2)); d = int(np.sum(~c1 & ~c2))
        al = alpha_binary_two_coders(a, b, c, d)
        if math.isnan(al):
            continue
        cells = rng.multinomial(n_units, np.array([a, b, c, d]) / n_units, size=boot)
        bs = [alpha_binary_two_coders(*row) for row in cells]
        bs = [v for v in bs if not math.isnan(v)]
        if len(bs) < boot * 0.5:
            continue
        lo, hi = np.quantile(bs, [0.025, 0.975])
        alphas.append(al)
        halfw.append((hi - lo) / 2)
    return {"mean_alpha": float(np.mean(alphas)), "median_halfwidth": float(np.median(halfw)), "valid_reps": len(alphas)}


def design_effect(icc: float, mean_cluster_size: float) -> float:
    """Efekt projektu dla próby klastrowej: deff = 1 + (m - 1) * icc (Kish; do weryfikacji w źródle, patrz 07)."""
    return 1 + (mean_cluster_size - 1) * icc


def effective_n(n: int, icc: float, mean_cluster_size: float) -> float:
    return n / design_effect(icc, mean_cluster_size)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("wilson"); s.add_argument("--k", type=int, required=True); s.add_argument("--n", type=int, required=True)
    s = sub.add_parser("positives"); s.add_argument("--p", type=float, nargs="+", default=[0.7, 0.8, 0.9]); s.add_argument("--npos", type=int, nargs="+", default=[20, 30, 50, 75, 100, 150])
    s = sub.add_parser("need"); s.add_argument("--p", type=float, required=True); s.add_argument("--halfwidth", type=float, required=True)
    s = sub.add_parser("alpha-sim"); s.add_argument("--n", type=int, nargs="+", required=True); s.add_argument("--prev", type=float, nargs="+", required=True); s.add_argument("--acc", type=float, nargs="+", required=True); s.add_argument("--reps", type=int, default=300)
    s = sub.add_parser("deff"); s.add_argument("--icc", type=float, required=True); s.add_argument("--m", type=float, required=True); s.add_argument("--n", type=int)
    a = p.parse_args(argv)

    if a.cmd == "wilson":
        lo, hi = wilson_ci(a.k, a.n); print(f"{a.k}/{a.n} = {a.k/a.n:.3f}; 95% CI Wilsona [{lo:.3f}; {hi:.3f}]")
    elif a.cmd == "positives":
        print("| liczba pozytywów | " + " | ".join(f"recall={x}" for x in a.p) + " |")
        print("|---|" + "---|" * len(a.p))
        for row in positives_table(tuple(a.p), tuple(a.npos)):
            print(f"| {row[0]} | " + " | ".join(f"±{v:.3f}" for v in row[1:]) + " |")
    elif a.cmd == "need":
        print(f"Potrzeba >= {n_needed(a.p, a.halfwidth)} przypadków pozytywnych dla ±{a.halfwidth} przy recall≈{a.p}")
    elif a.cmd == "alpha-sim":
        print("| n | prevalence | accuracy annotatora | oczekiwane alpha | połowa szer. 95% CI |")
        print("|---|---|---|---|---|")
        for n in a.n:
            for pv in a.prev:
                for ac in a.acc:
                    r = simulate_alpha(n, pv, ac, reps=a.reps)
                    print(f"| {n} | {pv} | {ac} | {r['mean_alpha']:.3f} | ±{r['median_halfwidth']:.3f} |")
    elif a.cmd == "deff":
        d = design_effect(a.icc, a.m); print(f"deff = {d:.2f}" + (f"; efektywne n = {effective_n(a.n, a.icc, a.m):.0f}" if a.n else ""))


if __name__ == "__main__":
    main()
