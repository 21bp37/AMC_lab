"""Testy filtra uchodźczego RU/UK (dane syntetyczne, bez sieci)."""
import re
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import config  # noqa: E402
from pipeline import telegram_refugee as tr  # noqa: E402

POS = ["Беженцы из Украины получают помощь в Польше", "Біженці з України в Польщі", "Украинцы в Польше открыли бизнес",
       "Українці у Польщі отримали статус", "Тимчасовий захист для українців", "Украинцы, живущие в Польше, жалуются",
       "Украинские мигранты на границе Польши", "Украинцы приехавшие в Польшу", "Заробітчани з України в Польщі"]
NEG = ["Польша передала Украине танки", "Президент Украины встретился с премьером Польши", "ВСУ атаковали позиции у границы с Польшей",
       "Украинцы отбили атаку, в Польше новости", "Украинцы победили. В Польше праздник", "Допомога Україні від Польщі: нові гаубиці"]


class TestTerms(unittest.TestCase):
    def test_positive_and_negative_examples(self):
        f = tr.flag(pd.Series(POS + NEG))
        self.assertEqual(f["is_refugee"].tolist(), [True] * len(POS) + [False] * len(NEG))

    def test_hits_report_matched_fragment(self):
        f = tr.flag(pd.Series(["Беженцы в Польше", "ничего"]))
        self.assertIn("беженц", f.loc[0, "refugee_hits"])
        self.assertEqual(f.loc[1, "refugee_hits"], "")

    def test_filter_does_not_contain_anti_lexicon_words(self):
        """Filtr mówi KTO, nie CO: żaden rdzeń z list nie może trafiać w słownik anty-UA (inaczej udział „anty” rośnie mechanicznie)."""
        anti = re.compile(config.TELEGRAM_ANTI_UA)
        for cat in ("uchodzcy", "migranci"):
            for stem in config.TELEGRAM_REFUGEE_TERMS[cat]:
                if "\\" in stem:
                    stem = stem.replace("\\w*", "x").replace("\\w", "x")
                self.assertIsNone(anti.search(stem), stem)
        for text in POS:
            only_topic = text
            self.assertIsNone(anti.search(only_topic), only_topic)

    def test_everything_passed_also_matches_ukraine_or_poland_not_required(self):
        # filtr jest warunkiem DODATKOWYM do UA+PL (stosowany po prepare), sam nie sprawdza Ukrainy ani Polski
        self.assertTrue(tr.flag(pd.Series(["беженцы"]))["is_refugee"].iloc[0])


class TestV03(unittest.TestCase):
    def test_phrase_allows_up_to_three_words_between(self):
        yes = ["Більше 2млн українців були змушені евакуюватись до Польщі через напад", "Украинцы, живущие в Польше, жалуются",
               "Украинцы получившие статус беженцев в Польше"]
        no = ["Украинцы отбили атаку, в Польше новости", "Украинцы победили. В Польше праздник",
              "Украинцы воюют на востоке страны, а в Польше выборы"]
        for t in yes:
            self.assertTrue(tr.flag(pd.Series([t]))["ukraincy_w_polsce"].iloc[0], t)
        for t in no:
            self.assertFalse(tr.flag(pd.Series([t]))["ukraincy_w_polsce"].iloc[0], t)


class TestV02(unittest.TestCase):
    FILLER = "Слово и ещё слово про погоду и футбол. " * 20          # ~760 znaków bez słów filtra

    def test_single_mention_deep_in_long_post_is_not_refugee(self):
        f = tr.flag(pd.Series([self.FILLER + "Беженцы получили помощь."]))
        self.assertTrue(f.loc[0, "refugee_weak"])
        self.assertFalse(f.loc[0, "is_refugee"])

    def test_two_mentions_or_lead_mention_is_refugee(self):
        two = tr.flag(pd.Series([self.FILLER + "Беженцы получили помощь. " + self.FILLER + "Беженцы уехали."]))
        lead = tr.flag(pd.Series(["Беженцы получили помощь. " + self.FILLER]))
        self.assertTrue(two.loc[0, "is_refugee"])
        self.assertTrue(lead.loc[0, "is_refugee"])

    def test_phrase_ukrainians_in_poland_is_always_strong(self):
        f = tr.flag(pd.Series([self.FILLER + "Украинцы в Польше открыли бизнес."]))
        self.assertTrue(f.loc[0, "is_refugee"])

    def test_migration_stems_do_not_match_inside_words(self):
        for t in ["иммиграцию в Турции", "Українська еміграція 1930 року", "міграційний тиск на Європу", "миграционная политика ЕС"]:
            self.assertFalse(tr.flag(pd.Series([t]))["refugee_weak"].iloc[0], t)
        self.assertTrue(tr.flag(pd.Series(["Мигранты на границе"]))["is_refugee"].iloc[0])


class TestStats(unittest.TestCase):
    def test_density_verdict(self):
        ok = {"median_day": 8, "zero_days": 0.1, "mean_week": 56}
        weekly = {"median_day": 1, "zero_days": 0.6, "mean_week": 30}
        few = {"median_day": 0, "zero_days": 0.95, "mean_week": 3}
        self.assertIn("gęsty", tr.density_verdict(ok))
        self.assertIn("tygodniowy", tr.density_verdict(weekly))
        self.assertIn("za mało", tr.density_verdict(few))

    def test_wilson_and_recall(self):
        p, lo, hi = tr.wilson(8, 10)
        self.assertAlmostEqual(p, 0.8)
        self.assertTrue(lo < p < hi and 0 <= lo and hi <= 1)
        est, lo, hi = tr.recall_ci(100, 9, 10, 1000, 1, 20)         # TP=90, FN=50 -> 0.643
        self.assertAlmostEqual(est, 90 / 140, places=6)
        self.assertTrue(lo < est < hi)


