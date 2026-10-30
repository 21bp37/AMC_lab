"""Testy wariantu wolumenowego (dane syntetyczne, bez sieci)."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import config, refugee_gate as g, refugee_volume as rv  # noqa: E402


def tw_frame(idx):
    rows = []
    for i, d in enumerate(idx):
        for j in range(3):
            t = "Ukraińcy dostają 500+ w Polsce" if j == 0 else "Ukraina dostała nowe czołgi"
            rows.append({"day": d, "clean_text": f"{t} {i}", "cascade_key": f"a{j}|{t}{i}"})
        rows.append({"day": d, "clean_text": "Ukraińcy dostają 500+ w Polsce", "cascade_key": f"a0|dup{i}"})
    return pd.DataFrame(rows)


def tg_frame(idx):
    rows = []
    for i, d in enumerate(idx):
        for side in ("Pro-Russian", "Pro-Ukrainian", "unlabeled"):
            rows.append({"day": d, "side": side, "message": f"Беженцы из Украины в Польше {i}", "copy_key": f"b{i}"})
            rows.append({"day": d, "side": side, "message": f"Танки для Украины от Польши {i}", "copy_key": f"t{i}"})
            rows.append({"day": d, "side": side, "message": f"Беженцы из Украины в Польше {i}", "copy_key": f"b{i}"})  # kopia
    return pd.DataFrame(rows)


class TestGate(unittest.TestCase):
    def test_gate_examples(self):
        self.assertTrue(g.telegram_about("Біженці з України в Польщі"))
        self.assertFalse(g.telegram_about("Танки для Украины от Польши"))
        self.assertFalse(g.telegram_about("вимушені переселенці на Донбасі"))
        self.assertTrue(g.x_about("Uchodźcy w Polsce"))
        self.assertFalse(g.x_about("Ukraina dostała czołgi"))


class TestBuild(unittest.TestCase):
    def test_counts_unique_and_rows(self):
        idx = rv.index()[:10]
        tw, tg = tw_frame(idx), tg_frame(idx)
        d = pd.concat([rv.x_series(tw, idx), rv.tg_series(tg, idx)], axis=1)
        self.assertTrue((d["x_about"] == 2).all())          # dwie różne kaskady o uchodźcach dziennie
        self.assertTrue((d["x_about_rows"] == 2).all())
        self.assertTrue((d["x_all"] == 4).all())
        self.assertTrue((d["tg_ru_about"] == 1).all())      # kopia liczona raz
        self.assertTrue((d["tg_ru_about_rows"] == 2).all())  # z kopiami dwa
        self.assertTrue((d["tg_ua_topic"] == 2).all())
        self.assertNotIn("tg_unlabeled_about", d.columns)   # strona nieznana nie wchodzi do testu


class TestStrictAndPeaks(unittest.TestCase):
    def test_strict_is_subset(self):
        self.assertTrue(g.x_about_strict("Uchodźcy w Polsce"))
        self.assertFalse(g.x_about_strict("Ukraińcy dostają 500+ w Polsce"))
        self.assertTrue(g.x_about("Ukraińcy dostają 500+ w Polsce"))
        self.assertTrue(g.telegram_about_strict("Беженцы из Украины"))
        self.assertFalse(g.telegram_about_strict("Украинцы в Польше открыли бизнес"))

    def test_series_and_peak_dump(self):
        idx = rv.index()[:10]
        tw, tg = tw_frame(idx), tg_frame(idx)
        tw["day"] = pd.to_datetime(tw["day"])
        d = pd.concat([rv.x_series(tw, idx), rv.tg_series(tg, idx)], axis=1)
        self.assertTrue((d["x_about_strict"] == 0).all())
        self.assertTrue((d["tg_ru_about_strict"] == 1).all())
        pk = rv.peak_dump(tw, tg, d, n_days=2, top=2)
        self.assertEqual(set(pk["platforma"]), {"X", "Telegram RU"})
        self.assertIn("ścisła", pk.columns)


class TestVariants(unittest.TestCase):
    def setUp(self):
        idx = rv.index()
        rng = np.random.default_rng(1)
        common = rng.poisson(20, len(idx))
        self.d = pd.DataFrame({"x_all": common * 3 + 50, "x_about": common + rng.poisson(5, len(idx)),
                               "x_about_rows": common + 10, "tg_ru_topic": rng.poisson(60, len(idx)),
                               "tg_ua_topic": rng.poisson(60, len(idx)), "tg_ru_about": common // 2 + rng.poisson(3, len(idx)),
                               "tg_ru_about_rows": common // 2 + 8, "tg_ua_about": rng.poisson(8, len(idx)),
                               "tg_ua_about_rows": rng.poisson(9, len(idx))}, index=idx)

    def test_smooth_days_replaces_only_spike(self):
        s = pd.Series(10.0, index=rv.index())
        s.loc["2022-06-02"] = 500
        out = rv.smooth_days(s, [pd.Timestamp("2022-06-02")])
        self.assertEqual(out.loc["2022-06-02"], 10.0)
        self.assertEqual(out.loc["2022-06-03"], 10.0)

    def test_variants_and_tests_run(self):
        v = rv.variants(self.d)
        self.assertIn("bez 2.06.2022", v)
        self.assertNotIn("Telegram: filtr v0.3", v)         # brak kolumny v0.3 -> wariant pominięty
        res = rv.run_tests(self.d, n_perm=50)
        self.assertEqual(set(res), set(v))
        self.assertTrue(all(0 <= r["p_ru"] <= 1 for r in res.values()))
        self.assertIn("| wariant |", rv.results_md(res, rv.density(self.d)))


if __name__ == "__main__":
    unittest.main()
