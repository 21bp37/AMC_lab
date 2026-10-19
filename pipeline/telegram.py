"""Filtrowanie zbioru „Russian and Ukrainian War-related Telegram Channels Dataset” do szeregów dziennych.

Zbiór ma ~79,6 mln postów w plikach post_texts_part_{n}.csv, więc nie ładujemy go do pandas:
DuckDB czyta pliki strumieniowo, filtruje wyrażeniem regularnym i agreguje po dniu i stronie kanału.

Wejście (ścieżki do lokalnej kopii zbioru, poza repozytorium):
    --posts    'dane/telegram/post_texts_part_*.csv'
    --clusters 'dane/telegram/leiden_clusters.csv'   (kolumny peer_id, side, cluster; 3 074 z 4 687 kanałów)
Wynik: data/processed/telegram_daily.csv  (day, side, n_posts, n_topic, views_topic, forwards_topic)

Filtr tematu (config.TELEGRAM_UA i TELEGRAM_PL): wzmianka o Ukrainie/Ukraińcach ORAZ o Polsce/Polakach.
Kanały bez etykiety Leidena dostają side = 'unlabeled' (raportujemy je osobno, nie wyrzucamy po cichu).

Użycie:
    python -m pipeline.telegram --posts '…/post_texts_part_*.csv' --clusters '…/leiden_clusters.csv'
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pipeline import config

SQL = """
WITH posts AS (
    SELECT peer_id, CAST(date AS TIMESTAMP) AS ts, message, TRY_CAST(views AS BIGINT) AS views,
           TRY_CAST(forwards AS BIGINT) AS forwards
    FROM read_csv_auto(?, union_by_name = true, ignore_errors = true)
    WHERE CAST(date AS TIMESTAMP) BETWEEN CAST(? AS TIMESTAMP) AND CAST(? AS TIMESTAMP) + INTERVAL 1 DAY
),
labelled AS (
    SELECT p.*, COALESCE(c.side, 'unlabeled') AS side
    FROM posts p LEFT JOIN read_csv_auto(?) c ON p.peer_id = c.peer_id
),
flagged AS (
    SELECT *, (regexp_matches(COALESCE(message, ''), ?) AND regexp_matches(COALESCE(message, ''), ?)) AS topic
    FROM labelled
)
SELECT CAST(date_trunc('day', ts AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Warsaw') AS DATE) AS day, side,
       COUNT(*) AS n_posts,
       SUM(CASE WHEN topic THEN 1 ELSE 0 END) AS n_topic,
       SUM(CASE WHEN topic THEN views ELSE 0 END) AS views_topic,
       SUM(CASE WHEN topic THEN forwards ELSE 0 END) AS forwards_topic
FROM flagged GROUP BY 1, 2 ORDER BY 1, 2
"""


def build_daily(posts_glob: str, clusters_csv: str, start: str = config.STUDY_START, end: str = config.STUDY_END) -> pd.DataFrame:
    import duckdb

    con = duckdb.connect()
    # Daty w zbiorze są w UTC; jeśli read_csv wczyta je jako TIMESTAMP bez strefy, traktujemy je jako UTC.
    con.execute("SET TimeZone = 'UTC'")
    df = con.execute(SQL, [posts_glob, start, end, clusters_csv, config.TELEGRAM_UA, config.TELEGRAM_PL]).df()
    df["day"] = pd.to_datetime(df["day"])
    return df


def side_series(daily: pd.DataFrame, side: str, col: str = "n_topic", start: str = config.STUDY_START,
                end: str = config.STUDY_END) -> pd.Series:
    idx = pd.date_range(start, end, freq="D")
    s = daily[daily["side"] == side].set_index("day")[col]
    return s.reindex(idx).fillna(0).astype(int)


def main() -> None:
    ap = argparse.ArgumentParser(description="Telegram -> dzienne szeregi tematu „Ukraińcy w Polsce”")
    ap.add_argument("--posts", required=True)
    ap.add_argument("--clusters", required=True)
    ap.add_argument("--out", default=str(config.PROCESSED / "telegram_daily.csv"))
    args = ap.parse_args()
    df = build_daily(args.posts, args.clusters)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(df.groupby("side")[["n_posts", "n_topic"]].sum())
    print(f"Zapisano {args.out}")


if __name__ == "__main__":
    main()
