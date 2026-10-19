"""Związek w czasie między dwoma szeregami: X (Telegram, kanały prorosyjskie lub proukraińskie) i Y (polskojęzyczny X).

Hipoteza projektu: trendy negatywnych treści o ukraińskich uchodźcach w Y są dodatnio skorelowane z trendami
w źródłach prorosyjskich. Test główny: `xcorr_test(..., min_lag=0, max_lag=7, positive=True)` na dziennych
przyrostach oraz `weekly_trend_corr` na tygodniowych przyrostach. Pozostałe miary są uzupełniające (kierunek):
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


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a - a.mean(), b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else float("nan")


def _xcorr_d(dx: pd.Series, dy: pd.Series, max_lag: int) -> pd.Series:
    """r(k) = corr(dX_{t-k}, dY_t); k > 0: X wcześniej. Równoważne dy.corr(dx.shift(k)), liczone w numpy."""
    a, b = np.asarray(dx, float), np.asarray(dy, float)
    n = len(a)
    out = {}
    for k in range(-max_lag, max_lag + 1):
        out[k] = _corr(a[: n - k], b[k:]) if k >= 0 else _corr(a[-k:], b[: n + k])
    return pd.Series(out, name="r")


def xcorr(x: pd.Series, y: pd.Series, max_lag: int = 14) -> pd.Series:
    """corr(dX_{t-k}, dY_t) dla k = -max_lag..max_lag, gdzie d = przyrost log(1+·)."""
    dx, dy = _prep(x).align(_prep(y), join="inner")
    return _xcorr_d(dx, dy, max_lag)


def xcorr_test(x: pd.Series, y: pd.Series, max_lag: int = 14, n_perm: int = 500, seed: int = 0,
               min_lag: int | None = None, positive: bool = False) -> dict:
    """Maksimum |r| (albo r, gdy positive=True) po opóźnieniach k z [min_lag, max_lag] vs rozkład zerowy
    z kołowych przesunięć przyrostów X. Test hipotezy: min_lag=0, max_lag=7, positive=True (korelacja dodatnia,
    jednoczesna albo z Telegramem o 0-7 dni wcześniej). Maksimum po k jest wliczone w rozkład zerowy, więc
    przeszukiwanie kilku opóźnień nie zawyża istotności.

    Przesuwamy przyrosty, nie poziomy: przesunięcie poziomów z trendem tworzy na „szwie” skok,
    który zaniża korelacje w rozkładzie zerowym (test byłby zbyt liberalny).
    """
    lo = -max_lag if min_lag is None else min_lag
    dx, dy = _prep(x).align(_prep(y), join="inner")
    stat = (lambda rr: rr.loc[lo:max_lag].max()) if positive else (lambda rr: rr.loc[lo:max_lag].abs().max())
    r = _xcorr_d(dx, dy, max_lag)
    sub = r.loc[lo:max_lag]
    k_best = int(sub.idxmax() if positive else sub.abs().idxmax())
    obs = float(stat(r))
    rng = np.random.default_rng(seed)
    n = len(dx)
    null = []
    for _ in range(n_perm):
        shift = int(rng.integers(max_lag + 1, n - max_lag - 1))
        dxs = pd.Series(np.roll(dx.to_numpy(), shift), index=dx.index)
        null.append(float(stat(_xcorr_d(dxs, dy, max_lag))))
    p = (1 + sum(v >= obs for v in null)) / (n_perm + 1)
    return {"best_lag": k_best, "r_best": float(r.loc[k_best]), "r_lag0": float(r.loc[0]), "p_perm_max_abs_r": float(p),
            "lag_range": [lo, max_lag], "one_sided_positive": positive, "r_by_lag": r.round(4).to_dict()}


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


def weekly_trend_corr(x: pd.Series, y: pd.Series, n_perm: int = 2000, seed: int = 0) -> dict:
    """Korelacja trendów tygodniowych: Spearman między tygodniowymi przyrostami log(1+suma tygodnia) X i Y.

    Przyrosty (zamiast poziomów) usuwają wspólny trend długookresowy: dwa szeregi, które oba maleją w roku,
    mają wysoką korelację poziomów bez żadnego związku. p: test permutacyjny z kołowych przesunięć przyrostów X
    (jednostronny, H1: rho > 0). Zwraca też rho poziomów dla porównania (bez testu).
    """
    wx = x.resample("W-SUN").sum()
    wy = y.resample("W-SUN").sum()
    wx, wy = wx.align(wy, join="inner")
    dx, dy = np.log1p(wx.astype(float)).diff().dropna(), np.log1p(wy.astype(float)).diff().dropna()
    rho = float(dx.rank().corr(dy.rank()))
    rng = np.random.default_rng(seed)
    n = len(dx)
    null = [float(pd.Series(np.roll(dx.to_numpy(), int(rng.integers(2, n - 1))), index=dx.index).rank().corr(dy.rank()))
            for _ in range(n_perm)]
    p = (1 + sum(v >= rho for v in null)) / (n_perm + 1)
    return {"n_weeks": int(n), "rho_changes": rho, "p_perm_one_sided": float(p),
            "rho_levels_no_test": float(wx.rank().corr(wy.rank()))}


def simulate_correlated(rho: float, n_days: int = 303, lag: int = 2, base: float = 60, sigma: float = 0.35,
                        seed: int = 0):
    """Dwa szeregi liczności (Poisson), których log-poziomy dzielą wspólny składnik: corr(u_x[t-lag], u_y[t]) = rho.

    Do szacowania mocy testu głównego; szum Poissona dodatkowo osłabia obserwowaną korelację, jak w danych.
    """
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_days + lag)
    ux = np.sqrt(rho) * s[lag:] + np.sqrt(1 - rho) * rng.standard_normal(n_days)
    uy = np.sqrt(rho) * s[:n_days] + np.sqrt(1 - rho) * rng.standard_normal(n_days)
    idx = pd.date_range("2022-03-04", periods=n_days, freq="D")
    x = rng.poisson(base * np.exp(sigma * ux))
    y = rng.poisson(base * np.exp(sigma * uy))
    return pd.Series(x, idx), pd.Series(y, idx)


def power_xcorr(rho: float, reps: int = 100, alpha: float = 0.05, n_perm: int = 199, base: float = 60,
                seed: int = 0) -> float:
    """Moc testu głównego (dzienne przyrosty, k = 0..7, jednostronnie) przy prawdziwej korelacji rho i opóźnieniu 2 dni."""
    hits = 0
    for r in range(reps):
        x, y = simulate_correlated(rho, base=base, seed=seed + r)
        hits += xcorr_test(x, y, max_lag=7, min_lag=0, positive=True, n_perm=n_perm, seed=r)["p_perm_max_abs_r"] < alpha
    return hits / reps


def control_difference(x_ru: pd.Series, x_ua: pd.Series, y: pd.Series, min_lag: int = 0, max_lag: int = 7,
                       block: int = 7, n_boot: int = 2000, seed: int = 0) -> dict:
    """Różnica max_k r_RU(k) - max_k r_UA(k) z blokowym bootstrapem dni (kryterium (c) reguły decyzyjnej).

    Losujemy ze zwracaniem bloki `block` kolejnych dni docelowych t (wspólnie dla RU i UA) i dla każdego k bierzemy
    pary (dX_{t-k}, dY_t) z oryginalnej serii. Pary z opóźnieniem nie przechodzą więc przez granice bloków,
    a autokorelacja w bloku i powiązanie RU/UA z tym samym dniem t są zachowane. Zwraca 95% przedział percentylowy.
    """
    d = pd.concat([_prep(x_ru), _prep(x_ua), _prep(y)], axis=1, join="inner").to_numpy()
    n = len(d)
    t_all = np.arange(max_lag, n)                     # dni docelowe, dla których istnieje każde t-k
    ks = range(min_lag, max_lag + 1)

    def stat(t: np.ndarray) -> float:
        yy = d[t, 2]
        r_ru = max(_corr(d[t - k, 0], yy) for k in ks)
        r_ua = max(_corr(d[t - k, 1], yy) for k in ks)
        return r_ru - r_ua

    obs = stat(t_all)
    rng = np.random.default_rng(seed)
    m = len(t_all)
    n_blocks = int(np.ceil(m / block))
    diffs = []
    for _ in range(n_boot):
        starts = rng.integers(0, m - block + 1, size=n_blocks)
        idx = np.concatenate([t_all[s: s + block] for s in starts])[:m]
        diffs.append(stat(idx))
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    return {"diff": float(obs), "ci95": [float(lo), float(hi)], "block_days": block, "n_boot": n_boot,
            "ci_above_zero": bool(lo > 0)}


def test_hypothesis(x_ru: pd.Series, x_ua: pd.Series, y: pd.Series, n_perm: int = 1000, seed: int = 0) -> dict:
    """Cały test hipotezy H (karta, sekcja 4; METODY.md §4): test główny dla RU i UA, test tygodniowy, różnica RU-UA.

    Wejście: dzienne liczności na wspólnym indeksie dat (np. `series.daily_series(...)["anti_contents"]` dla X
    i `telegram.side_series(..., col="n_topic_anti")` dla stron Telegrama).
    """
    main_ru = xcorr_test(x_ru, y, max_lag=7, min_lag=0, positive=True, n_perm=n_perm, seed=seed)
    main_ua = xcorr_test(x_ua, y, max_lag=7, min_lag=0, positive=True, n_perm=n_perm, seed=seed)
    week_ru = weekly_trend_corr(x_ru, y, n_perm=2000, seed=seed)
    diff = control_difference(x_ru, x_ua, y, seed=seed)
    a = main_ru["p_perm_max_abs_r"] < 0.05
    b = np.sign(week_ru["rho_changes"]) == np.sign(main_ru["r_best"])
    c = diff["ci_above_zero"]
    return {"main_ru": main_ru, "main_ua": main_ua, "weekly_ru": week_ru, "ru_minus_ua": diff,
            "criteria": {"a_main_p_lt_005": bool(a), "b_weekly_same_sign": bool(b), "c_ru_gt_ua": bool(c)},
            "supported": bool(a and b and c),
            "note": "wariant na udziałach (kryterium b) uruchamia się tą samą funkcją z udziałami zamiast liczności"}
