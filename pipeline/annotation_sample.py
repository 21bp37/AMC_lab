"""Próba do ręcznej anotacji: ~100 treści z X + ~100 postów z Telegrama, losowanie warstwowe, tłumaczenie RU/UK -> PL.

Po co: walidacja pomiaru narracji (karta M1, sekcja 6, punkt „Narracje”). Koderzy oceniają stanowisko wobec Ukraińców
i uchodźców, a my porównujemy ich etykiety ze słownikiem (pipeline/annotation_check.py).

Warstwy (cechy znane PRZED anotacją, żeby każda klasa pojawiła się w próbie):
  X        : wynik słownika stance_lex = anti / pro / mieszane / brak            (jednostka: unikalna treść, jak w EDA)
  Telegram : strona kanału x flaga słownika anty-UA (anti / inne) x filtr uchodźczy (uch / bez)  (jednostka: unikalny tekst)
Jedna anotacja służy dwóm celom: ocenie słownika pro/anty oraz ocenie filtra uchodźczego (etykieta „nie_dotyczy” = post nie jest
o Ukraińcach / uchodźcach w Polsce, więc nie trzeba osobnej kolumny „czy o uchodźcach”; zob. annotation_check.py, sekcja 3b).
Warstwa „brak/inne” jest konieczna: bez niej nie zmierzymy czułości słownika i nie zobaczymy treści neutralnych.
Z każdego źródła (konto / kanał) bierzemy co najwyżej --cap treści, żeby kilka kont nie zdominowało próby.
Prawdopodobieństwa włączenia zapisujemy (kolumna weight), więc wyniki można przeliczyć na populację.

Wyjście w --out (domyślnie annotation_work/, w .gitignore, bo zawiera teksty i loginy):
  proba_master.csv            klucz: warstwa, flaga słownika, wagi, trafienia słownika (NIE dawać koderom)
  anotacja_<kod>.xlsx / .csv  arkusz kodera: id, źródło, tekst PL, oryginał, etykieta (lista), tłumaczenie, komentarz;
                              każdy koder dostaje inną kolejność, bez informacji o warstwie i słowniku
  proba_podsumowanie.json     liczebności warstw

Użycie (z katalogu repozytorium):
  python -m pipeline.annotation_sample --coders A B C --translator google
  python -m pipeline.annotation_sample --coders A B --translator none      # bez tłumaczenia (zrobisz je ręcznie)
Tłumaczenie: google = pakiet deep-translator (pip install deep-translator, wymaga internetu; darmowa usługa bywa blokowana: błąd 429),
             deepl  = DeepL API przez deep-translator (darmowy klucz w zmiennej DEEPL_API_KEY),
             argos  = argostranslate (offline po jednorazowym pobraniu modeli), none = pomiń.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import config

sys.path.insert(0, str(config.ROOT / "tools"))
import sampling  # noqa: E402

LABELS = ["anty", "pro", "neutralne", "nie_dotyczy", "niejasne"]
LABEL_HELP = {
    "anty": "wypowiedź przedstawia Ukraińców / uchodźców z Ukrainy w Polsce negatywnie lub wrogo (roszczeniowość, nadużywanie "
            "świadczeń, przestępczość, zagrożenie dla Polaków, „banderyzm” jako zarzut wobec ludności), albo wzywa do działań przeciw nim",
    "pro": "wypowiedź przedstawia ich pozytywnie lub ich broni (pomoc, solidarność, wdzięczność, obrona przed hejtem i fałszywymi zarzutami)",
    "neutralne": "dotyczy Ukraińców / uchodźców w Polsce, ale bez wyraźnej oceny (informacja, pytanie, relacja, komunikat urzędowy)",
    "nie_dotyczy": "nie jest o Ukraińcach / uchodźcach jako ludziach w Polsce (np. sama wojna, armia, polityka międzynarodowa, "
                   "spam, treść o czymś innym)",
    "niejasne": "nie da się ocenić (urwany tekst, zły przekład, brak kontekstu, ironia nie do rozstrzygnięcia)",
}
RULES = [
    "Oceniamy stanowisko wobec Ukraińców / uchodźców w Polsce, a nie ogólny ton wpisu. Złość na Rosję, rząd lub Zachód to NIE jest „anty”.",
    "Wrogość wobec państwa, armii lub władz Ukrainy bez odniesienia do ludności w Polsce → „nie_dotyczy” (to nie jest narracja o uchodźcach).",
    "Cytat lub parafraza cudzego hejtu w celu jego obalenia → „pro”; cytat bez wyraźnej oceny → „neutralne”.",
    "Przy wątpliwościach wybierz „niejasne” i opisz powód w kolumnie „komentarz”. Nie konsultujcie się z innymi koderami.",
    "W Telegramie tekst jest tłumaczeniem maszynowym z rosyjskiego / ukraińskiego. Jeśli przekład jest niezrozumiały, zaznacz „słabe” w kolumnie „tlumaczenie”.",
    "Nie sprawdzaj w internecie, kto jest autorem, i nie zgaduj, co zaznaczył słownik: sprawdzamy, co mówi sam tekst.",
]

# Liczebności warstw przy n = 100 (skalowane, gdy podasz inne --n-x / --n-tg)
X_ALLOC = {"anti": 30, "pro": 25, "mieszane": 10, "brak": 35}
# Telegram: strona x flaga słownika anty-UA x filtr uchodźczy (uch = przepuszczony, bez = odrzucony). Więcej z „uch”, bo test hipotezy
# będzie liczony na postach po filtrze; „bez” potrzebne do oceny, ile postów uchodźczych filtr gubi.
TG_ALLOC = {f"{side}|{a}|{u}": n for side in ("Pro-Russian", "Pro-Ukrainian")
            for a, u, n in (("anti", "uch", 15), ("inne", "uch", 15), ("anti", "bez", 8), ("inne", "bez", 12))}

URL_RE = re.compile(r"https?://\S+|t\.co/\S+|www\.\S+")
MENTION_RE = re.compile(r"(?<!\w)@\w+")
MAX_CHARS = 1200       # dłuższe teksty skracamy (czytelność i limit tłumaczenia)
MIN_CHARS_X = 15
MIN_CHARS_TG = 30
ANNOT_DIR = config.ROOT / "annotation_work"


def use_utf8_console() -> None:
    """Windows (cp1250) nie umie wypisać np. „≥”, „κ”, „α” i wysypuje print(); wymuszamy UTF-8 (w razie czego znaki zastępcze zamiast błędu)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def num(n) -> str:
    return f"{int(n):,}".replace(",", " ")


