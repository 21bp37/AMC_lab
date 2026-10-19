"""Dzienne szeregi czasowe i wykrywanie peaków.

Szeregi (definicje pomiarowe; „dzień” = doba kalendarzowa Europe/Warsaw):
- rows          : wszystkie wiersze (oryginały + retweety + odpowiedzi),
- authored      : oryginały + odpowiedzi (treść pisana, bez kaskad RT),
- cascades      : liczba różnych kaskad aktywnych danego dnia (odporne na jeden wiralowy wpis),
- negative      : wiersze z etykietą sentymentu „negative”,
- anti_lex      : wiersze z trafieniem w leksykon narracji antyukraińskich (eksploracyjnie),
- pro_lex       : wiersze z trafieniem w leksykon treści proukraińskich,
- neg_anti      : negatywny sentyment ORAZ leksykon anty-UA (przybliżenie „negatywnych wobec Ukraińców”),
- pos_pro       : pozytywny sentyment ORAZ leksykon pro-UA,
- *_share       : udziały w `rows`.

Peak: dzień, w którym log(1+x) przekracza kroczącą medianę (okno `window`, wycentrowane)
o więcej niż `z` odporne odchylenia (1.4826·MAD) i jest lokalnym maksimum w ±`sep` dni.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def daily_series(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    idx = pd.date_range(start, end, freq="D")
    g = df.groupby("day")
    out = pd.DataFrame({
        "rows": g.size(),
        "authored": df[df["type"] != "retweet"].groupby("day").size(),
        "cascades": g["cascade_key"].nunique(),
        "negative": df[df["negative"]].groupby("day").size(),
        "anti_lex": df[df["anti_ua_lexicon"]].groupby("day").size(),
        "negative_authored": df[df["negative"] & (df["type"] != "retweet")].groupby("day").size(),
        "pro_lex": df[df["pro_ua_lexicon"]].groupby("day").size(),
        "neg_anti": df[df["negative"] & df["anti_ua_lexicon"]].groupby("day").size(),
        "pos_pro": df[df["positive"] & df["pro_ua_lexicon"]].groupby("day").size(),
    }).reindex(idx).fillna(0).astype(int)
    out.index.name = "day"
    out["negative_share"] = out["negative"] / out["rows"].replace(0, np.nan)
    out["anti_lex_share"] = out["anti_lex"] / out["rows"].replace(0, np.nan)
    return out


def robust_z(x: pd.Series, window: int = 15) -> pd.Series:
    lx = np.log1p(x.astype(float))
    med = lx.rolling(window, center=True, min_periods=window // 2).median()
    mad = (lx - med).abs().rolling(window, center=True, min_periods=window // 2).median()
    scale = (1.4826 * mad).replace(0, np.nan)
    floor = float(np.nanmedian(scale)) if np.isfinite(np.nanmedian(scale)) else 1.0
    return (lx - med) / scale.fillna(floor).clip(lower=floor * 0.5)


def detect_peaks(x: pd.Series, z: float = 3.0, window: int = 15, sep: int = 3) -> pd.DatetimeIndex:
    zs = robust_z(x, window)
    local_max = x == x.rolling(2 * sep + 1, center=True, min_periods=1).max()
    return x.index[(zs > z) & local_max & (x > 0)]


def peak_table(df: pd.DataFrame, series: pd.Series, peaks: pd.DatetimeIndex, events: dict | None = None) -> pd.DataFrame:
    """Opis peaków: wielkość, koncentracja na jednej kaskadzie/koncie, udział negatywnych, najbliższe wydarzenie."""
    events = {pd.Timestamp(k): v for k, v in (events or {}).items()}
    rows = []
    for d in peaks:
        day = df[df["day"] == d]
        casc = day["cascade_key"].value_counts()
        src = day["source_author"].value_counts()
        near = [f"{v} ({(d - k).days:+d} d)" for k, v in events.items() if abs((d - k).days) <= 3]
        rows.append({
            "day": d.date(), "n": int(series.loc[d]),
            "top_source": src.index[0] if len(src) else "", "top_source_share": float(src.iloc[0] / len(day)) if len(day) else np.nan,
            "top_cascade_share": float(casc.iloc[0] / len(day)) if len(day) else np.nan,
            "negative_share": float(day["negative"].mean()) if len(day) else np.nan,
            "event": "; ".join(near),
        })
    return pd.DataFrame(rows)
