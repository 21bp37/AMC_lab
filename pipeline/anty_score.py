"""Punktacja „anty” dla X (SZKIC v0.1, ręczne wagi bez uczenia) i bramka „o uchodźcach”.

Po co: leksykon z config.py ma na gold standardzie precyzję ok. 0,4–0,5 i czułość ok. 0,3–0,6. Punktacja zlicza cechy tekstu
(zagrożenie, koszt, uogólnienie, obelga, Wołyń/UPA, wykluczenie, Ukraińcy jako podmiot negatywnych czynności, „Ukraińcy” blisko
„w Polsce”) i odejmuje cechy przeciwne (obrona, kontekst rosyjski, krytyka rządu). Wagi są ustalone ręcznie, nie uczone, bo na 100
etykietach uczenie się przeucza. Punktacja służy tu głównie do WARSTWOWANIA próby tury 3 (więcej treści „anty” przy tej samej liczbie
koderów); jej jakość trzeba dopiero zmierzyć na tej turze. Zamroź wersję (VERSION, wagi, progi) w changelogu PRZED kodowaniem.
"""
from __future__ import annotations

import re

VERSION = "0.1"
THRESH_HIGH = 1.5      # punktacja >= HIGH: warstwa A
THRESH_MID = 0.5       # MID <= punktacja < HIGH: warstwa B; poniżej: C (bramka spełniona) lub D (bez bramki)

I = re.I
_URL = re.compile(r"https?://\S+|t\.co/\S+|www\.\S+")
_MENTION = re.compile(r"(?<!\w)@\w+")


def _c(p: str) -> re.Pattern:
    return re.compile(p, I)


FEATURES = {
    "zagrozenie": (1, _c(r"hiv\b|choroby|gruźlic|zaraz|epidemi|gwałt|morderst|mordow|rzeź|ludobójstw|przestęp|kradzie|bandy[tc]|terror")),
    "koszt": (1, _c(r"socjal|500\s?\+|800\s?\+|zasiłk|za darmo|za nic|na nasz koszt|nasz\w* podatk|z naszych podatk|kosztem polak|"
                    r"uprzywilej|pierwszeństw|zabier\w* (?:nam )?(?:prac|mieszka|miejsc)|wyciąg\w+ (?:kas|pieniądz)|utrzym\w+ (?:ich|ukrai)")),
    "uogolnienie": (1, _c(r"\bci ukra|wszyscy ukra|ukraińcy (?:zawsze|się nie zmienili|tylko|po prostu|są tacy|jak)|oni zawsze|taka nacja|ich mentaln|tacy są")),
    "obelga": (1, _c(r"dzicz|hołot|bydł|patolog|cwaniak|pasożyt|nachlebn|złodziej|ścierw|świni|zjeb|debil|idiot|chamstw|cham\b|prymityw|"
                     r"roszczeniow|niewdzięcz|bezczeln|\bukry\b|ukropy")),
    "wolyn": (1, _c(r"wołyń|rzeź\w* wołyńsk|upa\b|banderow|stepan bander|zbrodni\w* (?:upa|ukraińsk)|ludobójstw\w* (?:wołyń|ukrai)")),
    "wykluczenie": (1, _c(r"wracaj|niech wracaj|wynosz|wynoś|wypier|precz|do siebie|nie chcemy|dość tego|dosyć|wyjech|deportac|wydal|zamknąć granic|nie powinni")),
    "podmiot_neg": (1, _c(r"ukra[ińi]*[nń]c\w* (?:nie |tylko |po |już |znowu )?(?:przyjeżdż|biorą|pobierają|żądają|wymagają|roszcz|parkują|"
                          r"kradną|mordują|zabijają|atakują|okradają|wchodz)")),
    "obrona": (-1, _c(r"wdzięczn|dziękuj|chwała|slava|sława|pomoc|pomag|gościn|solidarn|wspier|bracia|witamy|szanuj|człowiek|ludzi|"
                      r"uciekają przed wojn|nie wolno|wstyd|hańb")),
    "rusek": (-1, _c(r"ruski|ruscy|ruskich|rosja|rosyjsk|putin|kacap|onuc|sowiec|kreml|ruskie|moskal")),
    "krytyka_wl": (-1, _c(r"\bpis\b|morawieck|kaczyńsk|rząd\w* |tusk|konfederac|duda|polityk")),
    "ukr_w_pl": (0.5, _c(r"ukra[ińi]*[nń]c\w*[^.!?\n]{0,60}(?:w polsce|tutaj|u nas|tu\b)|(?:w polsce|tutaj|u nas)[^.!?\n]{0,60}ukra[ińi]*[nń]c")),
}


def normalize(text: str) -> str:
    """Bez adresów, loginów i znaczników anonimizacji (surowy tekst i arkusz kodera dają ten sam wynik)."""
    t = _URL.sub("", str(text))
    t = _MENTION.sub("", t)
    return t.replace("[link]", "")


def hits(text: str) -> list[str]:
    t = normalize(text)
    return [k for k, (_, p) in FEATURES.items() if p.search(t)]


def score(text: str) -> float:
    t = normalize(text)
    return float(sum(w for w, p in FEATURES.values() if p.search(t)))


# ------------------------------------------------------------------ bramka „o uchodźcach / Ukraińcach w Polsce” (X-F)
_UKR = r"ukra[ińi]*[nń]c|ukrainiec|ukrainek|ukrainka|ukraińsk\w+ (?:uchodź|rodzin|dziec|kobiet|matk)"
_REFNOUN = _c(r"uchodź|uciekin|uciekaj\w+ przed wojn|przesiedle|imigran|migran|azyl")
_PL_HERE = (r"w polsce|tutaj|tu\b|u nas|do polski|w kraju|przyjecha|przyjeżdż|wjecha|osiedl|przyjmuj|przyjęt|pobiera|pobierają|mieszka")
_UKR_HERE = _c(r"(?:%s)[^.!?\n]{0,70}(?:%s)|(?:%s)[^.!?\n]{0,70}(?:%s)" % (_UKR, _PL_HERE, _PL_HERE, _UKR))
_SOCIAL = _c(r"500\s?\+|800\s?\+|socjal|pesel|zasiłk|świadcze|zbiórk|pomoc\w* (?:ukrai|uchodź|humanitar)|"
             r"zabier\w* (?:nam )?(?:prac|mieszka)|szczepi|szpital|lekarz|szko[łl]")
_EXTRA = _c(r"wdzięczn|dziękuj|dziękujemy|pomoc\w* (?:wojskow|społeczn)|nie chcieli uciekać|przyjazd\w* osób|hiv\b|dzicz|parkuj|"
            r"ukraińc\w* (?:od lat|zawsze|się nie zmienili)")
_UKR_RE = _c(_UKR)


def gate(text: str) -> bool:
    """Bramka X-F: czy post jest (prawdopodobnie) o uchodźcach / Ukraińcach w Polsce. Zob. reports/REGULY_PORUWNANIE.md."""
    t = str(text)
    if _REFNOUN.search(t) or _UKR_HERE.search(t):
        return True
    return bool(_UKR_RE.search(t)) and bool(_SOCIAL.search(t) or _EXTRA.search(t))


# ------------------------------------------------------------------ warstwy próby
STRATA = ["A_wysoka", "B_srednia", "C_niska_bramka", "D_niska_bez_bramki"]


def stratum(text: str) -> str:
    s = score(text)
    if s >= THRESH_HIGH:
        return STRATA[0]
    if s >= THRESH_MID:
        return STRATA[1]
    return STRATA[2] if gate(text) else STRATA[3]