def log(msg: str) -> None:
    """Komunikat z godziną (od razu na ekran, także przy długich krokach)."""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_posts_verbose(pattern: str) -> pd.DataFrame:
    """Jak eda_telegram.load_posts, ale z postępem po plikach (przy 4-8 dużych plikach widać, że coś się dzieje)."""
    import glob
    from pipeline import eda_telegram
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"Brak plików pasujących do {pattern}. Najpierw uruchom filtr_telegram.py.")
    frames = []
    for i, f in enumerate(files, 1):
        d, _ = eda_telegram.load_posts(f)
        frames.append(d)
        log(f"  plik {i}/{len(files)}: {Path(f).name}, {num(len(d))} postów")
    return pd.concat(frames, ignore_index=True).drop_duplicates(["peer_id", "id"])


# --------------------------------------------------------------------------- liczebności warstw
def scale_alloc(alloc: dict, n: int) -> dict:
    """Skaluje liczebności warstw do łącznej liczby n (metoda największych reszt)."""
    tot = sum(alloc.values())
    raw = {k: v * n / tot for k, v in alloc.items()}
    out = {k: int(np.floor(v)) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True)[: n - sum(out.values())]:
        out[k] += 1
    return out


def fit_alloc(alloc: dict, available: dict) -> dict:
    """Przycina liczebności do dostępnych w warstwie; niedobór oddaje warstwom z zapasem (proporcjonalnie do planu)."""
    out = {k: min(v, int(available.get(k, 0))) for k, v in alloc.items()}
    missing = sum(alloc.values()) - sum(out.values())
    while missing > 0:
        spare = {k: int(available.get(k, 0)) - out[k] for k in out if int(available.get(k, 0)) - out[k] > 0}
        if not spare:
            break
        wsum = sum(alloc[k] for k in spare)
        gave = 0
        for k in sorted(spare, key=lambda k: alloc[k], reverse=True):
            add = min(spare[k], max(1, int(round(missing * alloc[k] / wsum))), missing - gave)
            out[k] += add
            gave += add
            if gave >= missing:
                break
        if gave == 0:
            break
        missing -= gave
    return out


