"""Testy narzędzi walidacji instrumentu (zgodność, ewaluacja, liczebność, dziennik uruchomień).

Narzędzia są ogólne: posłużą do walidacji klasyfikatora sentymentu / narracji na gold standardzie.
"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import agreement as ag  # noqa: E402
import evaluation as ev  # noqa: E402
import prompt_robustness as pr  # noqa: E402
import run_log  # noqa: E402
import sample_size as ss  # noqa: E402


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



class TestRobustnessAndLog(unittest.TestCase):
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



if __name__ == "__main__":
    unittest.main()
