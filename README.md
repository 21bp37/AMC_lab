# Oszustwa z deepfake'ami: skala i czas życia reklam scamowych z wizerunkiem znanych osób

Repozytorium projektu zespołowego na kurs: praca o zjawisku społecznym, zweryfikowana dowodami empirycznymi. Temat: **Oszustwa z deepfake'ami**. Pytanie projektowe: **„Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”** Pytanie badawcze: **jaka jest mediana czasu życia reklam typu deepfake scam i jak kształtuje się ich dzienna intensywność wyświetleń?** Źródło danych: głównie TikTok Commercial Content Library / API (dane z UE).

Repozytorium zawiera dokumentację metodologiczną projektu, narzędzia do obsługi danych i walidacji pomiaru, testy oraz zasady pracy zespołu. **Nie zawiera danych o reklamach** (zob. „Dane”).

## Status

Etap M1 (karta eksploracji danych): dokumenty są szkicami do redakcji, dane jeszcze nie dotarły. Miejsca, które muszą uzupełnić poszczególne role albo dane, są oznaczone placeholderami `{{Pnn: ...}}` z właścicielem w `00_rejestr_placeholderow.md`.

## Struktura

| Ścieżka | Zawartość |
|---|---|
| `00_rejestr_placeholderow.md` | rejestr placeholderów (P01–P31) z właścicielem i statusem oraz punktów decyzyjnych (D1–D9) |
| `01_plan_pomiaru_M1.md` | plan pomiaru: pytanie badawcze i hipoteza, definicje (czas życia, dzienna intensywność, populacja), dowód na scam, analiza błędów, wykonalność, ograniczenia |
| `02_codebook_v0.1.md` | codebook: zmienne, wartości, przypadki graniczne, procedura pilotażu |
| `03_specyfikacja_interfejsu_dane.md` | wymagany schemat tabeli danych, szkielet macierzy legalności i data statementu |
| `04_plan_instrumentu.md` | annotator oceniany: warianty, zasady, drzewo decyzji, wersjonowanie promptów |
| `05_gold_standard_i_walidacja.md` | losowanie próby, liczebność, annotacja referencyjna, ocena, korekta błędu |
| `06_rejestr_ryzyk.md` | ryzyka i ograniczenia (R01–R22) z właścicielem, środkiem zaradczym i wskaźnikiem z danych |
| `07_bibliografia.md` | źródła z adnotacją i statusem weryfikacji |
| `09_ujawnienie_AI_i_wklad.md` | ujawnienie użycia AI i tabela wkładu |
| `10_playbook_po_otrzymaniu_danych.md` | kolejność działań po otrzymaniu danych |
| `WORKFLOW.md` | zasady pracy w repozytorium: gałęzie, commity, własność miejsc, dane, sesje z AI |
| `tools/` | narzędzia w Pythonie (schemat zmiennych, ładowanie JSON z TikToka, audyt danych, losowanie, liczebność, zgodność annotatorów, ocena, estymatory, czas życia i intensywność, dziennik uruchomień, kontrole spójności) |
| `tests/` | testy narzędzi na danych syntetycznych |
| `templates/` | arkusz annotacji (CSV), dziennik zmian codebooka |
| `prompts/` | prompty annotatora ocenianego (puste do zamrożenia codebooka) |
| `logs/` | dziennik uruchomień `runs.jsonl` (hashe, bez danych) |
| `data_synthetic/` | dane syntetyczne do testów (`is_synthetic=1`); nie opisują zjawiska |
| `.github/` | CI (testy i kontrole spójności, brak plików danych w repozytorium) i szablon pull requesta |

Numeracja dokumentów jest ciągła z przerwą na 08 (miejsce zarezerwowane, brak pliku).

## Dane

Wszystkie dane pochodzą z legalnych źródeł, zgodnie z regulaminami stron i licencjami; **nie stosujemy scrapowania**. Dane o reklamach nie wchodzą do repozytorium (`.gitignore`, kontrola w CI). Przechowuje je inżynier danych w miejscu uzgodnionym w macierzy legalności (03). Pole z nazwiskami osób publicznych (`celeb_id`) istnieje tylko w plikach roboczych poza repozytorium. Zasady dotyczące danych osobowych: 04 (zasada 4), 06 (R09, R10).

## Uruchomienie

Wymagania: Python (testowane na 3.12 i 3.13), `pip install -r requirements.txt`. Narzędzia importują się wzajemnie, więc uruchamiaj je z katalogu głównego.

```
python -m unittest discover -s tests -v       # testy
python tools/checks.py consistency            # schema.yaml, codebook i szablon CSV
python tools/checks.py placeholders           # placeholdery w dokumentach i rejestr
python tools/audit_dataset.py dane.csv        # audyt tabeli dostarczonej przez inżyniera danych
python tools/sampling.py dane.csv --stratum S --advertiser A --cap 5 --n 30 --seed 1 --out proba.csv
python tools/load_tiktok_json.py plik.json --retrieval-date 2026-10-12 --out poza_repo/ads_flat.csv   # JSON z TikToka -> tabela (poza repozytorium)
python tools/sample_size.py positives         # szerokość CI a liczba pozytywów
python tools/outcomes.py dane.csv --class-col gold --weight-col weight   # mediana czasu życia, udział I >= próg, pasmo dla reklam aktywnych
python tools/agreement.py arkusz.csv --vars celeb_mention scam_type
python tools/evaluation.py predykcje.csv --true gold --pred model --label 1 --cluster advertiser_id --weight weight
python tools/prompt_robustness.py predykcje_long.csv --positive 1
python tools/run_log.py --log logs/runs.jsonl ...
```

Opisy parametrów: `python tools/<nazwa>.py --help`.

## Praca w repozytorium

Zasady (gałęzie, pull requesty, własność placeholderów, dane, sesje z AI) są w `WORKFLOW.md`. Każdy pull request przechodzi CI i ma wypełniony szablon z listą kontrolną.

## Role i odpowiedzialność

Placeholdery i ryzyka w dokumentach mają właściciela: **lead** (pytanie, hipoteza, pytanie i hipoteza, progi, definicje czasu życia i intensywności, skład annotatorów, stan wiedzy), **inżynier danych** (źródła, legalność, ramka, pola, data statement), **inżynier pipelinu** (codebook, gold standard, walidacja, analiza błędów), **analityk** (modele i korekty końcowe). Własność jest opisana w `00_rejestr_placeholderow.md`; wypełnia ją właściciel.

## Ograniczenia

- Dokumenty to szkice do redakcji; autorzy odpowiadają za treść po weryfikacji, a użycie AI jest opisane w `09_ujawnienie_AI_i_wklad.md`.
- Pozycje w `07_bibliografia.md` o statusie „do sprawdzenia” trzeba otworzyć przed cytowaniem.
- Estymator w `tools/estimators.py` jest uproszczony (częstość klasy), a `tools/outcomes.py` liczy medianę i udziały z pasmem dla reklam aktywnych; żadne z nich nie jest pełnym DSL dla regresji ani modelem przeżycia (05, sekcja 6).
- Dane źródła są zagregowane (suma wyświetleń za okres): dzienna intensywność jest średnią i nie pozwala potwierdzić taktyki *burst-and-burn* (06, R20).
- Progi oznaczone w 05 (sekcja 7) jako „heurystyka własna” nie pochodzą z literatury.
