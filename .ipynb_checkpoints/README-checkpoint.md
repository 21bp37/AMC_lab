# Pipeline M1: skala i czas życia reklam scamowych z wizerunkiem znanych osób (rola: inżynier pipelinu)

Materiały przygotowawcze do karty eksploracji danych (M1) **bez dostępu do danych**. Zakres: codebook, gold standard, walidacja annotatora ocenianego, analiza błędów. Miejsca leada i inżyniera danych są tylko placeholderami z oznaczeniem właściciela (**[LEAD]**, **[INŻ. DANYCH]**, **[PIPELINE]**, **[ANALITYK]**). Jeden plik na artefakt; dokumenty można złożyć w jeden plik Word z kartą M1 (patrz niżej).

## Zawartość

| Plik | Co to jest |
|---|---|
| `00_rejestr_placeholderow.md` | rejestr placeholderów `{{Pnn}}` i punktów decyzyjnych D1–D9 |
| `01_plan_pomiaru_M1.md` | wkład do karty M1: co mierzy pipeline, definicje, dowód na scam, analiza błędów, wykonalność, ograniczenia (pytanie i hipoteza: placeholdery leada) |
| `02_codebook_v0.1.md` | codebook (źródło wartości: `tools/schema.yaml`) |
| `03_specyfikacja_interfejsu_dane.md` | czego potrzeba od inżyniera danych; szkielet macierzy legalności i data statementu |
| `04_plan_instrumentu.md` | annotator oceniany: macierz alternatyw, drzewo decyzji, reguły promptów |
| `05_gold_standard_i_walidacja.md` | próba, liczebność, annotacja referencyjna, ocena annotatora ocenianego, wpływ błędu na skalę i czas życia, korekta błędu |
| `06_rejestr_ryzyk.md` | ryzyka z środkami zaradczymi i wskaźnikami z danych |
| `07_bibliografia.md` | źródła ze statusem weryfikacji |
| `09_ujawnienie_AI_i_wklad.md` | ujawnienie użycia AI i tabela wkładu |
| `10_playbook_po_otrzymaniu_danych.md` | kroki po otrzymaniu danych |
| `tools/` | narzędzia (działają na dowolnej tabeli; **brak kodu pobierającego dane z sieci**) |
| `tests/` | testy narzędzi na danych syntetycznych |
| `templates/` | arkusz annotacji (CSV), dziennik zmian codebooka |
| `WORKFLOW.md`, `.github/`, `requirements.txt`, `.gitignore` | zasady pracy w repozytorium, CI (testy, kontrole spójności, brak danych w repo), szablon PR |
| `prompts/`, `logs/` | prompty annotatora ocenianego i dziennik uruchomień (puste do czasu zamrożenia codebooka) |
| `data_synthetic/` | dane SYNTETYCZNE do testów; nie są danymi o zjawisku |

## Narzędzia (wywołanie z katalogu głównego)

```
python tools/audit_dataset.py dane.csv                       # audyt tabeli od inżyniera danych
python tools/sampling.py dane.csv --stratum S --advertiser A --cap 5 --n 30 --seed 1 --out proba.csv
python tools/sample_size.py positives                        # szerokość CI a liczba pozytywów
python tools/agreement.py arkusz.csv --vars celeb_mention scam_type
python tools/evaluation.py predykcje.csv --true gold --pred model --label 1 --cluster advertiser_id --weight weight
python tools/prompt_robustness.py predykcje_long.csv --positive 1
python tools/run_log.py --log runs/runs.jsonl ...            # dziennik uruchomień
python tools/checks.py consistency | placeholders | sheet arkusz.csv
python -m unittest discover -s tests -v
```

Wymagania: Python 3.10+, numpy, pandas, scipy, pyyaml. Narzędzia z `tools/` importują się wzajemnie, więc uruchamiaj je z katalogu głównego.

## Składanie w jeden plik Word

```
python build/build_docx.py            # tworzy build/M1_pipeline.docx
```

Wymaga `pandoc` i `python-docx`. Placeholdery `{{Pnn: ...}}` są w pliku Word podświetlone na żółto. Kolejność plików: 00, 01, 02, 03, 04, 05, 06, 07, 09, 10.

## Ograniczenia, o których trzeba pamiętać

- Wszystko to są **szkice do redakcji**; oceniane jest zrozumienie i wkład własny (09).
- Statusy źródeł w `07_bibliografia.md`: pozycje „do sprawdzenia" otwórz przed cytowaniem.
- Estymator w `tools/estimators.py` jest uproszczony (częstość), a nie pełnym DSL dla regresji (05, sekcja 6).
- Liczby w tabelach (05) pochodzą z `tools/sample_size.py`; progi „heurystyka własna" są jawnie oznaczone w 05, sekcja 7.