def draw(frame: pd.DataFrame, alloc: dict, source_col: str, cap: int, seed: int) -> pd.DataFrame:
    """Losowanie warstwowe z limitem na źródło; zwraca próbę z kolumnami weight, stratum_N, stratum_n."""
    avail = frame.groupby("stratum").size().to_dict()
    fitted = fit_alloc(alloc, avail)
    short = {k: (alloc[k], fitted[k], avail.get(k, 0)) for k in alloc if fitted[k] < alloc[k]}
    if short:
        print(f"UWAGA: niedobór w warstwach (plan, wzięto, dostępne): {short}")
    fitted = {k: v for k, v in fitted.items() if v > 0}
    return sampling.stratified_sample(frame[frame["stratum"].isin(fitted)], "stratum", fitted,
                                      advertiser_col=source_col, cap_per_advertiser=cap, seed=seed)


# --------------------------------------------------------------------------- ramki źródłowe
def lex_hits(low_text: str, patterns: dict, limit: int = 8) -> str:
    """Które reguły słownika zadziałały i na jakim fragmencie (do analizy fałszywych trafień)."""
    out = []
    for name, pat in patterns.items():
        for m in re.finditer(pat, low_text):
            out.append(f"{name}:{m.group(0).strip()}")
            if len(out) >= limit:
                return "; ".join(out)
    return "; ".join(out)


def x_frame(path) -> pd.DataFrame:
    """Unikalne treści z X w oknie analizy (jak w EDA): jedna reprezentacja na kaskadę, preferujemy pełny tekst oryginału."""
    from pipeline import load_twitter
    log(f"X: wczytuję {Path(path).name} ...")
    raw = load_twitter.load_raw(path)
    log(f"X: {num(len(raw))} wierszy; liczę kaskady, flagi słownika, stanowisko ...")
    df = load_twitter.normalize(raw)
    df = df[(df["day"] >= config.EFFECTIVE_START) & (df["day"] <= config.STUDY_END)].copy()
    df["_pref"] = df["truncated"].astype(int) * 2 + (df["type"] != "original").astype(int)
    df = df.sort_values(["_pref", "ts"]).drop_duplicates("cascade_key")
    df = df[df["clean_text"].map(content_len) >= MIN_CHARS_X]
    log(f"X: {num(len(df))} unikalnych treści w oknie; warstwy: " +
        ", ".join(f"{k} {v}" for k, v in df["stance_lex"].value_counts().items()))
    return pd.DataFrame({
        "platform": "X", "source_id": df["cascade_key"], "source_group": df["source_author"], "date": df["day"].dt.date.astype(str),
        "side": "", "text_original": df["clean_text"], "stratum": df["stance_lex"], "lexicon_label": df["stance_lex"],
        "truncated": df["truncated"], "refugee_filter": "", "refugee_hits": "",
    }).reset_index(drop=True)