def synth_posts(tmp: Path):
    rng = np.random.default_rng(1)
    refugee = ["Беженцы из Украины в Польше №{}", "Біженці з України в Польщі №{}", "Украинцы в Польше получают пособия №{}"]
    other = ["Польша передала Украине танки №{}", "Президент Украины встретился с премьером Польши №{}", "Україна просить Польщу про зброю №{}"]
    rows = []
    for i in range(3000):
        ch = int(rng.integers(1, 60))
        t = (rng.choice(refugee) if rng.random() < 0.25 else rng.choice(other)).format(i)
        rows.append({"id": i, "peer_id": ch, "date": f"2022-0{int(rng.integers(4, 9))}-{int(rng.integers(10, 28))} 12:00:00+00:00",
                     "message": t + " " + "слово " * 8, "views": 10, "forwards": 1})
    pd.DataFrame(rows).to_csv(tmp / "posts_2022_part_1.csv", index=False)
    pd.DataFrame({"peer_id": range(1, 60), "cluster": 0, "side": ["pro-Russian" if i % 2 else "pro-Ukrainian" for i in range(1, 60)]}
                 ).to_csv(tmp / "leiden_clusters.csv", index=False)


class TestEndToEnd(unittest.TestCase):
    def test_check_then_score(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            synth_posts(d)
            old = (tr.REPORTS, config.PROCESSED)
            tr.REPORTS, config.PROCESSED = d / "reports", d / "processed"
            try:
                tr.cmd_check(Namespace(posts=str(d / "posts_2022_part_*.csv"), clusters=str(d / "leiden_clusters.csv"), n_pass=40, n_rej=40,
                                       translator="none", seed=1, out=str(d / "ann")))
                md = (d / "reports" / "filtr_uchodzczy_wyniki.md").read_text(encoding="utf-8")
                self.assertIn("Pro-Russian", md)
                daily = pd.read_csv(d / "processed" / "telegram_refugee_daily.csv")
                self.assertEqual(set(daily["side"]), {"Pro-Russian", "Pro-Ukrainian"})
                self.assertGreater(daily["n_refugee"].sum(), 0)
                self.assertLessEqual(daily["n_refugee"].sum(), daily["n_topic"].sum())

                master = pd.read_csv(d / "ann" / "filtr_przeglad_master.csv", encoding="utf-8-sig")
                self.assertEqual(set(master["group"]), {"przepuszczony", "odrzucony"})
                view = pd.read_csv(d / "ann" / "filtr_przeglad.csv", sep=";", encoding="utf-8-sig")
                self.assertNotIn("group", view.columns)                   # recenzent nie widzi decyzji filtra
                self.assertEqual(list(view.columns), ["id", "tekst_pl", "tekst_oryg", "o_uchodzcach", "tlumaczenie", "komentarz"])

                # recenzent: wszystkie przepuszczone „tak”, odrzucone „nie” => precyzja 1, brak pominiętych
                truth = dict(zip(master["item_id"], np.where(master["group"] == "przepuszczony", "tak", "nie")))
                view["o_uchodzcach"] = view["id"].map(truth)
                view.to_csv(d / "ann" / "filtr_przeglad.csv", sep=";", index=False, encoding="utf-8-sig")
                tr.cmd_score(Namespace(master=None, reviewed=str(d / "ann" / "filtr_przeglad.csv"), precision_min=0.7, recall_min=0.5,
                                       out=str(d / "ann")))
                sc = (d / "reports" / "filtr_uchodzczy_przeglad.md").read_text(encoding="utf-8")
                self.assertIn("1.00 [", sc)
                self.assertIn("Precyzja", sc.replace("precyzja", "Precyzja"))
            finally:
                tr.REPORTS, config.PROCESSED = old

    def test_reflag_fn_maps_master_rows_to_new_flags(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            synth_posts(d)
            posts, clusters = str(d / "posts_2022_part_*.csv"), str(d / "leiden_clusters.csv")
            df = tr.load(posts, clusters)
            pick = df.sample(20, random_state=1)
            master = pd.DataFrame({"platform": "Telegram", "source_id": (pick["peer_id"].astype(str) + "/" + pick["id"].astype(str)).to_numpy(),
                                   "refugee_filter": "nie", "refugee_hits": ""}, index=[f"P{i:03d}" for i in range(20)])
            new = tr.reflag_fn(posts, clusters)(master)
            self.assertEqual(list(new.index), list(master.index))
            self.assertEqual(new["refugee_filter"].eq("tak").tolist(), pick["is_refugee"].tolist())

    def test_xlsx_review_sheet_has_dropdown(self):
        import openpyxl
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.xlsx"
            tr.write_review_xlsx(p, pd.DataFrame({"id": ["R001"], "tekst_pl": ["x"], "tekst_oryg": ["y"], "o_uchodzcach": [""],
                                                  "tlumaczenie": [""], "komentarz": [""]}))
            wb = openpyxl.load_workbook(p)
            try:
                self.assertIn("tak,nie,niejasne", wb["Przeglad"].data_validations.dataValidation[0].formula1)
            finally:
                wb.close()


if __name__ == "__main__":
    unittest.main()
