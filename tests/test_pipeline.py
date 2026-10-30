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
        self.assertTrue(self.df.loc[4, "pro_ua_lexicon"])      # wdzięczność = treść pro-UA
        self.assertEqual(self.df.loc[4, "stance_lex"], "pro")

    def test_negated_gratitude_is_anti_not_pro(self):
        raw = fake_nodexl()
        raw.loc[0, "text"] = "Ukraińcy w Polsce liczą pieniądze od podatnika. Nie widać wdzięczności."
        df = normalize(raw)
        self.assertFalse(df.loc[0, "pro_ua_lexicon"])
        self.assertTrue(df.loc[0, "anti_ua_lexicon"])
        self.assertEqual(df.loc[0, "stance_lex"], "anti")

    def test_daily_series_fills_gaps(self):
        d = series.daily_series(self.df, "2022-05-08", "2022-05-12")
        self.assertEqual(len(d), 5)
        self.assertEqual(int(d.loc["2022-05-08", "rows"]), 0)
        self.assertEqual(int(d.loc["2022-05-10", "cascades"]), 3)
        self.assertEqual(int(d.loc["2022-05-10", "anti_contents"]), 1)   # „500+” (00:30 czasu PL)
        self.assertEqual(int(d.loc["2022-05-11", "anti_contents"]), 1)   # „banderowcy”  # oryginał (00:30 PL) + reply + RT; dwa RT = jedna kaskada


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

    def test_main_test_one_sided_lag_range(self):
        x, y = leadlag.simulate_correlated(0.5, lag=2, seed=3)
        r = leadlag.xcorr_test(x, y, max_lag=7, min_lag=0, positive=True, n_perm=199)
        self.assertEqual(r["lag_range"], [0, 7])
        self.assertEqual(r["best_lag"], 2)
        self.assertLess(r["p_perm_max_abs_r"], 0.05)
        # odwrotny kierunek (Y wcześniej o 2 dni) jest poza zakresem 0..7, więc test nie powinien go nagrodzić
        r2 = leadlag.xcorr_test(y, x, max_lag=7, min_lag=0, positive=True, n_perm=199)
        self.assertGreater(r2["p_perm_max_abs_r"], 0.05)

    def test_weekly_trend_corr_detects_and_ignores_common_trend(self):
        x, y = leadlag.simulate_correlated(0.6, lag=0, seed=5)
        self.assertLess(leadlag.weekly_trend_corr(x, y, n_perm=499)["p_perm_one_sided"], 0.05)
        # dwa niezależne szeregi z tym samym trendem spadkowym: poziomy skorelowane, przyrosty nie
        idx = pd.date_range("2022-03-04", periods=303)
        rng = np.random.default_rng(0)
        trend = np.linspace(200, 50, 303)
        a, b = pd.Series(rng.poisson(trend), idx), pd.Series(rng.poisson(trend), idx)
        res = leadlag.weekly_trend_corr(a, b, n_perm=499)
        self.assertGreater(res["rho_levels_no_test"], 0.8)
        self.assertGreater(res["p_perm_one_sided"], 0.05)

    def test_control_difference_and_full_test(self):
        x_ru, y = leadlag.simulate_correlated(0.5, lag=2, seed=1)
        _, x_ua = leadlag.simulate_correlated(0.0, lag=2, seed=9)          # niezwiązany z y
        d = leadlag.control_difference(x_ru, x_ua, y, n_boot=300)
        self.assertTrue(d["ci_above_zero"])
        self.assertFalse(leadlag.control_difference(x_ua, x_ru, y, n_boot=300)["ci_above_zero"])
        res = leadlag.test_hypothesis(x_ru, x_ua, y, n_perm=199)
        self.assertTrue(res["supported"])
        res0 = leadlag.test_hypothesis(x_ua, x_ru, y, n_perm=199)        # zamienione strony: H nie powinna przejść
        self.assertFalse(res0["supported"])

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
        # „получают пособия” = narracja anty-UA; pozostałe posty z tematem jej nie mają
        self.assertEqual(int(telegram.side_series(daily, "Pro-Russian", col="n_topic_anti").sum()), 1)
        self.assertEqual(int(telegram.side_series(daily, "Pro-Ukrainian", col="n_topic_anti").sum()), 0)


class TestTelegramEda(unittest.TestCase):
    def test_side_stats_without_writing_outputs(self):
        from pipeline import eda_telegram as et

        with tempfile.TemporaryDirectory() as d:
            pd.DataFrame({
                "id": [1, 2, 3, 4, 5], "peer_id": [10, 10, 20, 30, 10],
                "date": ["2022-03-05T10:00:00Z", "2022-03-05T11:00:00Z", "2022-03-06T10:00:00Z",
                         "2022-03-06T12:00:00Z", "2021-01-01T10:00:00Z"],
                "message": ["Украинцы в Польше получают пособия", "Украинцы в Польше получают пособия", "Українці у Польщі",
                            "украинцы в Польше", "Украинцы в Польше"],
                "views": [100, 5, 50, 7, 1], "forwards": [3, 0, 1, 0, 0],
            }).to_csv(Path(d) / "posts_2022_part_1.csv", index=False)
            pd.DataFrame({"peer_id": [10, 20], "side": ["Pro-Russian", "Pro-Ukrainian"], "cluster": [1, 2]}).to_csv(
                Path(d) / "cl.csv", index=False)
            raw, parts = et.load_posts(str(Path(d) / "posts_2022_part_*.csv"))
            df = et.prepare(raw, str(Path(d) / "cl.csv"))
        self.assertEqual(parts, [1])
        self.assertEqual(len(df), 4)                       # post z 2021 poza oknem
        daily = et.daily_by_side(df)
        ss = et.side_stats(df, daily)
        self.assertEqual(ss["Pro-Russian"]["posts"], 2)
        self.assertEqual(ss["Pro-Russian"]["anti_posts"], 2)
        self.assertEqual(ss["Pro-Russian"]["copy_share"], 0.5)   # drugi post to powtórzony tekst
        self.assertEqual(ss["unlabeled"]["posts"], 1)            # kanał bez etykiety nie znika
        self.assertEqual(ss["Pro-Ukrainian"]["anti_posts"], 0)


if __name__ == "__main__":
    unittest.main()
