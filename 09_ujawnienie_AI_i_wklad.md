# 09. Ujawnienie użycia AI i dziennik wkładu

Zasady kursu: oceniane są logi sesji z agentami, historia commitów, wykrywanie tekstu generowanego oraz obrona indywidualna; kryteria preprintu wymagają przejrzystego ujawnienia użycia AI. Ten dokument służy do uczciwego i sprawdzalnego opisania tego, co zrobiłeś ty, a co model.

## 1. Oświadczenie o przygotowaniu materiałów M1

Materiały tego repozytorium (dokumenty 00–10, narzędzia w `tools/`, testy) zostały **przygotowane przy użyciu asystenta AI (Claude)** w sesji roboczej na podstawie poleceń autora. Obejmuje to: szkice dokumentów, kod narzędzi i testów, wyszukiwanie literatury. Wszystkie dokumenty są szkicami do redakcji przez autora; autor odpowiada za ich treść po weryfikacji.

Wpisz po swojej stronie:

- Autor materiałów (rola: inżynier pipelinu): {{P21: imię i nazwisko | zależy od: zespół | domyślnie: brak}}
- Sesje z agentami, logi: {{P22: lokalizacja logów sesji i commit z materiałami | zależy od: repozytorium | domyślnie: brak}}

## 2. Tabela wkładu (uzupełniaj na bieżąco)

| Element | Wygenerowane przez AI (co) | Zmienione/dopisane przez autora (co) | Zweryfikowane przez (kto, jak) | Commit / log sesji |
|---|---|---|---|---|
| Codebook v0.1 | szkic zmiennych, definicji, przypadków granicznych | | | |
| Plan pomiaru (01) | szkic | | | |
| Plan annotatora ocenianego (04) | szkic | | | |
| Rejestr placeholderów i punktów decyzyjnych (00), specyfikacja interfejsu (03) | szkic | | | |
| Plan gold standardu (05) | szkic, obliczenia z narzędzi | | | |
| Rejestr ryzyk (06) | szkic | | | |
| Bibliografia (07) | wyszukanie i opis źródeł | | otwarcie oryginałów (statusy w 07) | |
| Narzędzia i testy | kod | | uruchomienie testów; przegląd kodu | |

## 3. Co autor musi zrobić, żeby obronić te materiały

1. Przeczytać i zrozumieć każdy dokument; potrafić wyjaśnić, **dlaczego** każdy próg i wybór jest taki, a nie inny (źródło albo „heurystyka własna" według 05, sekcja 7).
2. Otworzyć źródła oznaczone „do sprawdzenia" w 07 i poprawić dane bibliograficzne. **Nie wpisywać do preprintu źródeł, których się nie otworzyło.**
3. Uruchomić testy (`python -m unittest discover -s tests`) i przeczytać kod narzędzi, których użyje w analizie.
4. Zmienić materiały tam, gdzie się nie zgadza (zespół, dane, decyzje); same commity bez własnej pracy nie dowodzą wkładu.

## 4. Szablon wpisu do preprintu (sekcja „Użycie AI")

> Szkice dokumentów metodologicznych, kod narzędzi pomocniczych i testy zostały przygotowane z pomocą [model, wersja, data]. Autor [imię] zweryfikował [co] i zmienił [co]. Etykiety instrumentu AI zostały zwalidowane na gold standardzie opisanym w sekcji [X]. Pełne logi sesji i konfiguracji uruchomień dostępne w repozytorium [adres].

## 5. Zasady higieny

- Każde uruchomienie instrumentu AI jest w dzienniku (`tools/run_log.py`).
- Nie wklejamy do narzędzi AI danych, do których nie mamy prawa udostępniać osobom trzecim (macierz legalności, P07).
- Treści generowane (np. przykłady do codebooka) oznaczamy jako takie; przykłady z danych zanonimizujemy.
