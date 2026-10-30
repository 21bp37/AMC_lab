# WORKFLOW: praca w repozytorium

## Gałęzie i commity
- `main` chroniona: zmiany przez pull request z jednym przeglądem (inna osoba niż autor).
- Gałąź: `<rola>/<temat>`, np. `pipeline/ukraine-eda`.
- Commit: małe zmiany, opis w trybie rozkazującym. Commity są dowodem wkładu, więc każdy opisuje pracę osoby, która go tworzy.

## Dane
- Dane (X/Twitter, Telegram) nie wchodzą do repozytorium; lokalnie trzymamy je w `data/` (w `.gitignore`). Wyjątek przejściowy: `ukraine-source/with_sentiment.csv` (CLEANUP.md, D1).
- Do repozytorium wchodzą: kod, testy, dokumenty, raporty z liczbami i wykresami (`reports/`), bez treści postów.

## Odtwarzanie wyników
```
pip install -r requirements.txt
python -m unittest discover -s tests
python -m pipeline.eda_twitter                 # reports/eda_summary.json, eda_numbers.tex, peaks_table.tex, figures/
python -m pipeline.telegram --posts '…/post_texts_part_*.csv' --clusters '…/leiden_clusters.csv'
cd reports && latexmk -pdf M1_karta_eksploracji.tex
```

## Pomiar
Zmiana leksykonu, progu peaku lub klasyfikatora = nowa wersja w `pipeline/config.py` + wpis w `templates/codebook_changelog.md`. Prompty: `prompts/`, uruchomienia: `logs/runs.jsonl`.
