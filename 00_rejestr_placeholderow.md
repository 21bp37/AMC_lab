# 00. Rejestr placeholderów i punktów decyzyjnych

**Temat:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

Zakres tego repozytorium to wkład **inżyniera pipelinu**: codebook, gold standard, walidacja annotatora ocenianego, analiza błędów. Wszystko, co należy do innych ról, jest w dokumentach tylko jako placeholder i **nie jest wypełnione propozycją**. Oznaczenia właścicieli:

- **[PIPELINE]**: do uzupełnienia przez inżyniera pipelinu po pilotażu lub po otrzymaniu danych.
- **[INŻ. DANYCH]**: do uzupełnienia przez inżyniera danych (źródła, legalność, pola, statystyki opisowe zbioru).
- **[LEAD]**: do uzupełnienia przez team leada (pytanie, hipoteza, definicje wielkości, przegląd literatury, skład zespołu).
- **[ANALITYK]**: do uzupełnienia przez analityka (modele, korekty końcowe).

Wszystko, co zależy od danych albo od pracy innej roli, jest w dokumentach oznaczone jednolicie:

`{{Pnn: opis | zależy od: ... | domyślnie: ...}}`

Reguły: (1) placeholder zostaje w tekście, dopóki ktoś nie wpisze wartości z dowodem (plik, log, link); (2) po wpisaniu wartości usuń klamry i zmień status w tabeli poniżej; (3) komenda `python tools/checks.py placeholders` sprawdza, czy każdy użyty placeholder ma wiersz w rejestrze. Placeholdery w złożonym pliku Word są podświetlone na żółto.

## Rejestr placeholderów

| ID | Co trzeba wpisać | Właściciel | Zależy od | Punkt decyzyjny | Status |
|---|---|---|---|---|---|
| P01 | Zakres próby: kraje dostarczenia, języki, platformy, okno dat | [INŻ. DANYCH] | wybór źródła, dostępność | D2, D8 | otwarty |
| P02 | Liczba rekordów: reklam, unikatowych kreacji, reklamodawców (po deduplikacji) | [INŻ. DANYCH] | pobranie danych | D2, D7 | otwarty |
| P03 | Okno retencji źródła i daty pobrania (data pobrania jest zmienną) | [INŻ. DANYCH] | warunki źródła | D2, D6 | otwarty |
| P04 | Czy kreacje (obraz/wideo) są legalnie dostępne i na jakiej podstawie | [INŻ. DANYCH] | regulamin źródła, ewentualna zgoda prowadzącego | D1 | otwarty |
| P05 | Czy dostępny jest adres docelowy reklamy (domena) | [INŻ. DANYCH] | pola źródła | D4 | otwarty |
| P06 | Które pola czasu emisji (początek, koniec, status aktywności) i, jeśli lead ich wymaga, zasięgu są dostępne dla reklam komercyjnych | [INŻ. DANYCH] | oficjalna dokumentacja źródła | D6 | otwarty |
| P07 | Macierz legalności: źródło, podstawa prawna/ToS/licencja, pola, retencja, wolno zapisać | [INŻ. DANYCH] | lektura regulaminów | D1, D4, D6 | otwarty |
| P08 | Data statement: link i wersja | [INŻ. DANYCH] | P07 | wszystkie | otwarty |
| P09 | Odsetek reklam z wzmianką o osobie publicznej (prevalence) w próbie eksploracyjnej, z CI | [PIPELINE] | dane, pilotaż | D2 | otwarty |
| P10 | Rozkład języków i udział reklam po polsku | [INŻ. DANYCH] | dane | D8 | otwarty |
| P11 | Liczba klastrów (reklamodawców) i udział 10 największych | [INŻ. DANYCH] | dane | D7 | otwarty |
| P12 | Szacunek ICC i efektu projektu (deff) | [PIPELINE] / [ANALITYK] | dane z etykietami | D7 | otwarty |
| P13 | Wynik pilotażu annotacji: alpha per zmienna z CI | [PIPELINE] | pilotaż | D3 | otwarty |
| P14 | Wynik pierwszego testu annotatora ocenianego względem gold standardu | [PIPELINE] | pilotaż, wybór annotatora ocenianego | D5 | otwarty |
| P15 | Wybrany annotator oceniany: nazwa, wersja, parametry | [PIPELINE] | D1, D5, P20 | D5 | otwarty |
| P16 | Koszt i limity przetwarzania całości danych | [PIPELINE] | P02, P15 | D5 | otwarty |
| P17 | Wyniki eksploracji: rozkłady reklam w czasie i po platformach | [INŻ. DANYCH] | dane | D2 | otwarty |
| P18 | Warunki użycia Listy Ostrzeżeń CERT Polska (licencja samych danych listy) | [INŻ. DANYCH] | lektura warunków | D4 | otwarty |
| P19 | Pokrycie: jaki odsetek domen z danych można zestawić z listą CERT i w jakim oknie | [PIPELINE] | P05, P18 | D4 | otwarty |
| P20 | Ścieżka dostępu uczelni (np. umowa na Meta Content Library) i środowisko analizy | [LEAD] / [INŻ. DANYCH] | uczelnia | D1, D5 | otwarty |
| P21 | Skład zespołu annotatorów referencyjnych (ilu, którzy) i ich dostępność | [LEAD] | zespół | D3 | otwarty |
| P22 | Adres repozytorium, hash commita materiałów i lokalizacja logów sesji | [PIPELINE] | repozytorium | — | otwarty |
| P23 | Przykłady do codebooka z pilotażu (zanonimizowane, bez danych osobowych) | [PIPELINE] | pilotaż | D3 | otwarty |
| P24 | Limit reklam na reklamodawcę w komórce losowania | [PIPELINE] | rozkład reklamodawców (P11) | D7 | otwarty |
| P25 | Lista osób publicznych dla baseline'u słownikowego: źródło, licencja, wersja | [PIPELINE] / [INŻ. DANYCH] | licencja źródła listy | D5 | otwarty |
| P26 | Pytanie badawcze i hipoteza w wersji ostatecznej | [LEAD] | decyzja zespołu | — | otwarty |
| P27 | Definicja „skali” (jednostka liczenia: reklama, kreacja, reklamodawca; ewentualnie zasięg; okno czasu) | [LEAD] | decyzja zespołu, P06 | D2, D6 | otwarty |
| P28 | Definicja „czasu życia” reklamy (początek, koniec, traktowanie reklam wciąż aktywnych i reklam rozpoczętych przed oknem źródła) | [LEAD] / [INŻ. DANYCH] | P06, P03 | D6 | otwarty |
| P29 | Ramka: jak zbudowano zbiór reklam kandydujących (kryteria, zapytania, lista) | [INŻ. DANYCH] / [LEAD] | źródło, P01 | D9 | otwarty |
| P30 | Konstrukt „wizerunek znanej osoby”: wzmianka, widoczna twarz czy oba | [LEAD] | decyzja zespołu, D1 | D1 | otwarty |
| P31 | Stan wiedzy i uzasadnienie wartości badania | [LEAD] | lektura | — | otwarty |

