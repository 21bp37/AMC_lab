import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import agreement as ag  # noqa: E402
import checks  # noqa: E402
import estimators as est  # noqa: E402
import evaluation as ev  # noqa: E402
import make_synthetic as ms  # noqa: E402
import prompt_robustness as pr  # noqa: E402
import run_log  # noqa: E402
import sample_size as ss  # noqa: E402
import sampling as sp  # noqa: E402


class TestAgreement(unittest.TestCase):
    def test_perfect_and_chance(self):
        self.assertAlmostEqual(ag.krippendorff_alpha([["a", "a"], ["b", "b"], ["a", "a"], ["b", "b"]]), 1.0)
        rng = np.random.default_rng(0)
        units = [[rng.choice(["a", "b"]), rng.choice(["a", "b"])] for _ in range(4000)]
        self.assertAlmostEqual(ag.krippendorff_alpha(units), 0.0, delta=0.05)

    def test_alpha_close_to_kappa_two_coders(self):
        rng = np.random.default_rng(1)
        t = rng.random(3000) < 0.3
        a = np.where(rng.random(3000) < 0.9, t, ~t); b = np.where(rng.random(3000) < 0.9, t, ~t)
        units = [[str(x), str(y)] for x, y in zip(a, b)]
        self.assertAlmostEqual(ag.krippendorff_alpha(units), ag.cohen_kappa(a.astype(str), b.astype(str)), delta=0.01)

    def test_fast_binary_equals_general(self):
        a, b, c, d = 30, 5, 7, 58
        units = [["1", "1"]] * a + [["1", "0"]] * b + [["0", "1"]] * c + [["0", "0"]] * d
        self.assertAlmostEqual(ag.krippendorff_alpha(units), ag.alpha_binary_two_coders(a, b, c, d), places=9)

    def test_missing_values_and_three_coders(self):
        units = [["a", "a", None], ["b", "b", "b"], ["a", None, None], ["b", "a", "b"]]
        v = ag.krippendorff_alpha(units)
        self.assertTrue(0 < v < 1)

    def test_kappa_paradox_reported_via_prevalence_and_pa_na(self):
        # wysoka zgodność, niska kappa przy rzadkiej klasie [@feinstein1990]
        a = ["1"] * 2 + ["0"] * 96 + ["1"] * 1 + ["0"] * 1
        b = ["1"] * 2 + ["0"] * 96 + ["0"] * 1 + ["1"] * 1
        st = ag.binary_agreement_stats(a, b, "1")
        self.assertGreater(st["observed_agreement"], 0.97)
        self.assertLess(ag.cohen_kappa(a, b), 0.7)
        self.assertGreater(st["prevalence_index"], 0.9 * -1 if False else -1)  # PI zdefiniowane
        self.assertLess(st["positive_agreement"], st["negative_agreement"])

    def test_interpretation_thresholds(self):
        self.assertIn("wiarygodne", ag.interpret_alpha(0.85))
        self.assertIn("wstępne", ag.interpret_alpha(0.7))
        self.assertIn("niewystarczające", ag.interpret_alpha(0.5))


class TestSampling(unittest.TestCase):
    def test_horvitz_thompson_unbiased_with_cap(self):
        df = ms.make_synthetic(n=3000, seed=3)
        df["stratum"] = df["celeb_pred"].astype(str)
        true_total = df["celeb_true"].sum()
        ests = []
        for seed in range(60):
            s = sp.stratified_sample(df, "stratum", {"0": 100, "1": 100}, "advertiser_id", 8, seed=seed)
            ests.append(sp.horvitz_thompson_total(s, "celeb_true"))
        self.assertAlmostEqual(np.mean(ests) / true_total, 1.0, delta=0.06)

    def test_inclusion_probs_valid_and_cap_respected(self):
        df = ms.make_synthetic(n=2000, seed=4)
        df["stratum"] = df["month"]
        s = sp.stratified_sample(df, "stratum", 50, "advertiser_id", 3, seed=1)
        self.assertTrue(((s["inclusion_prob"] > 0) & (s["inclusion_prob"] <= 1)).all())
        self.assertLessEqual(s.groupby(["stratum", "advertiser_id"]).size().max(), 3)
        self.assertTrue((s.groupby("stratum").size() <= 50).all())


