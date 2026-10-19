# Negatywne treści o ukraińskich uchodźcach: polskojęzyczny X a prorosyjski Telegram (2022)

Projekt zespołowy (kurs AMC). Hipoteza: trendy w pojawianiu się negatywnych treści na temat ukraińskich uchodźców w polskich mediach społecznościowych są skorelowane z podobnymi trendami w źródłach prorosyjskich. Karta eksploracji (M1): `reports/M1_karta_eksploracji.tex`; definicje miar i testów: `reports/METODY.md`.

## Struktura

| Ścieżka | Zawartość |
|---|---|
| `pipeline/config.py` | ścieżki, filtry tematu, leksykon narracji (wersjonowany), lista wydarzeń |
| `pipeline/load_twitter.py` | eksport NodeXL → tabela robocza (typ wiersza, kaskady RT, dzień PL, flagi) + raport jakości |
| `pipeline/series.py` | szeregi dzienne i wykrywanie peaków (odporny z-score) |
| `pipeline/leadlag.py` | test hipotezy (korelacja przyrostów dziennych i tygodniowych z testem permutacyjnym), analizy kierunku (Granger, dopasowanie peaków), symulacje mocy |
| `pipeline/telegram.py` | filtr 79 mln postów Telegrama (DuckDB) → szeregi dzienne wg strony kanału |
| `pipeline/eda_twitter.py` | eksploracja X: `reports/eda_summary.json`, `eda_numbers.tex`, `peaks_table.tex`, `figures/` |
| `tools/` | narzędzia walidacji instrumentu: zgodność koderów, P/R/F1, liczebność próby, korekta estymacji, dziennik uruchomień |
| `tests/` | testy na danych syntetycznych |
| `reports/` | karta M1 (LaTeX), wyniki eksploracji (`eda_results.md`, generowany), definicje miar i testów (`METODY.md`) |
| `ukraine-source/with_sentiment.csv` | eksport X (NodeXL + etykiety sentymentu); **do przeniesienia poza repozytorium**, zob. `CLEANUP.md` |

## Uruchomienie

```
pip install -r requirements.txt
python -m unittest discover -s tests
python -m pipeline.eda_twitter
cd reports && latexmk -pdf M1_karta_eksploracji.tex
```

Zasady pracy: `WORKFLOW.md`. Użycie AI: `09_ujawnienie_AI_i_wklad.md`.