## Punkty decyzyjne

Każdy punkt ma postać: jeśli (wynik z danych), to (zmiana planu). Progi pochodzące z literatury są oznaczone źródłem; progi własne są oznaczone jako heurystyka.

| ID | Pytanie | Jeśli TAK | Jeśli NIE |
|---|---|---|---|
| D1 | Czy kreacje (obraz/wideo) są legalnie dostępne? (P04, P07) | włącz poziom L2 codebooka (widoczna twarz oceniana przez annotatora referencyjnego; zob. 04) | tylko poziom L1 (tekst i metadane); konstrukt zawęża się do wzmianki o osobie publicznej, nie wizerunku (decyzja o sformułowaniu tematu: P30) |
| D2 | Czy w próbie jest dość reklam scamowych z wzmianką lub wizerunkiem osoby publicznej, aby oszacować skalę z użytecznym przedziałem ufności? (P02, P09) | plan próby z 05 | zawęż zakres lub raportuj jako eksploracyjne; wynik negatywny o wykonalności jest pełnoprawnym wynikiem |
| D3 | Czy zmienne osiągają α ≥ 0,80 (wiarygodne) lub ≥ 0,667 (tylko wnioski wstępne)? (P13) | użyj zmiennej w analizie z odpowiednim zastrzeżeniem | popraw definicję i powtórz pilotaż; po drugiej nieudanej rundzie usuń zmienną z pomiaru |
| D4 | Czy jest adres docelowy i legalny dostęp do listy CERT? (P05, P18, P19) | łańcuch dowodu reklama, domena, lista CERT | scam wyłącznie z oceny annotatora referencyjnego, z jawnym zastrzeżeniem o błędzie etykiety (06, R03) |
| D5 | Czy annotator oceniany jest wystarczająco zgodny z gold standardem? (P14) | użyj do całości z korektą błędu (05) | kodowanie ręczne mniejszej próby (wariant E w 04) lub zmiana annotatora ocenianego |
| D6 | Czy dostępne są daty początku i końca emisji (czas życia) oraz, jeśli lead tego wymaga, zasięg? (P06, P28) | zmienne wynikowe z metadanych | pomiar czasu życia (lub skali w wymiarze zasięgu) niemożliwy; wynik negatywny o pomiarze (01, sekcja 8) |
| D7 | Czy liczba klastrów jest wystarczająca? (P11, P12) | bootstrap klastrowy lub efekty losowe | agreguj do poziomu reklamodawcy lub kampanii; przy bardzo małej liczbie klastrów wnioskowanie tylko opisowe [@cameron2015] |
| D8 | Czy udział reklam po polsku jest wystarczający? (P10) | analiza łączna | analizy osobno per język, wnioski ograniczone do języka z próbą |
| D9 | Czy ramka (P29) jest zbudowana niezależnie od wyniku annotatora ocenianego i od kryterium „scam”? | skalę można interpretować względem ramki | skalę raportujemy wyłącznie jako liczbę w ramce, bez uogólnienia na populację reklam |
