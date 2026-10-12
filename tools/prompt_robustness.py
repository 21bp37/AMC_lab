"""Wrażliwość etykiet na wariant promptu / model / powtórzenie uruchomienia.

Uzasadnienie: w replikacji 37 zadań adnotacji z 21 badań autorzy pokazali, że konfiguracja (np. parafraza promptu)
potrafi zmienić wnioski: ok. 31% hipotez miało błędne wnioski nawet dla najlepszych modeli, a ludzkie adnotacje
zmniejszają ryzyko fałszywie pozytywnych wyników [@baumann2025].
Dlatego każdy wynik końcowy raportujemy jako zakres po konfiguracjach, nie jako jedną wartość.

Wejście: CSV w formacie długim: item_id, config, label  (config = np. "prompt_v3|model_x|run2").

Użycie:
    python tools/prompt_robustness.py predykcje_long.csv --positive tak
"""
from __future__ import annotations

import argparse
import itertools

import pandas as pd

from agreement import cohen_kappa


def robustness_report(df: pd.DataFrame, item="item_id", config="config", label="label", positive=None) -> dict:
    wide = df.pivot_table(index=item, columns=config, values=label, aggfunc="first")
    cfgs = list(wide.columns)
    pair_kappas = {}
    for a, b in itertools.combinations(cfgs, 2):
        pair_kappas[(a, b)] = cohen_kappa(wide[a].tolist(), wide[b].tolist())
    flip_rate = float((wide.nunique(axis=1) > 1).mean())
    out = {"n_items": len(wide), "n_configs": len(cfgs), "flip_rate": flip_rate, "pair_kappas": pair_kappas}
    if positive is not None:
        prev = {c: float((wide[c] == positive).mean()) for c in cfgs}
        out["prevalence_by_config"] = prev
        out["prevalence_range"] = (min(prev.values()), max(prev.values()))
    return out


def format_report(r: dict) -> str:
    ks = [v for v in r["pair_kappas"].values() if v == v]
    lines = [f"Elementów: {r['n_items']}; konfiguracji: {r['n_configs']}",
             f"Odsetek elementów, w których konfiguracje się różnią (flip rate): {r['flip_rate']:.3f}"]
    if ks:
        lines.append(f"Kappa między konfiguracjami: min {min(ks):.3f}, mediana {sorted(ks)[len(ks)//2]:.3f}, max {max(ks):.3f}")
    if "prevalence_range" in r:
        lo, hi = r["prevalence_range"]
        lines.append(f"Zakres częstości pozytywów po konfiguracjach: [{lo:.3f}; {hi:.3f}]")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv"); p.add_argument("--positive")
    a = p.parse_args(argv)
    print(format_report(robustness_report(pd.read_csv(a.csv, dtype=str), positive=a.positive)))


if __name__ == "__main__":
    main()
