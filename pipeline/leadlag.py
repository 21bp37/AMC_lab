"""Opóźnienie między dwoma dziennymi szeregami (źródło X, np. Telegram prorosyjski -> odbiorca Y, np. polski X).

Trzy uzupełniające się miary (H1: X wyprzedza Y; H2: opóźnienie jest w przybliżeniu stałe):
1. `xcorr`         : korelacja krzyżowa przyrostów log(1+x); k > 0 oznacza, że X wyprzedza Y o k dni.
                     Różnicowanie usuwa wspólny trend (oba szeregi rosną/opadają z ogólnym zainteresowaniem wojną),
                     który inaczej daje pozorną korelację przy każdym opóźnieniu.
2. `peak_lags`     : dla każdego peaku Y najbliższy wcześniejszy (lub równoczesny) peak X w oknie `max_lag`;
                     rozkład tych opóźnień testuje „stałość” (mały rozrzut = stałe opóźnienie).
3. `granger_min_p` : test przyczynowości Grangera X -> Y i Y -> X (kierunek, nie mechanizm).

Istotność 1 i 2: test permutacyjny przez kołowe przesunięcia X (zachowuje autokorelację i liczbę peaków).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _prep(s: pd.Series) -> pd.Series:
    return np.log1p(s.astype(float)).diff().dropna()


def _xcorr_d(dx: pd.Series, dy: pd.Series, max_lag: int) -> pd.Series:
    return pd.Series({k: dy.corr(dx.shift(k)) for k in range(-max_lag, max_lag + 1)}, name="r")


def xcorr(x: pd.Series, y: pd.Series, max_lag: int = 14) -> pd.Series:
    """corr(dX_{t-k}, dY_t) dla k = -max_lag..max_lag, gdzie d = przyrost log(1+·)."""
    dx, dy = _prep(x).align(_prep(y), join="inner")
    return _xcorr_d(dx, dy, max_lag)


def xcorr_test(x: pd.Series, y: pd.Series, max_lag: int = 14, n_perm: int = 500, seed: int = 0) -> dict:
    """Maksimum |r| po opóźnieniach vs rozkład zerowy z kołowych przesunięć przyrostów X.

    Przesuwamy przyrosty, nie poziomy: przesunięcie poziomów z trendem tworzy na „szwie” skok,
    który zaniża korelacje w rozkładzie zerowym (test byłby zbyt liberalny).
    """
    dx, dy = _prep(x).align(_prep(y), join="inner")
    r = _xcorr_d(dx, dy, max_lag)
    k_best = int(r.abs().idxmax())
    obs = float(r.abs().max())
    rng = np.random.default_rng(seed)
    n = len(dx)
    null = []
    for _ in range(n_perm):
        shift = int(rng.integers(max_lag + 1, n - max_lag - 1))
        dxs = pd.Series(np.roll(dx.to_numpy(), shift), index=dx.index)
        null.append(float(_xcorr_d(dxs, dy, max_lag).abs().max()))
    p = (1 + sum(v >= obs for v in null)) / (n_perm + 1)
    return {"best_lag": k_best, "r_best": float(r.loc[k_best]), "p_perm_max_abs_r": float(p), "r_by_lag": r.round(4).to_dict()}


def peak_lags(x_peaks, y_peaks, max_lag: int = 7) -> list[int | None]:
    """Opóźnienie (dni) od najbliższego peaku X w [t-max_lag, t] do każdego peaku Y; None = brak dopasowania."""
    xp = pd.DatetimeIndex(x_peaks)
    out = []
    for t in pd.DatetimeIndex(y_peaks):
        d = (t - xp).days
        d = d[(d >= 0) & (d <= max_lag)]
        out.append(int(d.min()) if len(d) else None)
    return out


def peak_lag_test(x_peaks, y_peaks, index: pd.DatetimeIndex, max_lag: int = 7, n_perm: int = 1000, seed: int = 0) -> dict:
    lags = peak_lags(x_peaks, y_peaks, max_lag)
    matched = [v for v in lags if v is not None]
    share = len(matched) / len(lags) if lags else float("nan")
    pos = np.array([index.get_loc(p) for p in pd.DatetimeIndex(x_peaks)])
    n = len(index)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        sh = (pos + int(rng.integers(1, n))) % n
        l2 = peak_lags(index[np.sort(sh)], y_peaks, max_lag)
        null.append(np.mean([v is not None for v in l2]) if l2 else np.nan)
    p = (1 + sum(v >= share for v in null)) / (n_perm + 1)
    return {"n_y_peaks": len(lags), "n_matched": len(matched), "share_matched": share,
            "median_lag": float(np.median(matched)) if matched else None,
            "iqr_lag": (float(np.percentile(matched, 75) - np.percentile(matched, 25)) if matched else None),
            "p_perm_share": float(p), "lags": lags}


def granger_min_p(x: pd.Series, y: pd.Series, max_lag: int = 7) -> dict:
    from statsmodels.tsa.stattools import grangercausalitytests

    dx, dy = _prep(x), _prep(y)
    dx, dy = dx.align(dy, join="inner")
    res = {}
    for name, (a, b) in {"x_to_y": (dy, dx), "y_to_x": (dx, dy)}.items():
        data = pd.concat([a, b], axis=1).to_numpy()
        tests = grangercausalitytests(data, maxlag=max_lag)
        ps = {lag: float(t[0]["ssr_ftest"][1]) for lag, t in tests.items()}
        best = min(ps, key=ps.get)
        res[name] = {"best_lag": int(best), "p": ps[best], "p_by_lag": ps}
    return res


def simulate_series(n_days: int = 300, n_events: int = 10, lag: int = 3, jitter: int = 1, base_x: float = 200,
                    base_y: float = 130, amp: float = 3.0, follow: float = 1.0, seed: int = 0):
    """Para syntetycznych szeregów: zdarzenia w X i (z prawd. `follow`) w Y po `lag`±`jitter` dniach.

    Służy do testów i do szacowania mocy: czy przy tylu peakach, ile mamy w danych, wykryjemy opóźnienie.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-03-04", periods=n_days, freq="D")
    ev = np.sort(rng.choice(np.arange(10, n_days - 15), size=n_events, replace=False))
    sx, sy = np.zeros(n_days), np.zeros(n_days)
    for e in ev:
        sx[e:e + 3] += amp * np.array([1.0, 0.5, 0.2])
        if rng.random() < follow:
            t = e + lag + int(rng.integers(-jitter, jitter + 1))
            if t + 3 <= n_days:
                sy[t:t + 3] += amp * np.array([1.0, 0.5, 0.2])
    trend = np.linspace(1.0, 0.5, n_days)
    x = rng.poisson(base_x * trend * (1 + sx))
    y = rng.poisson(base_y * trend * (1 + sy))
    return pd.Series(x, idx), pd.Series(y, idx), idx[ev]


def power_peak_lag(n_events: int, lag: int = 3, follow: float = 0.7, reps: int = 100, alpha: float = 0.05,
                   max_lag: int = 7, z: float = 2.5, seed: int = 0) -> dict:
    """Moc testu dopasowania peaków (peak_lag_test) i trafność estymaty mediany opóźnienia."""
    from pipeline.series import detect_peaks

    hits, med = 0, []
    for r in range(reps):
        x, y, _ = simulate_series(n_events=n_events, lag=lag, follow=follow, seed=seed + r)
        px, py = detect_peaks(x, z=z), detect_peaks(y, z=z)
        if len(px) == 0 or len(py) == 0:
            continue
        res = peak_lag_test(px, py, x.index, max_lag=max_lag, n_perm=199, seed=r)
        hits += res["p_perm_share"] < alpha
        if res["median_lag"] is not None:
            med.append(res["median_lag"])
    return {"n_events": n_events, "lag": lag, "follow": follow, "power": hits / reps,
            "median_of_median_lag": float(np.median(med)) if med else None}
