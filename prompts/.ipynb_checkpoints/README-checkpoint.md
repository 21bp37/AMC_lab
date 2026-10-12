# prompts/

Prompty annotatora ocenianego. Nazwa: `prompt_<zmienna>_v<N>.txt`. Zmiana = nowy plik, nie nadpisanie (04, sekcja 4).

Pliki powstają dopiero po zamrożeniu codebooka. Prompt zawiera wyłącznie definicje, wartości, przykłady i reguły graniczne z `02_codebook_*.md`; nie dodaje własnych reguł i nie pyta o tożsamość osoby na obrazie (04, zasada 4).

Każde uruchomienie jest zapisane w `logs/runs.jsonl` przez `tools/run_log.py`.
