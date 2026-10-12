"""Zmienne wynikowe pytania badawczego: czas życia reklamy i dzienna intensywność wyświetleń.

Definicje (parametry progów należą do leada i mogą się zmienić; domyślne wartości = hipoteza z 01):
- czas życia L (dni kalendarzowe, włącznie z dniem pierwszym i ostatnim) = (delivery_stop - delivery_start) + 1;
  reklama z tego samego dnia ma L = 1.
- dzienna intensywność I = skumulowane wyświetlenia (kolumna zasięgu, domyślnie `reach_total`) / L.
  Źródło nie udostępnia rozkładu w czasie (tylko sumę za okres), więc I to średnia, a nie przebieg dzienny.
- reklama bez daty końca = cenzurowana prawostronnie (wciąż aktywna w dniu pobrania): jej L jest dolnym ograniczeniem
  (retrieval_date - delivery_start + 1), a prawdziwe L jest nieznane.

Co robi moduł: policzenie L i I, ważona mediana i ważony udział reklam z I >= próg, pasmo mediany L (reklamy aktywne
liczone jako obserwowane do dnia pobrania = dolne ograniczenie; jako nieskończone = górne), bootstrap po klastrach.
Czego NIE robi: nie jest modelem przeżycia (Kaplan-Meier, modele parametryczne: zadanie analityka) i nie koryguje
błędu klasyfikacji populacji (05, sekcja 6). Wagi = 1/prawdopodobieństwo włączenia (próba z gold standardu).
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd


def compute_outcomes(df: pd.DataFrame, start: str = "delivery_start", stop: str = "delivery_stop",
                     retrieval: str = "retrieval_date", reach: str = "reach_total") -> pd.DataFrame:
    d = df.copy()
    s = pd.to_datetime(d[start], errors="coerce")
    e = pd.to_datetime(d[stop], errors="coerce")
    r = pd.to_datetime(d[retrieval], errors="coerce")
    d["open_ended"] = e.isna() & s.notna()
    end_obs = e.fillna(r)
    d["lifetime_days"] = (end_obs - s).dt.days + 1          # dla reklam aktywnych: dolne ograniczenie
    d.loc[d["lifetime_days"] < 1, "lifetime_days"] = np.nan  # stop przed start lub brak dat: odrzucamy, nie naprawiamy
    d["lifetime_days"] = d["lifetime_days"].astype(float)
    if reach in d:
        d["reach_total"] = pd.to_numeric(d[reach], errors="coerce")
        d["intensity_per_day"] = d["reach_total"] / d["lifetime_days"]
    return d


def weighted_quantile(x, w, q: float) -> float:
    """Najmniejsza wartość x, przy której skumulowana waga >= q * suma wag (definicja dla wartości dyskretnych)."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    ok = ~(np.isnan(x) | np.isnan(w))
    x, w = x[ok], w[ok]
    if len(x) == 0:
        return float("nan")
    order = np.argsort(x, kind="stable")
    x, w = x[order], w[order]
    cum = np.cumsum(w)
    return float(x[np.searchsorted(cum, q * cum[-1] - 1e-12)])


def weighted_share_at_least(x, w, thr: float) -> float:
    x = np.asarray(x, float); w = np.asarray(w, float)
    ok = ~(np.isnan(x) | np.isnan(w))
    return float(w[ok][x[ok] >= thr].sum() / w[ok].sum()) if ok.any() else float("nan")


def median_lifetime_bounds(d: pd.DataFrame, weight: str = "weight") -> tuple[float, float]:
    """(dolne, górne) ograniczenie mediany L. Dolne: reklamy aktywne z L obserwowanym do pobrania.
    Górne: reklamy aktywne jako nieskończone (najgorszy przypadek)."""
    w = d[weight] if weight in d else pd.Series(1.0, index=d.index)
    lo = weighted_quantile(d["lifetime_days"], w, 0.5)
    hi_x = d["lifetime_days"].where(~d["open_ended"], np.inf)
    hi = weighted_quantile(hi_x, w, 0.5)
    return lo, hi