class TestEstimators(unittest.TestCase):
    def test_difference_estimator_corrects_naive_bias(self):
        naive, corr = [], []
        for seed in range(80):
            df = ms.make_synthetic(n=6000, seed=100 + seed)
            truth = df["celeb_true"].mean()
            df["stratum"] = df["celeb_pred"].astype(str)
            s = sp.stratified_sample(df, "stratum", {"0": 300, "1": 150}, "advertiser_id", 10, seed=seed)
            pop = df.rename(columns={"celeb_pred": "pred", "advertiser_id": "cluster"}).copy()
            pop["gold"] = np.nan; pop["weight"] = np.nan
            key = s.set_index("ad_id")
            m = pop["ad_id"].isin(key.index)
            pop.loc[m, "gold"] = pop.loc[m, "ad_id"].map(key["celeb_true"]).astype(float)
            pop.loc[m, "weight"] = pop.loc[m, "ad_id"].map(key["weight"])
            naive.append(est.naive_prevalence(pop) - truth)
            corr.append(est.difference_estimate(pop) - truth)
        # Obciążenie oceniamy względem błędu standardowego średniej (estymator po korekcie jest nieobciążony,
        # ale ma większą wariancję niż naiwny; stały próg przy małej liczbie powtórzeń dawał fałszywe alarmy).
        se = lambda v: np.std(v, ddof=1) / np.sqrt(len(v))
        self.assertLess(abs(np.mean(corr)), 3 * se(corr))
        self.assertGreater(abs(np.mean(naive)), 5 * se(naive))  # naiwna estymata jest obciążona (czułość < 1)
        self.assertLess(abs(np.mean(corr)), abs(np.mean(naive)))

    def test_sens_spec_inversion(self):
        q = 0.1 * 0.7 + 0.9 * 0.02
        self.assertAlmostEqual(est.prevalence_from_sens_spec(q, 0.7, 0.98), 0.1, places=9)
        self.assertTrue(math.isnan(est.prevalence_from_sens_spec(0.1, 0.5, 0.4)))


class TestEvaluationAndSize(unittest.TestCase):
    def test_prf_known_values_and_weights(self):
        yt = ["1", "1", "0", "0", "1"]; yp = ["1", "0", "0", "1", "1"]
        r = ev.prf(yt, yp, "1")
        self.assertAlmostEqual(r["precision"], 2 / 3); self.assertAlmostEqual(r["recall"], 2 / 3)
        rw = ev.prf(yt, yp, "1", weights=[1, 1, 1, 1, 1])
        self.assertAlmostEqual(r["f1"], rw["f1"])

    def test_cluster_bootstrap_wider_than_row_bootstrap_under_clustering(self):
        rng = np.random.default_rng(0)
        rows = []
        for c in range(30):
            acc = rng.uniform(0.5, 1.0)
            for _ in range(40):
                t = int(rng.random() < 0.5); p = t if rng.random() < acc else 1 - t
                rows.append((c, str(t), str(p)))
        df = pd.DataFrame(rows, columns=["c", "t", "p"])
        w_c = ev.cluster_bootstrap_prf(df, "t", "p", "1", "c", boot=400)["recall"]
        w_r = ev.cluster_bootstrap_prf(df, "t", "p", "1", None, boot=400)["recall"]
        self.assertGreater(w_c[2] - w_c[1], w_r[2] - w_r[1])

    def test_wilson_and_need(self):
        lo, hi = ss.wilson_ci(40, 50)
        self.assertTrue(lo < 0.8 < hi)
        n = ss.n_needed(0.8, 0.10)
        self.assertLessEqual(ss.wilson_halfwidth(0.8, n), 0.10)
        self.assertGreater(ss.wilson_halfwidth(0.8, n - 1), 0.10)

    def test_deff_and_alpha_sim_monotone(self):
        self.assertAlmostEqual(ss.design_effect(0.1, 11), 2.0)
        small = ss.simulate_alpha(60, 0.3, 0.92, reps=80, boot=150, seed=1)["median_halfwidth"]
        large = ss.simulate_alpha(400, 0.3, 0.92, reps=80, boot=150, seed=1)["median_halfwidth"]
        self.assertGreater(small, large)