def tg_frame(posts_glob: str, clusters_csv: str) -> pd.DataFrame:
    """Unikalne teksty z Telegrama (po filtrze Ukraina+Polska, okno analizy), tylko kanały ze znaną stroną."""
    from pipeline import eda_telegram
    log("Telegram: wczytuję pliki z postami ...")
    raw = load_posts_verbose(posts_glob)
    log(f"Telegram: razem {num(len(raw))} postów; stosuję okno, filtr Ukraina+Polska i dopasowuję strony kanałów ...")
    df = eda_telegram.prepare(raw, clusters_csv)
    log(f"Telegram: po filtrze UA+PL w oknie: {num(len(df))} postów")
    df = df[df["side"].isin(["Pro-Russian", "Pro-Ukrainian"])].copy()
    df = df[df["message"].fillna("").map(content_len) >= MIN_CHARS_TG]
    df = df.sort_values("ts").drop_duplicates("copy_key")          # kopie tego samego tekstu liczymy raz
    from pipeline import telegram_refugee                          # import tutaj: moduł filtra importuje ten plik
    fl = telegram_refugee.flag(df["message"])
    df = df.assign(is_refugee=fl["is_refugee"].to_numpy(), refugee_hits=fl["refugee_hits"].to_numpy())
    log(f"Telegram: {num(len(df))} unikalnych tekstów ze znaną stroną kanału; przepuszczone przez filtr uchodźczy: "
        f"{num(df['is_refugee'].sum())} ({100 * df['is_refugee'].mean():.0f}%)")
    return pd.DataFrame({
        "platform": "Telegram", "source_id": df["peer_id"].astype(str) + "/" + df["id"].astype(str),
        "source_group": df["peer_id"].astype(str), "date": df["day"].dt.date.astype(str), "side": df["side"],
        "text_original": df["message"],
        "stratum": df["side"] + "|" + np.where(df["is_anti"], "anti", "inne") + "|" + np.where(df["is_refugee"], "uch", "bez"),
        "lexicon_label": np.where(df["is_anti"], "anti", "brak"), "truncated": False,
        "refugee_filter": np.where(df["is_refugee"], "tak", "nie"), "refugee_hits": df["refugee_hits"],
    }).reset_index(drop=True)


# --------------------------------------------------------------------------- tłumaczenie
def detect_lang(text: str) -> str:
    return "uk" if re.search(r"[іїєґІЇЄҐ]", text) else "ru"


def make_translator(kind: str):
    """Zwraca funkcję (tekst, język_źródłowy) -> tekst PL albo None dla kind='none'."""
    if kind == "none":
        return None
    if kind == "google":
        try:
            from deep_translator import GoogleTranslator       # pip install deep-translator
        except ImportError:
            raise SystemExit("Brak pakietu deep-translator: pip install deep-translator (albo --translator none / argos)")
        return lambda t, lang: GoogleTranslator(source=lang, target="pl").translate(t)
    if kind == "deepl":
        import os
        key = os.environ.get("DEEPL_API_KEY", "").strip()
        if not key:
            raise SystemExit("Brak klucza DeepL. Darmowy klucz (500 tys. znaków miesięcznie): deepl.com/pro-api. "
                             "Potem w Git Bashu: export DEEPL_API_KEY=twoj_klucz   (klucze darmowe kończą się na :fx)")
        try:
            import requests
        except ImportError:
            raise SystemExit("Brak pakietu requests: pip install requests")
        url = ("https://api-free.deepl.com" if key.endswith(":fx") else "https://api.deepl.com") + "/v2/translate"
        langs = {"ru": "RU", "uk": "UK"}

        def deepl(t, lang):
            r = requests.post(url, headers={"Authorization": f"DeepL-Auth-Key {key}"},
                              json={"text": [t], "source_lang": langs.get(lang, lang.upper()), "target_lang": "PL"}, timeout=30)
            if r.status_code != 200:
                raise RuntimeError(f"DeepL HTTP {r.status_code}: {r.text[:200]}")
            return r.json()["translations"][0]["text"]
        return deepl
    if kind == "argos":
        import argostranslate.package as pkg                   # pip install argostranslate
        import argostranslate.translate as tr
        need = [("ru", "en"), ("uk", "en"), ("en", "pl")]
        have = {(a.code, b.code) for a in tr.get_installed_languages() for b in tr.get_installed_languages()
                if a.get_translation(b) is not None}
        if not all(n in have for n in need):
            pkg.update_package_index()
            for p in pkg.get_available_packages():
                if (p.from_code, p.to_code) in need:
                    pkg.install_from_path(p.download())
        return lambda t, lang: tr.translate(t, lang, "pl")
    raise SystemExit(f"Nieznany translator: {kind} (google | deepl | argos | none)")


