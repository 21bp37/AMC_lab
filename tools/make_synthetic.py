"""Generator danych SYNTETYCZNYCH wyłącznie do testowania narzędzi. To NIE są dane o reklamach ani o zjawisku.

Struktura zaszyta celowo, żeby testy wykrywały typowe błędy metodyczne:
- reklamodawcy o rozkładzie silnie skośnym (kilku generuje większość reklam) -> klastrowanie,
- częstość ekspozycji zależna od reklamodawcy (dodatnie ICC) -> efektywne n < n,
- klasyfikator z czułością < 1 i swoistością < 1, o błędach zależnych od typu reklamy -> obciążenie naiwnej estymaty,
- wynik (reach) zależny od ekspozycji ze znanym efektem -> test odtwarzania efektu.

Użycie:
    python tools/make_synthetic.py --n 5000 --seed 1 --out data_synthetic/synthetic_ads.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def make_synthetic(n: int = 5000, n_advertisers: int = 120, prevalence: float = 0.10, sens: float = 0.70, spec: float = 0.98,
                   effect_on_log_reach: float = 0.30, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    w = 1.0 / np.arange(1, n_advertisers + 1) ** 1.1
    w /= w.sum()
    adv = rng.choice(n_advertisers, size=n, p=w)
    logit_mu = np.log(prevalence / (1 - prevalence))
    adv_eff = rng.normal(0, 1.2, n_advertisers)
    p_exp = 1 / (1 + np.exp(-(logit_mu + adv_eff[adv])))
    celeb_true = (rng.random(n) < p_exp).astype(int)
    scam_type = rng.choice(["investment_crypto", "health_supplements", "giveaway_contest", "other"], size=n, p=[0.45, 0.25, 0.2, 0.1])
    sens_i = np.where(scam_type == "other", sens - 0.15, sens)
    pred = np.where(celeb_true == 1, rng.random(n) < sens_i, rng.random(n) < (1 - spec)).astype(int)
    log_reach = 8 + 0.5 * adv_eff[adv] + effect_on_log_reach * celeb_true + rng.normal(0, 0.8, n)
    return pd.DataFrame({
        "ad_id": [f"SYN{i:06d}" for i in range(n)],
        "creative_id": [f"SYNC{i:06d}" for i in range(n)],
        "advertiser_id": [f"SYNADV{a:04d}" for a in adv],
        "month": rng.choice(["2026-07", "2026-08", "2026-09"], size=n),
        "scam_type": scam_type,
        "celeb_true": celeb_true,
        "celeb_pred": pred,
        "reach": np.exp(log_reach).round().astype(int),
        "is_synthetic": 1,
    })


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=5000); p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    df = make_synthetic(a.n, seed=a.seed)
    df.to_csv(a.out, index=False)
    print(f"Zapisano {len(df)} wierszy SYNTETYCZNYCH do {a.out}")


if __name__ == "__main__":
    main()