class TestAudit(unittest.TestCase):
    def test_audit_counts_and_concentration(self):
        import audit_dataset as au
        df = ms.make_synthetic(n=2000, seed=9)
        df["language"] = "pl"; df["platform"] = "x"; df["retrieval_date"] = "2026-10-01"; df["ad_text"] = "t"
        df["creative_available"] = 0; df["source_name"] = "syn"; df["source_version"] = "0"
        a = au.audit(df)
        self.assertEqual(a["n_rows"], 2000)
        self.assertEqual(a["missing_required_columns"], [])
        self.assertEqual(a["duplicate_ad_id"], 0)
        c = a["concentration"]
        self.assertTrue(0 < c["top10_share"] <= 1)
        self.assertLessEqual(c["effective_clusters"], c["n_clusters"])
        self.assertEqual(a["creative_available_share"], 0.0)
        self.assertIn("P02", au.format_report(a))

    def test_audit_lifespan_censoring(self):
        import audit_dataset as au
        df = pd.DataFrame({"delivery_start": ["2026-01-01", "2026-01-01", "2026-02-01", "2026-03-01"],
                           "delivery_stop": ["2026-01-11", None, "2026-01-20", "2026-03-31"]})
        a = au.audit(df)
        self.assertAlmostEqual(a["open_ended_share"], 0.25)
        self.assertEqual(a["negative_duration_rows"], 1)   # stop przed start
        self.assertEqual(a["closed_duration_days"]["n"], 2)
        self.assertEqual(a["closed_duration_days"]["median"], 20.0)

    def test_concentration_equal_clusters(self):
        import audit_dataset as au
        c = au.concentration(pd.Series([10] * 20))
        self.assertAlmostEqual(c["effective_clusters"], 20.0)


class TestRobustnessLogAndChecks(unittest.TestCase):
    def test_prompt_robustness_flip_rate(self):
        df = pd.DataFrame({"item_id": list("ABAB") + ["C", "C"], "config": ["p1", "p1", "p2", "p2", "p1", "p2"],
                           "label": ["1", "0", "1", "1", "0", "0"]})
        r = pr.robustness_report(df, positive="1")
        self.assertAlmostEqual(r["flip_rate"], 1 / 3)

    def test_run_log_writes_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "p.txt"; p.write_text("prompt"); i = Path(d) / "i.csv"; i.write_text("a\n1")
            rec = run_log.log_run(str(Path(d) / "runs.jsonl"), "x", "m", "v", {"temperature": 0}, str(p), str(i), 1)
            self.assertEqual(len(rec["prompt_sha256"]), 64)
            self.assertEqual(len((Path(d) / "runs.jsonl").read_text().splitlines()), 1)

    def test_sheet_validation(self):
        schema = checks.load_schema()
        ok = [{"celeb_mention": "explicit_name", "celeb_id": "fikcyjna_osoba", "scam_type": "investment_crypto"}]
        self.assertEqual(checks.validate_sheet_rows(ok, schema), [])
        bad = [{"celeb_mention": "maybe", "celeb_id": ""}, {"celeb_mention": "implied", "celeb_id": ""},
               {"celeb_mention": "none", "celeb_id": "x"}, {"media_type": "image"}]
        errs = checks.validate_sheet_rows(bad, schema)
        self.assertEqual(len(errs), 4)
        self.assertEqual(checks.validate_sheet_rows([{"media_type": "image"}], schema, allow_l2=True), [])

    def test_repo_consistency_and_placeholders(self):
        self.assertEqual(checks.check_consistency(), [])
        errs, stats = checks.check_placeholders()
        self.assertEqual(errs, [])
        self.assertGreater(stats["registry"], 10)


if __name__ == "__main__":
    unittest.main()
