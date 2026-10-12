"""Wczytanie JSON z TikTok Commercial Content Library / API do płaskiej tabeli zgodnej ze specyfikacją 03.

Struktura wejścia (ustalona na próbce pilotażowej): słownik {słowo_kluczowe: [reklama, ...]}; reklama ma sekcje
`advertiser`, `basic` (daty `first_shown_date`/`last_shown_date` jako RRRRMMDD, `status`, `status_statement`, adresy mediów),
`metrics` (`unique_users_seen` jako PRZEDZIAŁ tekstowy, np. "400K-500K", i rozbicia po krajach, wieku i płci) oraz `targeting`.

Ważne:
- `unique_users_seen` to liczba UNIKALNYCH UŻYTKOWNIKÓW (zasięg), nie wyświetleń, i jest podana jako przedział, więc
  zapisujemy `reach_min`, `reach_max` i `reach_total` (środek przedziału, tylko do prostych obliczeń).
- Adresów mediów (podpisane, wygasające linki CDN) NIE zapisujemy do tabeli; zapisujemy tylko flagi `has_video`, `has_image`.
  Pobieranie mediów wymaga zgody wynikającej z warunków źródła (D1, P04).
- Nazwy reklamodawców mogą być danymi osobowymi (jednoosobowe działalności): zapisujemy tylko `business_id`.
- Brak pola tekstu reklamy i adresu docelowego w tej strukturze.
- W próbce pilotażowej reklamy ze statusem `inactive` (usunięte przez TikTok) miały puste dane reklamodawcy i żadnych mediów:
  nie da się ich zaklasyfikować z kreacji ani przypisać do klastra (06, R23).

Użycie:
    python tools/load_tiktok_json.py plik.json --retrieval-date 2026-10-12 --out poza_repo/ads_flat.csv
Wynik zapisuj poza repozytorium (dane o reklamach nie wchodzą do repozytorium).
"""
from __future__ import annotations

import argparse
import json
import re

import pandas as pd

_MULT = {"": 1.0, "K": 1e3, "M": 1e6}


def _parse_number(token: str, default_suffix: str = "") -> float:
    m = re.fullmatch(r"\s*([\d.,]+)\s*([KkMm]?)\s*", token)
    if not m:
        raise ValueError(f"nie rozpoznano liczby: {token!r}")
    suffix = (m.group(2) or default_suffix).upper()
    return float(m.group(1).replace(",", ".")) * _MULT[suffix]


def parse_range(text: str) -> tuple[float, float]:
    """"400K-500K" -> (400000, 500000); "0-1K" -> (0, 1000); "480K" -> (480000, 480000)."""
    text = str(text).strip()
    if "-" not in text:
        v = _parse_number(text)
        return v, v
    lo_s, hi_s = [p.strip() for p in text.split("-", 1)]
    hi = _parse_number(hi_s)
    hi_suffix = re.search(r"[KkMm]$", hi_s)
    # dolna granica bez sufiksu dziedziczy sufiks górnej tylko, gdy jest niezerowa ("1K-10K": 1K; "0-1K": 0)
    lo_has_suffix = re.search(r"[KkMm]$", lo_s)
    lo = _parse_number(lo_s, hi_suffix.group(0) if (hi_suffix and not lo_has_suffix and float(lo_s.replace(",", ".")) > 0) else "")
    return lo, hi


def flatten(data: dict, retrieval_date: str) -> pd.DataFrame:
    rows = []
    for keyword, ads in data.items():
        for a in ads:
            basic, met, tg = a.get("basic", {}), a.get("metrics", {}), a.get("targeting", {})
            lo, hi = parse_range(met["unique_users_seen"]) if met.get("unique_users_seen") else (float("nan"),) * 2
            rows.append({
                "ad_id": str(a["ad_id"]), "creative_id": str(a["ad_id"]),
                "advertiser_id": str(a.get("advertiser", {}).get("business_id") or ""),   # tekst: 19-cyfrowe identyfikatory gubią precyzję jako liczby
                "platform": "tiktok", "source_name": "tiktok_commercial_content", "source_version": "json_pilot",
                "delivery_start": pd.to_datetime(basic.get("first_shown_date"), format="%Y%m%d", errors="coerce"),
                "delivery_stop": pd.to_datetime(basic.get("last_shown_date"), format="%Y%m%d", errors="coerce"),
                "retrieval_date": retrieval_date,
                "status": basic.get("status"), "status_statement": basic.get("status_statement"),
                "source_removed_flag": int(str(basic.get("status", "")).lower() == "inactive"
                                           and "removed" in str(basic.get("status_statement", "")).lower()),
                "reach_raw": met.get("unique_users_seen"), "reach_min": lo, "reach_max": hi, "reach_total": (lo + hi) / 2,
                "countries_seen": ",".join(met.get("unique_users_seen_by_country", {}).keys()),
                "targeted_raw": tg.get("number_of_users_targeted"),
                "targeting_countries": ",".join(tg.get("country", [])),
                "has_video": int(bool(basic.get("videos"))), "has_image": int(bool(basic.get("image_urls"))),
                "creative_available": int(bool(basic.get("videos") or basic.get("image_urls"))),
                "frame_source": keyword,
            })
    df = pd.DataFrame(rows)
    for c in ("delivery_start", "delivery_stop"):
        df[c] = df[c].dt.strftime("%Y-%m-%d")
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("json_path")
    ap.add_argument("--retrieval-date", required=True, help="data pobrania danych (RRRR-MM-DD); jest zmienną w analizie")
    ap.add_argument("--out", required=True, help="plik CSV poza repozytorium")
    a = ap.parse_args()
    with open(a.json_path, encoding="utf-8") as f:
        df = flatten(json.load(f), a.retrieval_date)
    df.to_csv(a.out, index=False)
    print(f"zapisano {len(df)} reklam, {df['advertiser_id'].nunique()} reklamodawców -> {a.out}")


if __name__ == "__main__":
    main()