class TranslationUnavailable(RuntimeError):
    """Tłumacz zawodzi od pierwszych tekstów (blokada, limit, brak sieci): nie ma sensu męczyć go dalej."""


def translate_all(texts: pd.Series, translator, cache_path: Path, retries: int = 3, log_every: int = 10) -> tuple[list[str], list[str]]:
    """Tłumaczy teksty z cache (żeby ponowne uruchomienie nie tłumaczyło od nowa). Zwraca (tłumaczenia, statusy)."""
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    out, status = [], []
    total, n_cache, n_err = len(texts), 0, 0
    for k, t in enumerate(texts, 1):
        key = hashlib.sha1(t.encode("utf-8")).hexdigest()
        if key in cache:
            out.append(cache[key]); status.append("ok"); n_cache += 1
            if k % log_every == 0 or k == total:
                log(f"  tłumaczenie {k}/{total} (z cache: {n_cache}, błędy: {n_err})")
            continue
        res, err = None, ""
        for attempt in range(retries):
            try:
                res = translator(t, detect_lang(t))
                break
            except Exception as e:                              # noqa: BLE001 — sieć/limit zewnętrznego API
                err = repr(e)[:120]
                time.sleep(1.5 * (attempt + 1))
        if res:
            cache[key] = res; out.append(res); status.append("ok")
        else:
            out.append(""); status.append(f"blad: {err}"); n_err += 1
            if n_err <= 2:
                log(f"  BŁĄD tłumaczenia ({k}/{total}): {err}")
            if n_err >= 3 and n_err == k - n_cache:          # nic jeszcze się nie udało
                raise TranslationUnavailable(err)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        if k % log_every == 0 or k == total:
            log(f"  tłumaczenie {k}/{total} (z cache: {n_cache}, błędy: {n_err})")
    return out, status


# --------------------------------------------------------------------------- arkusze koderów
def anonymize(t: str) -> str:
    """Koderzy (i tłumacz) nie widzą loginów ani adresów: @login -> @użytkownik, adres -> [link]."""
    return MENTION_RE.sub("@użytkownik", URL_RE.sub("[link]", str(t)))


def content_len(t: str) -> int:
    """Długość treści bez adresów i wzmianek (wpis typu „@ktoś https://t.co/…” nie ma czego oceniać)."""
    return len(MENTION_RE.sub("", URL_RE.sub("", str(t))).strip())


def clip(t: str) -> str:
    t = re.sub(r"[ \t]+", " ", str(t)).strip()
    return t if len(t) <= MAX_CHARS else t[:MAX_CHARS].rsplit(" ", 1)[0] + " […]"


