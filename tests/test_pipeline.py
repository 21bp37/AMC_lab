"""Testy pipeline'u na danych syntetycznych (bez prawdziwych postów)."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import config, leadlag, series  # noqa: E402
from pipeline.load_twitter import normalize  # noqa: E402


def fake_nodexl(n=6):
    base = {v: [None] * n for v in config.TWITTER_COLUMNS.values()}
    df = pd.DataFrame(base)
    df["tweet_id"] = [str(i) for i in range(n)]
    df["author"] = ["a", "b", "c", "d", "a", "e"][:n]
    df["target"] = ["a", "x", "c", "x", "a", "c"][:n]
    df["relationship"] = ["Tweet", "Retweet", "Replies to", "Retweet", "Tweet", "Replies to"][:n]
    df["ts"] = ["2022-05-09 22:30:00", "2022-05-10 08:00:00", "2022-05-10 09:00:00",
                "2022-05-10 10:00:00", "2022-05-11 10:00:00", "2022-05-11 11:00:00"][:n]
    df["text"] = ["Ukraińcy w Polsce dostają 500+", "RT @X: Ukraińcy w Polsce …", "a Polacy?",
                  "RT @X: Ukraińcy w Polsce …", "wdzięczni Ukraińcy w Polsce", "banderowcy"][:n]
    df["sentiment"] = ["negative", "neutral", "negative", "neutral", "positive", "negative"][:n]
    df["sentiment_score"] = 0.99
    return df


class TestLoad(unittest.TestCase):
    def setUp(self):
        self.df = normalize(fake_nodexl())

    def test_types_and_rt_source(self):
        self.assertEqual(self.df["type"].tolist(), ["original", "retweet", "reply", "retweet", "original", "reply"])
        self.assertEqual(self.df.loc[1, "source_author"], "x")
        self.assertEqual(self.df.loc[1, "cascade_key"], self.df.loc[3, "cascade_key"])  # ten sam RT = jedna kaskada

    def test_day_in_warsaw_time(self):
        # 22:30 UTC 9 maja = 00:30 10 maja w Warszawie (CEST)
        self.assertEqual(str(self.df.loc[0, "day"].date()), "2022-05-10")

    def test_lexicon_no_false_positive_on_gratitude(self):
        self.assertTrue(self.df.loc[0, "anti_ua_lexicon"])      # 500+
        self.assertFalse(self.df.loc[4, "anti_ua_lexicon"])     # „wdzięczni” nie jest narracją
        self.assertTrue(self.df.loc[5, "nar_banderyzm"])

    def test_daily_series_fills_gaps(self):
        d = series.daily_series(self.df, "2022-05-08", "2022-05-12")
        self.assertEqual(len(d), 5)
        self.assertEqual(int(d.loc["2022-05-08", "rows"]), 0)
        self.assertEqual(int(d.loc["2022-05-10", "cascades"]), 3)  # oryginał (00:30 PL) + reply + RT; dwa RT = jedna kaskada


class TestPeaks(unittest.TestCase):
    def test_detects_injected_spikes(self):
        rng = np.random.default_rng(0)
        idx = pd.date_range("2022-03-01", periods=200)
        x = pd.Series(rng.poisson(100, 200), idx)
        x.iloc[[50, 120]] = 600
        found = series.detect_peaks(x, z=3.0)
        self.assertTrue({idx[50], idx[120]} <= set(found))
        self.assertLessEqual(len(found), 4)


class TestLeadLag(unittest.TestCase):
    def test_xcorr_recovers_known_lag(self):
        x, y, _ = leadlag.simulate_series(n_events=12, lag=3, jitter=0, seed=1)
        r = leadlag.xcorr_test(x, y, max_lag=10, n_perm=99)
        self.assertEqual(r["best_lag"], 3)
        self.assertLess(r["p_perm_max_abs_r"], 0.05)

    def test_xcorr_null_calibrated(self):
        # niezależne szeregi: odsetek p < 0,05 bliski 5% (tolerancja na 30 powtórzeń)
        ps = []
        for s in range(30):
            x, _, _ = leadlag.simulate_series(n_events=12, seed=100 + s)
            _, y, _ = leadlag.simulate_series(n_events=12, seed=200 + s)
            ps.append(leadlag.xcorr_test(x, y, max_lag=10, n_perm=99, seed=s)["p_perm_max_abs_r"])
        self.assertLessEqual(np.mean(np.array(ps) < 0.05), 0.2)

    def test_peak_lags(self):
        xp = pd.to_datetime(["2022-03-01", "2022-03-20"])
        yp = pd.to_datetime(["2022-03-04", "2022-03-20", "2022-04-30"])
        self.assertEqual(leadlag.peak_lags(xp, yp, max_lag=7), [3, 0, None])

    def test_peak_lag_test_detects_following(self):
        x, y, _ = leadlag.simulate_series(n_events=12, lag=3, jitter=0, seed=4)
        res = leadlag.peak_lag_test(series.detect_peaks(x), series.detect_peaks(y), x.index, n_perm=199)
        self.assertEqual(res["median_lag"], 3)
        self.assertLess(res["p_perm_share"], 0.05)

    def test_granger_direction(self):
        x, y, _ = leadlag.simulate_series(n_events=15, lag=2, jitter=0, seed=5)
        g = leadlag.granger_min_p(x, y, max_lag=4)
        self.assertLess(g["x_to_y"]["p"], g["y_to_x"]["p"])


class TestTelegram(unittest.TestCase):
    def test_duckdb_filter_and_side_join(self):
        try:
            import duckdb  # noqa: F401
        except ImportError:
            self.skipTest("brak duckdb")
        from pipeline import telegram

        with tempfile.TemporaryDirectory() as d:
            pd.DataFrame({
                "id": [1, 2, 3, 4], "peer_id": [10, 10, 20, 30],
                "date": ["2022-03-05 10:00:00", "2022-03-05 11:00:00", "2022-03-06 10:00:00", "2022-03-06 12:00:00"],
                "message": ["Украинцы в Польше получают пособия", "погода", "Українці у Польщі", "украинцы в Польше"],
                "views": [100, 5, 50, 7], "forwards": [3, 0, 1, 0], "edit_date": [None] * 4,
            }).to_csv(Path(d) / "post_texts_part_1.csv", index=False)
            pd.DataFrame({"peer_id": [10, 20], "side": ["Pro-Russian", "Pro-Ukrainian"], "cluster": [1, 2]}).to_csv(
                Path(d) / "leiden.csv", index=False)
            daily = telegram.build_daily(str(Path(d) / "post_texts_part_*.csv"), str(Path(d) / "leiden.csv"))
        ru = telegram.side_series(daily, "Pro-Russian")
        self.assertEqual(int(ru.loc["2022-03-05"]), 1)
        self.assertEqual(int(daily.loc[daily["side"] == "Pro-Russian", "n_posts"].sum()), 2)
        self.assertEqual(int(telegram.side_series(daily, "unlabeled").sum()), 1)  # kanał bez etykiety nie znika
        self.assertEqual(int(telegram.side_series(daily, "Pro-Ukrainian").sum()), 1)


if __name__ == "__main__":
    unittest.main()
