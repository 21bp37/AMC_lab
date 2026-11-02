"""Bramka „post o uchodźcach / Ukraińcach w Polsce” (wersja 0.4). Nie rozstrzyga postawy (anty / pro).

Telegram: działa na tekście ORYGINALNYM (RU/UK), więc nie wymaga tłumaczenia pełnych danych. X: tekst polski.
Reguły postawy nie przeszły walidacji (reports/M_codebook_gold_standard.tex), więc nie ma ich tutaj.
"""
from __future__ import annotations
import re

VERSION = "0.4"
I = re.I

# ---------------- Telegram (RU/UK) ----------------
# Rdzenie „uchodźca / migrant / ochrona czasowa”. Celowo BEZ „переселенц / вимушені переселенці”
# (to zwykle przesiedleńcy wewnętrzni na Ukrainie, nie uchodźcy w Polsce).
TG_REFUGEE_CORE = re.compile(
    r"беженц|беженк|беженств|беженск|біженц|біженк|біженств|біженськ|"
    r"(?<!\w)мигрант|(?<!\w)мігрант|гастарбайтер|заробітчан|"
    r"временн\w* защит|тимчасов\w* захист|просител\w* убежищ|шукач\w* притулку", I)
# „Ukrainiec/Ukrainka (+ do 3 słów) w/do Polsce/Polski”
TG_UA_IN_PL = re.compile(
    r"украин[цк]\w*(?:[\s,]+[^\W\d_]+){0,3}?\s+(?:в|во)\s+польш|"
    r"україн[цк]\w*(?:[\s,]+[^\W\d_]+){0,3}?\s+(?:в|у|до)\s+польщ", I)
TG_LEAD_CHARS = 300


def telegram_about(text: str) -> bool:
    """True, gdy rdzeń uchodźczy pada w pierwszych 300 znakach LUB gdzieś jest fraza „Ukraińcy w Polsce”."""
    t = text or ""
    return bool(TG_REFUGEE_CORE.search(t[:TG_LEAD_CHARS])) or bool(TG_UA_IN_PL.search(t))


# ---------------- X (PL) ----------------
UKR = r"ukra[ińi]*[nń]c|ukrainiec|ukrainek|ukrainka|ukraińsk\w+ (?:uchodź|rodzin|dziec|kobiet|matk)"
REFNOUN = re.compile(r"uchodź|uciekin|uciekaj\w+ przed wojn|przesiedle|imigran|migran|azyl", I)
PL_HERE = (r"w polsce|tutaj|tu\b|u nas|do polski|w kraju|przyjecha|przyjeżdż|wjecha|osiedl|przyjmuj|przyjęt|"
           r"pobiera|pobierają|mieszka")
UKR_HERE = re.compile(r"(?:%s)[^.!?\n]{0,70}(?:%s)|(?:%s)[^.!?\n]{0,70}(?:%s)" % (UKR, PL_HERE, PL_HERE, UKR), I)
SOCIAL = re.compile(
    r"500\s?\+|800\s?\+|socjal|pesel|zasiłk|świadcze|zbiórk|pomoc\w* (?:ukrai|uchodź|humanitar)|"
    r"zabier\w* (?:nam )?(?:prac|mieszka)|szczepi|szpital|lekarz|szko[łl]", I)
EXTRA = re.compile(
    r"wdzięczn|dziękuj|dziękujemy|pomoc\w* (?:wojskow|społeczn)|nie chcieli uciekać|przyjazd\w* osób|hiv\b|dzicz|parkuj|"
    r"ukraińc\w* (?:od lat|zawsze|się nie zmienili)", I)
_UKR = re.compile(UKR, I)


def x_about(text: str) -> bool:
    """Post o uchodźcach / Ukraińcach w Polsce: rzeczownik uchodźczy, albo „Ukraińcy” blisko „tutaj / w Polsce / przyjechali…”,
    albo „Ukraińcy” + sprawy socjalne (500+, PESEL, zasiłek, zbiórka…) lub wdzięczność / zdrowie / zachowanie."""
    t = text or ""
    if REFNOUN.search(t) or UKR_HERE.search(t):
        return True
    return bool(_UKR.search(t)) and bool(SOCIAL.search(t) or EXTRA.search(t))


# ---------------- wariant ŚCISŁY (zapowiedziany z góry, przed wynikami na pełnych danych) ----------------
def telegram_about_strict(text: str) -> bool:
    """Tylko rdzeń uchodźczy / migrancki / ochrona czasowa w pierwszych 300 znakach (bez frazy „Ukraińcy w Polsce”)."""
    return bool(TG_REFUGEE_CORE.search((text or "")[:TG_LEAD_CHARS]))


def x_about_strict(text: str) -> bool:
    """Tylko rzeczownik uchodźczy (uchodźca, uciekinier, imigrant, azyl...), bez luźnego „Ukraińcy” + „tu / w Polsce”."""
    return bool(REFNOUN.search(text or ""))