def coder_view(master: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Co widzi koder: bez warstwy, słownika, strony kanału i autora. Własna, losowa kolejność."""
    d = master.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    is_tg = d["platform"] == "Telegram"
    return pd.DataFrame({
        "id": d["item_id"], "zrodlo": d["platform"],
        "tekst_pl": np.where(is_tg & (d["text_pl"] == ""), "(brak tłumaczenia, patrz tekst_oryg)", d["text_pl"]),
        "tekst_oryg": np.where(is_tg, d["text_original"], ""),
        "etykieta": "", "tlumaczenie": "", "komentarz": "",
    })


def write_xlsx(path: Path, view: pd.DataFrame, coder: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Anotacja"
    ws.append(list(view.columns))
    for row in view.itertuples(index=False):
        ws.append(list(row))
    widths = {"id": 8, "zrodlo": 10, "tekst_pl": 70, "tekst_oryg": 50, "etykieta": 14, "tlumaczenie": 13, "komentarz": 35}
    head_fill = PatternFill("solid", fgColor="DDEBF7")
    for i, col in enumerate(view.columns, start=1):
        letter = ws.cell(row=1, column=i).column_letter
        ws.column_dimensions[letter].width = widths.get(col, 15)
        ws.cell(row=1, column=i).font = Font(bold=True)
        ws.cell(row=1, column=i).fill = head_fill
    wrap = Alignment(wrap_text=True, vertical="top")
    fill_in = PatternFill("solid", fgColor="FFF2CC")
    for r in range(2, ws.max_row + 1):
        for c in range(1, len(view.columns) + 1):
            ws.cell(row=r, column=c).alignment = wrap
        ws.cell(row=r, column=5).fill = fill_in
    ws.freeze_panes = "C2"
    last = ws.max_row
    dv = DataValidation(type="list", formula1='"' + ",".join(LABELS) + '"', allow_blank=True, showErrorMessage=True,
                        errorTitle="Etykieta", error="Wybierz jedną etykietę z listy.")
    dv2 = DataValidation(type="list", formula1='"ok,słabe"', allow_blank=True)
    ws.add_data_validation(dv); ws.add_data_validation(dv2)
    dv.add(f"E2:E{last}"); dv2.add(f"F2:F{last}")

    ins = wb.create_sheet("Instrukcja")
    ins.column_dimensions["A"].width = 16
    ins.column_dimensions["B"].width = 120
    ins.append([f"Koder {coder}", "Przypisz każdemu wierszowi dokładnie jedną etykietę w kolumnie „etykieta” (żółta, lista rozwijana)."])
    ins.append([])
    ins.append(["Etykieta", "Znaczenie"])
    for l in LABELS:
        ins.append([l, LABEL_HELP[l]])
    ins.append([])
    ins.append(["Zasady", ""])
    for i, r in enumerate(RULES, 1):
        ins.append([i, r])
    for row in ins.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in (ins["A3"], ins["B3"]):
        cell.font = Font(bold=True)
    wb.save(path)


# --------------------------------------------------------------------------- główny przebieg
def build_master(x_df: pd.DataFrame, tg_df: pd.DataFrame, n_x: int, n_tg: int, cap: int, seed: int) -> pd.DataFrame:
    parts = []
    if len(x_df) and n_x:
        s = draw(x_df, scale_alloc(X_ALLOC, n_x), "source_group", cap, seed)
        low = s["text_original"].str.lower()
        s["lex_hits"] = [lex_hits(t, {**config.ANTI_UA_NARRATIVES, **{"pro_" + k: v for k, v in config.PRO_UA_NARRATIVES.items()}}) for t in low]
        parts.append(s)
    if len(tg_df) and n_tg:
        s = draw(tg_df, scale_alloc(TG_ALLOC, n_tg), "source_group", cap, seed + 1)
        s["lex_hits"] = [lex_hits(t, {"anti_ru_uk": config.TELEGRAM_ANTI_UA}) for t in s["text_original"]]
        parts.append(s)
    if not parts:
        raise SystemExit("Pusta próba: podaj dane X (--twitter) i/lub Telegrama (--posts, --clusters).")
    m = pd.concat(parts, ignore_index=True)
    m["text_original"] = m["text_original"].map(lambda t: clip(anonymize(t)))   # trafienia słownika policzone wcześniej na surowym tekście
    m = m.sample(frac=1.0, random_state=seed + 2).reset_index(drop=True)
    m.insert(0, "item_id", [f"P{i:03d}" for i in range(1, len(m) + 1)])
    m["text_pl"] = np.where(m["platform"] == "X", m["text_original"], "")
    m["translation_status"] = np.where(m["platform"] == "X", "nie dotyczy", "brak")
    m["lexicon_version"] = config.LEXICON_VERSION
    return m


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--twitter", default=str(config.RAW_TWITTER))
    ap.add_argument("--posts", default=str(config.ROOT / "data" / "telegram" / "posts_2022_part_*.csv"))
    ap.add_argument("--clusters", default=str(config.ROOT / "data" / "telegram" / "leiden_clusters.csv"))
    ap.add_argument("--n-x", type=int, default=100)
    ap.add_argument("--n-tg", type=int, default=100)
    ap.add_argument("--cap", type=int, default=3, help="maks. treści z jednego konta / kanału w jednej warstwie")
    ap.add_argument("--coders", nargs="+", default=["A", "B"], help="kody koderów, np. A B C (C może być modelem językowym)")
    ap.add_argument("--translator", choices=["google", "deepl", "argos", "none"], default="google")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(ANNOT_DIR))
    ap.add_argument("--from-master", action="store_true",
                    help="pomiń kroki 1-3: weź próbę z istniejącego proba_master.csv (np. po naprawie tłumacza) i tylko przetłumacz / zapisz arkusze")
    args = ap.parse_args(argv)
    use_utf8_console()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if args.from_master:
        log(f"Pomijam kroki 1-3: wczytuję próbę z {out / 'proba_master.csv'}")
        master = pd.read_csv(out / "proba_master.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
        for c in ("weight", "stratum_N", "stratum_n", "inclusion_prob"):
            if c in master.columns:
                master[c] = pd.to_numeric(master[c])
        master["text_pl"] = np.where(master["platform"] == "X", master["text_original"], master["text_pl"])
    else:
        log("Krok 1/5: dane z X")
        x_df = x_frame(args.twitter) if args.n_x and Path(args.twitter).exists() else pd.DataFrame()
        log("Krok 2/5: dane z Telegrama")
        tg_df = tg_frame(args.posts, args.clusters) if args.n_tg else pd.DataFrame()
        log("Krok 3/5: losowanie warstwowe")
        master = build_master(x_df, tg_df, args.n_x, args.n_tg, args.cap, args.seed)
        log(f"  wylosowano {len(master)} treści (X {int((master['platform'] == 'X').sum())}, Telegram {int((master['platform'] == 'Telegram').sum())})")
        master.to_csv(out / "proba_master.csv", index=False, encoding="utf-8-sig")      # zapis przed tłumaczeniem

    log(f"Krok 4/5: tłumaczenie postów z Telegrama ({args.translator})")
    tr = make_translator(args.translator)
    is_tg = master["platform"] == "Telegram"
    if tr is not None and is_tg.any():
        try:
            tl, st = translate_all(master.loc[is_tg, "text_original"], tr, out / "translation_cache.json")
            master.loc[is_tg, "text_pl"] = [clip(t) for t in tl]
            master.loc[is_tg, "translation_status"] = st
            bad = sum(s != "ok" for s in st)
            if bad:
                print(f"UWAGA: {bad} tłumaczeń się nie powiodło (patrz translation_status w proba_master.csv); "
                      f"uruchom z --from-master, udane są w cache.")
        except TranslationUnavailable as e:
            log("TŁUMACZENIE NIE DZIAŁA: " + str(e))
            log("  Zapisuję arkusze bez tłumaczenia. Napraw tłumacza (zob. niżej) i uruchom to samo polecenie z --from-master "
                "(losowanie się nie powtórzy).")
            log("  Test tłumacza: python -c \"from deep_translator import GoogleTranslator as G; "
                "print(G(source='ru', target='pl').translate('Беженцы из Украины'))\"")
            log("  Inne wyjścia: --translator argos (offline) albo --translator none i ręczne wklejenie tekstów z kolumny tekst_oryg do DeepL / Google Translate.")
    else:
        log("  pomijam tłumaczenie (--translator none lub brak postów z Telegrama)")
    master.to_csv(out / "proba_master.csv", index=False, encoding="utf-8-sig")

    log("Krok 5/5: zapis arkuszy dla koderów")
    for i, code in enumerate(args.coders):
        view = coder_view(master, args.seed + 100 + i)
        write_xlsx(out / f"anotacja_{code}.xlsx", view, code)
        view.to_csv(out / f"anotacja_{code}.csv", index=False, sep=";", encoding="utf-8-sig")

    summ = (master.groupby(["platform", "stratum"]).agg(N=("stratum_N", "first"), n=("stratum_n", "first"),
                                                          waga_sr=("weight", "mean")).reset_index())
    (out / "proba_podsumowanie.json").write_text(summ.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
    print(summ.to_string(index=False))
    log(f"Gotowe w {time.time() - t0:.0f} s.")
    print(f"\nZapisano w {out}: proba_master.csv (klucz, NIE dla koderów) oraz anotacja_<kod>.xlsx/.csv dla: {', '.join(args.coders)}")


if __name__ == "__main__":
    main()
