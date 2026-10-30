# Sprzątanie gałęzi `ukraine-source` (zmiana tematu: deepfake/TikTok → Telegram/X, Ukraińcy w Polsce)

Stan przed: dokumentacja i narzędzia dotyczyły poprzedniego tematu (reklamy deepfake scam z TikTok Commercial Content Library). Nic z warstwy dziedzinowej nie pasuje do nowych danych.

## Usunięte (przestarzałe, dotyczą reklam TikToka)

| Plik | Powód |
|---|---|
| `00_rejestr_placeholderow.md` | placeholdery P01–P33 i decyzje D1–D9 dla reklam |
| `01_plan_pomiaru_M1.md`, `M1_karta_eksploracji_danych.md` | hipoteza o czasie życia reklam; zastąpione przez `reports/M1_karta_eksploracji.tex` |
| `02_codebook_v0.1.md`, `tools/schema.yaml`, `templates/annotation_sheet_template.csv` | zmienne kodowania kreacji reklam (deepfake, celebryta, scam) |
| `03_specyfikacja_interfejsu_dane.md`, `tools/audit_dataset.py`, `tools/load_tiktok_json.py` | interfejs i loader danych TikToka; zastąpione przez `pipeline/load_twitter.py` i `pipeline/telegram.py` |
| `04_plan_instrumentu.md`, `05_gold_standard_i_walidacja.md`, `06_rejestr_ryzyk.md`, `10_playbook_po_otrzymaniu_danych.md` | plan annotatora wizualnego, gold standard i ryzyka dla reklam |
| `M1_pipeline.md` (130 KB) | opis starego pipeline'u |
| `tools/outcomes.py`, `tools/make_synthetic.py`, `tools/checks.py` | czas życia/intensywność reklam, generator syntetycznych reklam, kontrole codebooka |
| `tools/test_tools.py`, `tests/test_tools.py` | dwie rozjechane kopie testów starych narzędzi; zastąpione przez `tests/test_pipeline.py` i `tests/test_validation_tools.py` |
| wszystkie `.ipynb_checkpoints/` (17 plików) | śmieci Jupytera; dodane do `.gitignore` |

## Zmienione

| Plik | Zmiana |
|---|---|
| `README.md`, `WORKFLOW.md` | nowy temat, struktura, polecenia odtworzenia wyników |
| `requirements.txt` | + matplotlib, statsmodels, duckdb; − PyYAML |
| `.github/workflows/ci.yml` | usunięte kroki `checks.py`; testy z `tests/`; reguła „brak danych” z przejściowym wyjątkiem dla CSV z X |
| `.github/pull_request_template.md`, `templates/codebook_changelog.md`, `prompts/README.md`, `logs/README.md` | odwołania do nowego pomiaru (leksykon, klasyfikator) zamiast codebooka reklam |
| `07_bibliografia.md` | zostały sekcje A (zgodność), B (LLM jako annotator), D (wnioskowanie); usunięte C (reklamy) i E; nowa sekcja C do uzupełnienia |
| `09_ujawnienie_AI_i_wklad.md` | tabela wkładu dla nowych materiałów |
| `tools/estimators.py`, `tools/sampling.py`, `tools/run_log.py` | poprawione odwołania do usuniętych plików |

## Zostawione bez zmian (ogólne, przydadzą się do walidacji klasyfikatora)

`tools/agreement.py`, `tools/evaluation.py`, `tools/sample_size.py`, `tools/prompt_robustness.py`, `tools/run_log.py`, `tools/estimators.py`, `tools/sampling.py`. Docstringi wciąż mówią o „reklamach/reklamodawcach”; w nowym temacie klastrem jest konto źródłowe (X) albo kanał (Telegram). **Do zmiany przy pierwszym użyciu** (pipeline). `estimators.py` i `sampling.py` nie mają teraz testów, bo stare testy opierały się na usuniętym generatorze reklam.

## Decyzje dla zespołu (nie podjęte w tym commicie)

- **D1 — `ukraine-source/with_sentiment.csv` w publicznym repozytorium.** Plik zawiera pełne treści 55 035 postów, loginy i ID autorów. Regulamin deweloperski X pozwala udostępniać publicznie identyfikatory postów, a nie ich treść, a loginy autorów to dane osobowe. Rekomendacja: usunąć plik z repozytorium (również z historii, np. `git filter-repo`), trzymać go w prywatnym miejscu, a w repo zostawić tylko listę `tweet_id`. Do decyzji: lead + inżynier danych. Do tego czasu CI ma wyjątek na ten jeden plik.
- **D2 — pochodzenie etykiet sentymentu** (`Sentiment_Label`, `Sentiment_Score`): który model, wersja, na jakim polu tekstu (RT są ucięte). Bez tego etykiet nie można opisać w preprincie. Właściciel: kto dodał plik (commit 8dc68ad).
- **D3 — oryginalne zapytanie do API** (czy „Ukraińcy” AND „w Polsce”, z odmianą czy bez) i przyczyna braku danych 24.02–3.03.2022. Właściciel: inżynier danych.
- **D4 — zbiór Telegrama: rozwiązane co do źródła.** Kyrychenko R., *Russian and Ukrainian War-related Telegram Channels*, Zenodo, doi:10.5281/zenodo.16949193, CC BY 4.0, 49 GB (8 plików postów). Do zrobienia: pobranie poza repozytorium (inżynier danych) i uruchomienie `python -m pipeline.telegram`.
