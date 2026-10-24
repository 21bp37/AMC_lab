"""Testy generatora próby do anotacji i skryptu weryfikacji zgodności (dane syntetyczne, bez sieci)."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import annotation_check as ck  # noqa: E402
from pipeline import annotation_sample as sm  # noqa: E402


def synth_x(n_per=None, seed=0):
    n_per = n_per or {"anti": 200, "pro": 150, "mieszane": 40, "brak": 2000}
    rows = []
    for st, n in n_per.items():
        for i in range(n):
            rows.append({"platform": "X", "source_id": f"{st}{i}", "source_group": f"u{i % 80}", "date": "2022-05-01", "side": "",
                         "text_original": f"treść numer {i} socjal" if st == "anti" else f"treść numer {i}", "stratum": st,
                         "lexicon_label": st, "truncated": False})
    return pd.DataFrame(rows)


def synth_tg(seed=0):
    rows = []
    sizes = {("anti", "uch"): 60, ("inne", "uch"): 400, ("anti", "bez"): 100, ("inne", "bez"): 800}
    for side in ("Pro-Russian", "Pro-Ukrainian"):
        for (kind, ref), n in sizes.items():
            for i in range(n):
                rows.append({"platform": "Telegram", "source_id": f"{side}{kind}{ref}{i}", "source_group": f"c{i % 40}",
                             "date": "2022-06-01", "side": side, "text_original": f"текст номер {i} пособия" if kind == "anti" else f"текст номер {i}",
                             "stratum": f"{side}|{kind}|{ref}", "lexicon_label": "anti" if kind == "anti" else "brak", "truncated": False,
                             "refugee_filter": "tak" if ref == "uch" else "nie", "refugee_hits": "беженц" if ref == "uch" else ""})
    return pd.DataFrame(rows)


class TestAllocation(unittest.TestCase):
    def test_scale_sums_to_n(self):
        for n in (20, 50, 100, 137):
            self.assertEqual(sum(sm.scale_alloc(sm.X_ALLOC, n).values()), n)
            self.assertEqual(sum(sm.scale_alloc(sm.TG_ALLOC, n).values()), n)

    def test_fit_redistributes_shortfall(self):
        plan = {"a": 30, "b": 25, "c": 10, "d": 35}
        fit = sm.fit_alloc(plan, {"a": 5, "b": 1000, "c": 1000, "d": 1000})
        self.assertEqual(fit["a"], 5)
        self.assertEqual(sum(fit.values()), 100)

    def test_fit_when_not_enough_in_total(self):
        fit = sm.fit_alloc({"a": 30, "b": 30}, {"a": 4, "b": 3})
        self.assertEqual(fit, {"a": 4, "b": 3})


class TestSample(unittest.TestCase):
    def setUp(self):
        self.master = sm.build_master(synth_x(), synth_tg(), 100, 100, cap=3, seed=1)

    def test_sizes_and_every_stratum_present(self):
        m = self.master
        self.assertEqual((m["platform"] == "X").sum(), 100)
        self.assertEqual((m["platform"] == "Telegram").sum(), 100)
        self.assertEqual(set(m.loc[m["platform"] == "X", "stratum"]), {"anti", "pro", "mieszane", "brak"})
        self.assertEqual(m.loc[m["platform"] == "Telegram", "stratum"].nunique(), 8)
        self.assertEqual(m["item_id"].is_unique, True)

    def test_weights_reproduce_population(self):
        m = self.master
        for plat, frame in (("X", synth_x()), ("Telegram", synth_tg())):
            s = m[m["platform"] == plat]
            self.assertAlmostEqual(s["weight"].sum() / len(frame), 1.0, delta=0.12)   # cap na źródło lekko zmniejsza ramkę

    def test_cap_per_source(self):
        m = self.master
        c = m.groupby(["stratum", "source_group"]).size()
        self.assertLessEqual(c.max(), 3)

    def test_deterministic(self):
        again = sm.build_master(synth_x(), synth_tg(), 100, 100, cap=3, seed=1)
        self.assertEqual(self.master["source_id"].tolist(), again["source_id"].tolist())

    def test_coder_view_blinded_and_shuffled(self):
        m = self.master
        v1, v2 = sm.coder_view(m, 5), sm.coder_view(m, 6)
        self.assertEqual(list(v1.columns), ["id", "zrodlo", "tekst_pl", "tekst_oryg", "etykieta", "tlumaczenie", "komentarz"])
        self.assertEqual(set(v1["id"]), set(m["item_id"]))
        self.assertNotEqual(v1["id"].tolist(), v2["id"].tolist())
        joined = " ".join(v1.astype(str).agg(" ".join, axis=1))
        self.assertNotIn("Pro-Russian", joined)
        self.assertNotIn("mieszane", joined)


class TestAnonymize(unittest.TestCase):
    def test_masks_handles_and_links(self):
        t = "@jan_k zobacz https://t.co/AbC123 i @ewa"
        out = sm.anonymize(t)
        self.assertNotIn("jan_k", out); self.assertNotIn("t.co", out); self.assertNotIn("ewa", out)
        self.assertIn("[link]", out)

    def test_content_len_ignores_handles_and_links(self):
        self.assertEqual(sm.content_len("@Oskar_M04 https://t.co/HAkhmsq2by"), 0)
        self.assertGreater(sm.content_len("@x to jest prawdziwy tekst"), 15)

    def test_master_has_no_handles_but_hits_use_raw_text(self):
        x = synth_x({"anti": 50, "pro": 50, "mieszane": 20, "brak": 200})
        x["text_original"] = "@banderowiec_77 socjal https://t.co/zzz " + x["text_original"]
        m = sm.build_master(x, pd.DataFrame(), 40, 0, cap=5, seed=3)
        self.assertFalse(m["text_original"].str.contains("banderowiec_77").any())
        self.assertTrue(m["lex_hits"].fillna("").str.contains("banderyzm").any())


class TestTranslation(unittest.TestCase):
    def test_cache_and_failure(self):
        calls = []

        def fake(t, lang):
            calls.append(t)
            if "zły" in t:
                raise RuntimeError("limit")
            return "PL:" + t

        with tempfile.TemporaryDirectory() as d:
            cache = Path(d) / "c.json"
            texts = pd.Series(["привіт", "привет", "zły tekst"])
            import pipeline.annotation_sample as m
            old = m.time.sleep
            m.time.sleep = lambda s: None
            try:
                out, st = sm.translate_all(texts, fake, cache, retries=2)
                self.assertEqual(out[:2], ["PL:привіт", "PL:привет"])
                self.assertTrue(st[2].startswith("blad"))
                n_before = len(calls)
                out2, st2 = sm.translate_all(texts[:2], fake, cache)
                self.assertEqual(len(calls), n_before)           # z cache
                self.assertEqual(out2, out[:2])
            finally:
                m.time.sleep = old

    def test_fail_fast_when_translator_is_down(self):
        import pipeline.annotation_sample as m
        old = m.time.sleep
        m.time.sleep = lambda s: None

        def broken(t, lang):
            raise RuntimeError("429 Too Many Requests")

        try:
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaises(sm.TranslationUnavailable) as cm:
                    sm.translate_all(pd.Series([f"текст {i}" for i in range(50)]), broken, Path(d) / "c.json", retries=2)
                self.assertIn("429", str(cm.exception))
        finally:
            m.time.sleep = old

    def test_from_master_resumes_without_resampling(self):
        master = sm.build_master(synth_x(), synth_tg(), 100, 100, cap=3, seed=4)
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            master.to_csv(d / "proba_master.csv", index=False, encoding="utf-8-sig")
            sm.main(["--from-master", "--translator", "none", "--coders", "A", "B", "--out", str(d)])
            again = pd.read_csv(d / "proba_master.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
            self.assertEqual(again["item_id"].tolist(), master["item_id"].tolist())
            sheet = pd.read_csv(d / "anotacja_A.csv", sep=";", encoding="utf-8-sig")
            self.assertEqual(len(sheet), 200)

    def test_deepl_backend_uses_header_and_free_url(self):
        import os
        import requests
        from unittest import mock
        seen = {}

        class Resp:
            status_code = 200
            text = ""

            def json(self):
                return {"translations": [{"text": "PL"}]}

        def fake_post(url, headers=None, json=None, timeout=None):
            seen.update(url=url, headers=headers, json=json)
            return Resp()

        old = os.environ.get("DEEPL_API_KEY")
        try:
            os.environ.pop("DEEPL_API_KEY", None)
            with self.assertRaises(SystemExit):
                sm.make_translator("deepl")
            os.environ["DEEPL_API_KEY"] = "abc:fx"
            with mock.patch.object(requests, "post", fake_post):
                out = sm.make_translator("deepl")("привет", "ru")
            self.assertEqual(out, "PL")
            self.assertTrue(seen["url"].startswith("https://api-free.deepl.com"))
            self.assertEqual(seen["headers"]["Authorization"], "DeepL-Auth-Key abc:fx")
            self.assertEqual(seen["json"]["source_lang"], "RU")
        finally:
            if old is None:
                os.environ.pop("DEEPL_API_KEY", None)
            else:
                os.environ["DEEPL_API_KEY"] = old

    def test_detect_lang(self):
        self.assertEqual(sm.detect_lang("Україна їде"), "uk")
        self.assertEqual(sm.detect_lang("Украина едет"), "ru")


def simulate(master, coders, noise, seed=0, truth_fn=None):
    """Prawda zależy od warstwy; każdy koder myli się z prawdopodobieństwem noise."""
    rng = np.random.default_rng(seed)
    truth = {}
    for i, r in master.iterrows():
        u = rng.random()
        if r["platform"] == "Telegram":
            kind, ref = r["stratum"].split("|")[1:3]
            if ref == "uch":
                t = "anty" if (kind == "anti" and u < 0.6) else ("neutralne" if u < 0.8 else "nie_dotyczy")
            else:
                t = "nie_dotyczy" if u < 0.93 else "neutralne"
        elif r["stratum"] == "anti":
            t = "anty" if u < 0.75 else "neutralne"
        elif r["stratum"] == "pro":
            t = "pro" if u < 0.8 else "neutralne"
        else:
            t = "anty" if u < 0.5 else "pro"
        truth[r["item_id"]] = t
    sheets = {}
    for c in coders:
        lab = []
        for i in master["item_id"]:
            t = truth[i]
            lab.append(t if rng.random() > noise else rng.choice(sm.LABELS))
        sheets[c] = pd.DataFrame({"id": master["item_id"], "etykieta": lab, "tlumaczenie": "", "komentarz": ""})
    return truth, sheets


class TestCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.master = sm.build_master(synth_x(), synth_tg(), 100, 100, cap=3, seed=2)
        self.master["text_pl"] = self.master["text_original"]
        self.master.to_csv(self.d / "proba_master.csv", index=False, encoding="utf-8-sig")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, sheets, **kw):
        paths = []
        for c, df in sheets.items():
            p = self.d / f"anotacja_{c}.csv"
            df.to_csv(p, index=False, sep=";", encoding="utf-8-sig")
            paths.append(p)
        return ck.run(self.d / "proba_master.csv", paths, None, kw.pop("classifiers", []), kw.pop("resolved", None),
                      self.d, boot=200, kappa_min=0.4, prec_min=0.7)

    def test_perfect_agreement_gives_kappa_one(self):
        _, sheets = simulate(self.master, ["A", "B"], noise=0.0)
        rep = self._run(sheets)
        self.assertIn("1.00 [", rep)
        self.assertIn("do rozstrzygnięcia: 0", rep)

    def test_disagreements_go_to_queue_and_resolve(self):
        _, sheets = simulate(self.master, ["A", "B"], noise=0.3, seed=3)
        self._run(sheets)
        q = pd.read_csv(self.d / "do_rozstrzygniecia.csv", encoding="utf-8-sig")
        self.assertGreater(len(q), 0)
        q["etykieta_final"] = "neutralne"
        q.to_csv(self.d / "res.csv", index=False)
        rep = self._run(sheets, resolved=self.d / "res.csv")
        self.assertIn("do rozstrzygnięcia: 0", rep)

    def test_low_agreement_triggers_warning(self):
        _, sheets = simulate(self.master, ["A", "B"], noise=0.95, seed=4)
        rep = self._run(sheets)
        self.assertIn("< 0.4", rep)

    def test_xlsx_roundtrip_and_validation(self):
        view = sm.coder_view(self.master, 9)
        view["etykieta"] = "anty"
        p = self.d / "anotacja_Z.xlsx"
        sm.write_xlsx(p, view, "Z")
        got = ck.load_coder(p, "Z")
        self.assertEqual(len(got), len(view))
        self.assertTrue((got["Z__label"] == "anty").all())
        view.loc[0, "etykieta"] = "chyba tak"
        view.to_csv(self.d / "anotacja_Q.csv", index=False, sep=";")
        with self.assertRaises(SystemExit):
            ck.load_coder(self.d / "anotacja_Q.csv", "Q")

    def test_precision_recall_against_known_truth(self):
        # koderzy bez błędów: wzorzec = prawda, więc metryki słownika można policzyć ręcznie z wagami
        truth, sheets = simulate(self.master, ["A", "B"], noise=0.0, seed=5)
        rep = self._run(sheets)
        m = self.master.assign(y=self.master["item_id"].map(truth))
        x = m[m["platform"] == "X"]
        pred = x["lexicon_label"].isin(["anti", "mieszane"])
        tp = (x["weight"] * (pred & (x["y"] == "anty"))).sum()
        prec = tp / (x["weight"] * pred).sum()
        rec = tp / (x["weight"] * (x["y"] == "anty")).sum()
        self.assertIn(f"{prec:.2f} [", rep)
        self.assertIn(f"{rec:.2f} [", rep)
        self.assertTrue((self.d / "bledy_leksykonu.csv").exists())

    def test_filter_precision_recall_against_known_truth(self):
        truth, sheets = simulate(self.master, ["A", "B"], noise=0.0, seed=7)
        rep = self._run(sheets)
        t = self.master[self.master["platform"] == "Telegram"].assign(y=lambda d: d["item_id"].map(truth))
        passed = t["refugee_filter"].eq("tak")
        on = t["y"].isin(["anty", "pro", "neutralne"])
        w = t["weight"]
        prec = (w * (passed & on)).sum() / (w * passed).sum()
        tp = (w * (passed & on)).sum()
        fn = (w * (~passed & on)).sum()
        self.assertIn("3b. Filtr uchodźczy", rep)
        self.assertIn(f"{prec:.2f} [", rep)
        self.assertIn(f"{tp / (tp + fn):.2f} [", rep)
        self.assertTrue((self.d / "bledy_filtra.csv").exists())

    def test_classifier_not_in_reference(self):
        truth, sheets = simulate(self.master, ["A", "B", "C"], noise=0.0, seed=6)
        sheets["C"]["etykieta"] = "anty"          # „model” zawsze mówi anty
        rep = self._run(sheets, classifiers=["C"])
        self.assertIn("Koderzy wzorca: A, B", rep)
        self.assertIn("| C |", rep)

    def test_needs_two_reference_coders(self):
        _, sheets = simulate(self.master, ["A", "B"], noise=0.0)
        with self.assertRaises(SystemExit):
            self._run(sheets, classifiers=["B"])


if __name__ == "__main__":
    unittest.main()
