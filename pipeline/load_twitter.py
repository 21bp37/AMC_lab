"""Wczytanie eksportu NodeXL (X/Twitter, PL, 2022) do tabeli roboczej.

Co robi:
- mapuje nazwy kolumn NodeXL na nazwy robocze (config.TWITTER_COLUMNS),
- parsuje czas (UTC) i dzień kalendarzowy w strefie Europe/Warsaw (zjawisko dotyczy polskiej publiczności),
- rozróżnia typ wiersza: original / retweet / reply,
- dla retweetów odzyskuje autora źródłowego (`source_author`) i klucz kaskady (`cascade_key`),
- dodaje flagi tematu i leksykonu narracji (wersja eksploracyjna),
- sprawdza jakość: duplikaty ID, braki, zakres dat.

Użycie:
    python -m pipeline.load_twitter [--input ścieżka.csv]
Wynik: data/processed/twitter.csv.gz (poza repozytorium) + raport jakości na stdout.
"""
from __future__ import annotations

import argparse
import json
import re

import numpy as np
import pandas as pd

from pipeline import config

RT_PREFIX = re.compile(r"^RT @(\w+):\s*")


def load_raw(path=config.RAW_TWITTER) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"Imported ID": "string", "Conversation ID": "string",
                                  "In Reply To Tweet ID": "string", "Retweet ID": "string", "Author ID": "string"})
    missing = [c for c in config.TWITTER_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Brak kolumn w eksporcie NodeXL: {missing}")
    return df[list(config.TWITTER_COLUMNS)].rename(columns=config.TWITTER_COLUMNS)


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ts"] = pd.to_datetime(out["ts"], utc=True)
    out["day"] = out["ts"].dt.tz_convert("Europe/Warsaw").dt.tz_localize(None).dt.floor("D")
    out["type"] = out["relationship"].map({"Tweet": "original", "Retweet": "retweet", "Replies to": "reply"})
    if out["type"].isna().any():
        raise ValueError(f"Nieznane wartości relationship: {out.loc[out['type'].isna(), 'relationship'].unique()}")
    out["text"] = out["text"].fillna("")
    rt_src = out["text"].str.extract(RT_PREFIX, expand=False).str.lower()
    out["source_author"] = np.where(out["type"] == "retweet", rt_src.fillna(out["target"].str.lower()),
                                    out["author"].str.lower())
    out["clean_text"] = out["text"].str.replace(RT_PREFIX, "", regex=True)
    # Kaskada = treść źródłowa; dla RT ID oryginału bywa puste, więc kluczem jest autor + początek tekstu
    out["cascade_key"] = out["source_author"] + "|" + out["clean_text"].str.lower().str[:80]
    out["truncated"] = out["text"].str.endswith("…")
    low = out["clean_text"].str.lower()
    out["topic_ua"] = low.str.contains(config.TOPIC_UA)
    out["topic_pl"] = low.str.contains(config.TOPIC_PL)
    out["topic_both"] = out["topic_ua"] & out["topic_pl"]
    for name, pattern in config.ANTI_UA_NARRATIVES.items():
        out[f"nar_{name}"] = low.str.contains(pattern, regex=True)
    nar_cols = [c for c in out.columns if c.startswith("nar_")]
    out["anti_ua_lexicon"] = out[nar_cols].any(axis=1)
    out["negative"] = out["sentiment"].eq("negative")
    return out


def quality_report(df: pd.DataFrame) -> dict:
    by_day = df.groupby("day").size()
    eff = by_day[by_day.index >= config.EFFECTIVE_START]
    return {
        "n_rows": int(len(df)),
        "n_by_type": df["type"].value_counts().to_dict(),
        "duplicate_tweet_id": int(df["tweet_id"].duplicated().sum()),
        "n_authors": int(df["author"].nunique()),
        "n_unique_texts": int(df["clean_text"].nunique()),
        "n_cascades": int(df["cascade_key"].nunique()),
        "ts_min": str(df["ts"].min()), "ts_max": str(df["ts"].max()),
        "n_days": int(by_day.size),
        "rows_before_effective_start": int((df["day"] < config.EFFECTIVE_START).sum()),
        "median_daily_rows_effective": float(eff.median()),
        "share_truncated_rt": float(df.loc[df["type"] == "retweet", "truncated"].mean()),
        "share_topic_both_original": float(df.loc[df["type"] == "original", "topic_both"].mean()),
        "share_topic_ua": float(df["topic_ua"].mean()),
        "sentiment_dist": df["sentiment"].value_counts(normalize=True).round(4).to_dict(),
        "share_sentiment_score_gt_0_95": float((df["sentiment_score"] > 0.95).mean()),
        "share_anti_ua_lexicon": float(df["anti_ua_lexicon"].mean()),
        "missing_share": {c: float(df[c].isna().mean()) for c in ["sentiment", "text", "author"]},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", default=str(config.RAW_TWITTER))
    args = ap.parse_args()
    df = normalize(load_raw(args.input))
    config.PROCESSED.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED / "twitter.csv.gz"
    df.to_csv(out, index=False)
    print(json.dumps(quality_report(df), ensure_ascii=False, indent=2, default=str))
    print(f"Zapisano {out}")


if __name__ == "__main__":
    main()
