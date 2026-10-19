# Antyukraińskie narracje: Telegram prorosyjski → polskojęzyczny X (2022)

Projekt zespołowy (kurs AMC). Pytanie: czy wzrosty treści o Ukraińcach w Polsce pojawiają się najpierw w prorosyjskich kanałach Telegrama, a dopiero później w polskojęzycznym X/Twitterze, i czy opóźnienie jest w przybliżeniu stałe. Karta eksploracji (M1): `reports/M1_karta_eksploracji.tex`.

## Struktura

| Ścieżka | Zawartość |
|---|---|
| `pipeline/config.py` | ścieżki, filtry tematu, leksykon narracji (wersjonowany), lista wydarzeń |
| `pipeline/load_twitter.py` | eksport NodeXL → tabela robocza (typ wiersza, kaskady RT, dzień PL, flagi) + raport jakości |
| `pipeline/series.py` | szeregi dzienne i wykrywanie peaków (odporny z-score) |
| `pipeline/leadlag.py` | korelacja krzyżowa, dopasowanie peaków z testem permutacyjnym, Granger, symulacja mocy |
| `pipeline/telegram.py` | filtr 79 mln postów Telegrama (DuckDB) → szeregi dzienne wg strony kanału |
| `pipeline/eda_twitter.py` | eksploracja X: `reports/eda_summary.json`, `eda_numbers.tex`, `peaks_table.tex`, `figures/` |
| `tools/` | narzędzia walidacji instrumentu: zgodność koderów, P/R/F1, liczebność próby, korekta estymacji, dziennik uruchomień |
| `tests/` | testy na danych syntetycznych |
| `reports/` | wyniki eksploracji i karta M1 (LaTeX) |
| `ukraine-source/with_sentiment.csv` | eksport X (NodeXL + etykiety sentymentu); **do przeniesienia poza repozytorium**, zob. `CLEANUP.md` |

## Uruchomienie

```
pip install -r requirements.txt
python -m unittest discover -s tests
python -m pipeline.eda_twitter
cd reports && latexmk -pdf M1_karta_eksploracji.tex
```

Zasady pracy: `WORKFLOW.md`. Użycie AI: `09_ujawnienie_AI_i_wklad.md`.
