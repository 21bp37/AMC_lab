"""Stałe pipeline'u: ścieżki, słowniki słów kluczowych, lista wydarzeń.

Słowniki są parametrami pomiaru, nie wynikami. Każda zmiana słownika = nowa wersja (LEXICON_VERSION)
i wpis w CHANGELOG pomiaru, bo zmienia zmienną wynikową.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_TWITTER = ROOT / "ukraine-source" / "with_sentiment.csv"   # do przeniesienia poza repo (zob. CLEANUP.md)
PROCESSED = ROOT / "data" / "processed"                          # w .gitignore
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

# Kolumny NodeXL -> nazwy robocze
TWITTER_COLUMNS = {
    "Imported ID": "tweet_id",
    "Vertex 1": "author",
    "Vertex 2": "target",
    "Relationship": "relationship",
    "Relationship Date (UTC)": "ts",
    "Tweet": "text",
    "Retweet Count": "retweet_count",
    "Favorite Count": "like_count",
    "Reply Count": "reply_count",
    "Quote Count": "quote_count",
    "Domains in Tweet": "domains",
    "Hashtags in Tweet": "hashtags",
    "Conversation ID": "conversation_id",
    "In Reply To Tweet ID": "reply_to_id",
    "Retweet ID": "retweet_of_id",
    "Author ID": "author_id",
    "Vertex 1 Group": "nodexl_group",
    "Sentiment_Label": "sentiment",
    "Sentiment_Score": "sentiment_score",
}

# Okno badania (deklarowane w opisie zbioru) i dzień, od którego zbiór jest faktycznie kompletny
# (ustalone w eksploracji: 24.02-03.03.2022 to tylko kilkadziesiąt wierszy).
STUDY_START = "2022-02-24"
STUDY_END = "2022-12-31"
EFFECTIVE_START = "2022-03-04"

# Filtr tematyczny (odtworzenie kryterium doboru; w danych tylko ~45% oryginałów zawiera obie frazy dosłownie)
TOPIC_UA = r"ukrai|ukraiń|ukrain"
TOPIC_PL = r"w polsce|polsk|polak|polacy|polek"

# Leksykon narracji antyukraińskich (wersja eksploracyjna, do walidacji na gold standardzie).
# Narracje odpowiadają kategoriom znanym z raportów o dezinformacji wobec uchodźców w PL.
LEXICON_VERSION = "0.2"
ANTI_UA_NARRATIVES = {
    "swiadczenia": r"800\s?\+|500\s?\+|świadcze|zasiłk|socjal|za darmo|na nasz koszt|utrzym|podatnik",
    "praca_mieszkania": r"zabier\w* (?:nam )?(?:prac|mieszka)|podwyż\w* czynsz|kolejk\w* do lekarz",
    "przestepczosc": r"gwałt|morderst|bandy[tc]|napad|przestęp|kradzie",
    "banderyzm": r"bandero|banderow|upa\b|wołyń|ukrainizac|ukropol",
    "roszczeniowosc": r"roszczeni|niewdzięcz|(?:nie widać|brak\w*|bez) wdzięczn|bezczeln|panosz",
    "zagrozenie_zdrowie": r"gruźlic|choroby|epidemi|szczepi",
}

# Leksykon treści proukraińskich (solidarność, pomoc, wdzięczność). Wersja eksploracyjna.
PRO_UA_NARRATIVES = {
    "pomoc": r"pomag|pomoc\w* (?:ukrai|uchodź)|zbiórk|wolontari|gościn|przyjmuj\w* uchodź",
    "solidarnosc": r"solidarn|wspier|wsparci|bracia|braterst|przyjaci|razem|sława ukrain|slava ukrain|standwithukraine|witamy",
    "wdziecznosc": r"wdzięczn|dziękuj",
}
# Negacja wdzięczności („nie widać wdzięczności”) to narracja anty-UA, nie pro-UA: zeruje flagę pro dla wpisu.
NEGATED_GRATITUDE = r"(?:nie widać|nie ma|brak\w*|bez|zero) wdzięczn|niewdzięcz"

# Telegram: słowa kluczowe RU/UK dla „Ukraińcy w Polsce” (do filtrowania 79 mln postów)
TELEGRAM_UA = r"(?i)(?:украин|україн)"
TELEGRAM_PL = r"(?i)(?:польш|польщ|поляк|поляц|польськ|варшав)"

# Telegram: narracje anty-UA w RU/UK (SZKIC v0.1, niezwalidowany; zespół nie zna RU/UK, więc walidacja na próbie ok. 100 postów
# po tłumaczeniu maszynowym). Odpowiada kategoriom polskiego leksykonu.
TELEGRAM_ANTI_UA = (r"(?i)(?:пособи|выплат|халяв|бесплатн|за счет поляков|за счёт поляков|нахлебник|паразит|"
                    r"неблагодарн|наглост|наглы|бандер|нацист|укроп|хохл|понаех|преступн|грабе|насил|"
                    r"утриманц|невдячн)")

# Wydarzenia do opisu peaków (daty UTC; lista robocza, do weryfikacji przez analityka)
EVENTS = {
    "2022-03-12": "ustawa o pomocy UA",
    "2022-05-09": "ambasador Rosji (farba)",
    "2022-05-14": "Eurowizja",
    "2022-11-15": "Przewodów",
}
