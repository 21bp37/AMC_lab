# WORKFLOW: praca w repozytorium

## Gałęzie i commity
- `main` jest chroniona: zmiany przez pull request z jednym przeglądem (inna osoba niż autor).
- Gałąź: `<rola>/<temat>`, np. `pipeline/pilot-celeb-mention`.
- Commit: małe zmiany, wiadomość w trybie rozkazującym i z odwołaniem do ID (np. `P13`, `R05`, `D3`). Commity są oceniane jako dowód wkładu, więc każdy commit opisuje to, co zrobiła osoba, która go tworzy.

## Własność miejsc
Placeholdery `{{Pnn}}` ma prawo wypełnić tylko właściciel z rejestru (00). Pipeline nie uzupełnia miejsc leada, inżyniera danych ani analityka. Po wypełnieniu usuń klamry, zmień status w 00 i uruchom `python tools/checks.py placeholders`.

## Dane
- Dane o reklamach nie wchodzą do repozytorium (`.gitignore`, kontrola w CI). Przechowuje je i udostępnia inżynier danych w uzgodnionym miejscu, zgodnie z macierzą legalności (03, P07).
- Pole `celeb_id` istnieje tylko w plikach roboczych poza repozytorium (`annotation_work/`).
- Do repozytorium wchodzą: dokumenty, kod, testy, szablony, dane syntetyczne (`is_synthetic=1`), `logs/runs.jsonl` (hashe, bez danych).

## Codebook i prompty
1. Zmiana codebooka: nowa wersja + wpis w `templates/codebook_changelog.md`; po zamrożeniu tylko przez PR z powtórną oceną na próbie kontrolnej.
2. Prompt: nowy plik `prompts/prompt_<zmienna>_v<N>.txt`, nigdy nadpisanie.
3. Każde uruchomienie annotatora ocenianego: wpis w `logs/runs.jsonl` (`tools/run_log.py`).

## Sesje z AI
Logi sesji z agentem przechowujemy poza `main` (lokalizacja w P22) i opisujemy wkład w 09. Redakcja logu tylko jawna i uzgodniona z prowadzącym.

## Kontrola jakości (CI)
`.github/workflows/ci.yml` uruchamia testy, kontrole spójności i sprawdza, że w repozytorium nie ma plików danych.