def _boot(d: pd.DataFrame, fn, cluster: str | None, boot: int, seed: int, level: float):
    rng = np.random.default_rng(seed)
    d = d.reset_index(drop=True)
    groups = [g.index.to_numpy() for _, g in d.groupby(cluster)] if cluster and cluster in d else [np.array([i]) for i in range(len(d))]
    k = len(groups)
    vals = [fn(d.loc[np.concatenate([groups[i] for i in rng.integers(0, k, k)])]) for _ in range(boot)]
    a = (1 - level) / 2
    lo, hi = np.nanquantile(vals, [a, 1 - a])
    return fn(d), float(lo), float(hi)


def summarize(d: pd.DataFrame, thr_days: float = 2, thr_intensity: float = 25000, min_share: float = 0.5,
              weight: str = "weight", cluster: str | None = "advertiser_id", boot: int = 500, seed: int = 0) -> dict:
    """d: populacja badana (tylko pozytywy), po compute_outcomes. Zwraca estymaty i 95% CI (bootstrap po klastrach)."""
    d = d.copy()
    if weight not in d:
        d[weight] = 1.0
    out = {"n": int(len(d)), "n_open_ended": int(d["open_ended"].sum()),
           "n_valid_lifetime": int(d["lifetime_days"].notna().sum())}
    med = lambda x: weighted_quantile(x["lifetime_days"], x[weight], 0.5)
    out["median_lifetime_days"] = dict(zip(("estimate", "ci_lo", "ci_hi"), _boot(d, med, cluster, boot, seed, 0.95)))
    out["median_lifetime_bounds"] = dict(zip(("lower_open_as_observed", "upper_open_as_infinite"), median_lifetime_bounds(d, weight)))
    # H1 (mediana L <= T_L) jest równoważna temu, że udział reklam z L <= T_L wynosi co najmniej 50%
    sl = lambda x: weighted_share_at_least(-x["lifetime_days"], x[weight], -thr_days)
    out["share_lifetime_le_threshold"] = dict(zip(("estimate", "ci_lo", "ci_hi"), _boot(d, sl, cluster, boot, seed, 0.95)))
    if "intensity_per_day" in d:
        sh = lambda x: weighted_share_at_least(x["intensity_per_day"], x[weight], thr_intensity)
        out["share_intensity_ge_threshold"] = dict(zip(("estimate", "ci_lo", "ci_hi"), _boot(d, sh, cluster, boot, seed, 0.95)))
        out["median_intensity_per_day"] = weighted_quantile(d["intensity_per_day"], d[weight], 0.5)
        out["median_reach_total"] = weighted_quantile(d["reach_total"], d[weight], 0.5) if "reach_total" in d else None
    out["params"] = {"thr_days": thr_days, "thr_intensity": thr_intensity, "min_share": min_share}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("csv")
    ap.add_argument("--class-col", help="kolumna 0/1: przynależność do populacji badanej (gold albo predykcja)")
    ap.add_argument("--weight-col", default="weight")
    ap.add_argument("--cluster", default="advertiser_id")
    ap.add_argument("--reach-col", default="reach_total")
    ap.add_argument("--thr-days", type=float, default=2)
    ap.add_argument("--thr-intensity", type=float, default=25000)
    ap.add_argument("--min-share", type=float, default=0.5)
    ap.add_argument("--boot", type=int, default=500)
    a = ap.parse_args()
    df = pd.read_csv(a.csv)
    if a.class_col:
        df = df[df[a.class_col] == 1]
    d = compute_outcomes(df, reach=a.reach_col)
    print(json.dumps(summarize(d, a.thr_days, a.thr_intensity, a.min_share, a.weight_col, a.cluster, a.boot), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
