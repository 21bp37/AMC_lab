# 09. Ujawnienie użycia AI i dziennik wkładu

Zasady kursu: oceniane są logi sesji z agentami, historia commitów, wykrywanie tekstu generowanego oraz obrona indywidualna; kryteria preprintu wymagają przejrzystego ujawnienia użycia AI. Ten dokument służy do uczciwego i sprawdzalnego opisania tego, co zrobiłeś ty, a co model.

## 1. Oświadczenie o przygotowaniu materiałów M1

Materiały tego repozytorium (pipeline w `pipeline/`, narzędzia w `tools/`, testy, karta M1 w `reports/`) zostały **przygotowane przy użyciu asystenta AI (Claude)** w sesji roboczej na podstawie poleceń autora. Obejmuje to: szkice dokumentów, kod narzędzi i testów, wyszukiwanie literatury. Wszystkie dokumenty są szkicami do redakcji przez autora; autor odpowiada za ich treść po weryfikacji.

Wpisz po swojej stronie:

- Autor materiałów (rola: inżynier pipeline'u): UZUPEŁNIJ imię i nazwisko
- Sesje z agentami, logi: UZUPEŁNIJ lokalizację logów sesji i commit z materiałami

## 2. Tabela wkładu (uzupełniaj na bieżąco)

| Element | Wygenerowane przez AI (co) | Zmienione/dopisane przez autora (co) | Zweryfikowane przez (kto, jak) | Commit / log sesji |
|---|---|---|---|---|
| Pipeline eksploracji X (`pipeline/load_twitter.py`, `series.py`, `eda_twitter.py`) | kod, wybór miar (kaskady, odporny z-score) | | uruchomienie, przegląd kodu | |
| Filtr Telegrama i testy opóźnień (`pipeline/telegram.py`, `leadlag.py`) | kod, symulacja mocy | | testy syntetyczne | |
| Leksykon narracji 0.1 (`pipeline/config.py`) | szkic wzorców | | walidacja na gold standardzie (do zrobienia) | |
| Karta M1 (`reports/M1_karta_eksploracji.tex`) | szkic tekstu; liczby z `eda_numbers.tex` | | | |
| Sprzątanie repozytorium (`CLEANUP.md`) | lista i zmiany | | | |
| Narzędzia walidacji (`tools/`) | kod z poprzedniego tematu, przeniesiony | | testy | |

## 3. Co autor musi zrobić, żeby obronić te materiały

1. Przeczytać i zrozumieć każdy dokument; potrafić wyjaśnić, **dlaczego** każdy próg i wybór jest taki, a nie inny (źródło albo „heurystyka własna" „heurystyka własna”).
2. Otworzyć źródła oznaczone „do sprawdzenia" w 07 i poprawić dane bibliograficzne. **Nie wpisywać do preprintu źródeł, których się nie otworzyło.**
3. Uruchomić testy (`python -m unittest discover -s tests`) i przeczytać kod narzędzi oraz pipeline'u, których użyje w analizie.
4. Zmienić materiały tam, gdzie się nie zgadza (zespół, dane, decyzje); same commity bez własnej pracy nie dowodzą wkładu.

## 4. Szablon wpisu do preprintu (sekcja „Użycie AI")

> Szkice dokumentów metodologicznych, kod narzędzi pomocniczych i testy zostały przygotowane z pomocą [model, wersja, data]. Autor [imię] zweryfikował [co] i zmienił [co]. Etykiety instrumentu AI zostały zwalidowane na gold standardzie opisanym w sekcji [X]. Pełne logi sesji i konfiguracji uruchomień dostępne w repozytorium [adres].

## 5. Zasady higieny

- Każde uruchomienie instrumentu AI jest w dzienniku (`tools/run_log.py`).
- Nie wklejamy do narzędzi AI danych, do których nie mamy prawa udostępniać osobom trzecim (macierz legalności, P07).
- Treści generowane (np. przykłady do codebooka) oznaczamy jako takie; przykłady z danych zanonimizujemy.
