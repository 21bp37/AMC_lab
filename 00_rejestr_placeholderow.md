# 00. Rejestr placeholderów i punktów decyzyjnych

**Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

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
| P01 | Okno dat pełnego pobrania. **Wpisane:** źródło = TikTok Commercial Content Library / API; kraje = UE; próbka pilotażowa (44 reklamy, pobrana 2026-10-12): pierwszy dzień emisji 2025-09-30 do 2026-10-03 | [INŻ. DANYCH] | wybór źródła, dostępność | D2, D8 | częściowo |
| P02 | Liczba reklam, kreacji, reklamodawców w pełnym zbiorze (po deduplikacji). **Próbka pilotażowa:** 44 reklamy, 14 rozpoznawalnych reklamodawców, 8 reklam bez reklamodawcy | [INŻ. DANYCH] | pełne pobranie | D2, D7 | częściowo |
| P03 | Data pobrania (jest zmienną). **Wpisane:** retencja źródła = do roku od ostatniego wyświetlenia reklamy (oficjalna strona API) | [INŻ. DANYCH] | pobranie danych | D2, D6 | częściowo |
| P04 | Czy kreacje (obraz/wideo) są legalnie dostępne i na jakiej podstawie | [INŻ. DANYCH] | regulamin źródła, ewentualna zgoda prowadzącego | D1 | otwarty |
| P05 | Adres docelowy reklamy. **Ustalone na próbce pilotażowej:** pola nie ma w danych; zewnętrznej listy scamów nie używamy, więc nie jest potrzebne | [INŻ. DANYCH] | pola źródła | — | wpisane (do potwierdzenia na pełnym zbiorze) |
| P06 | Znaczenie pól czasu emisji i zasięgu. **Ustalone na próbce pilotażowej:** daty `first_shown_date` i `last_shown_date` (RRRRMMDD) są u wszystkich reklam; zasięg `unique_users_seen` to unikalni użytkownicy jako przedział; status „active”/„inactive” z komunikatem o usunięciu; dane zagregowane (suma za okres) | [INŻ. DANYCH] | dokumentacja źródła | D6 | wpisane z próbki (do potwierdzenia w dokumentacji) |
| P07 | Macierz legalności: źródło, podstawa prawna/ToS/licencja, pola, retencja, wolno zapisać | [INŻ. DANYCH] | lektura regulaminów | D1, D6 | otwarty |
| P08 | Data statement: link i wersja | [INŻ. DANYCH] | P07 | wszystkie | otwarty |
| P09 | Prevalence scamu i podejrzenia deepfake'a w próbie eksploracyjnej, z CI | [PIPELINE] | dane, pilotaż | D2 | otwarty |
| P10 | Rozkład języków. **Ustalone:** źródło nie podaje języka reklamy (pole targetowania puste dla 43 z 44); język ustalany z kreacji | [INŻ. DANYCH] | kodowanie | D8 | wpisane (język z kodowania) |
| P11 | Liczba klastrów i udział 10 największych. **Próbka pilotażowa:** 14 reklamodawców + 8 reklam bez reklamodawcy; 3 największych ma 25 z 44 reklam (57%); w pełnym zbiorze do powtórzenia | [INŻ. DANYCH] | dane | D7 | częściowo |
| P12 | Szacunek ICC i efektu projektu (deff) | [PIPELINE] / [ANALITYK] | dane z etykietami | D7 | otwarty |
| P13 | Wynik pilotażu annotacji: alpha per zmienna z CI | [PIPELINE] | pilotaż | D3 | otwarty |
| P14 | Wynik pierwszego testu annotatora ocenianego względem gold standardu | [PIPELINE] | pilotaż, wybór annotatora ocenianego | D5 | otwarty |
| P15 | Wybrany annotator oceniany: nazwa, wersja, parametry | [PIPELINE] | D1, D5, P20 | D5 | otwarty |
| P16 | Koszt i limity przetwarzania całości danych | [PIPELINE] | P02, P15 | D5 | otwarty |
| P17 | Wyniki eksploracji: rozkłady reklam w czasie, wstępne rozkłady L i I. **Próbka pilotażowa:** zob. M1_karta_eksploracji_danych.md, sekcja 4 (cała ramka, bez klasyfikacji) | [INŻ. DANYCH] | dane | D2 | częściowo |
| P18 | (wycofane: źródło Lista Ostrzeżeń CERT Polska usunięte decyzją zespołu) | — | — | — | wycofane |
| P19 | (wycofane: pokrycie listy CERT; źródło usunięte) | — | — | — | wycofane |
| P20 | Ścieżka dostępu: wniosek o TikTok Commercial Content API (konto deweloperskie, wniosek badawczy) i środowisko analizy. **Wpisane:** API otwarte dla publiczności i badaczy po wniosku (strona produktu) | [LEAD] / [INŻ. DANYCH] | uczelnia, wniosek | D1, D5 | częściowo |
| P21 | Skład zespołu annotatorów referencyjnych (ilu, którzy) i ich dostępność | [LEAD] | zespół | D3 | otwarty |
| P22 | Adres repozytorium, hash commita materiałów i lokalizacja logów sesji | [PIPELINE] | repozytorium | — | otwarty |
| P23 | Przykłady do codebooka z pilotażu (zanonimizowane, bez danych osobowych) | [PIPELINE] | pilotaż | D3 | otwarty |
| P24 | Limit reklam na reklamodawcę w komórce losowania | [PIPELINE] | rozkład reklamodawców (P11) | D7 | otwarty |
| P25 | Lista osób publicznych dla baseline'u słownikowego: źródło, licencja, wersja | [PIPELINE] / [INŻ. DANYCH] | licencja źródła listy | D5 | otwarty |
| P26 | Hipoteza i brzmienie pytania badawczego. **Wpisane z ustaleń leada (2026-10-12):** pytanie o medianę czasu życia i dzienną intensywność; hipoteza: mediana ≤ 2 dni, ponad 50% reklam ≥ 25 tys. wyświetleń na dzień (liczby mogą się zmienić; parametry T_L, T_I, p_min w 01) | [LEAD] | decyzja zespołu | — | wpisane (do potwierdzenia liczb) |
| P27 | Definicja wielkości mierzonych. **Wpisane z ustaleń leada:** dzienna intensywność = skumulowane impresje / liczba aktywnych dni; jednostka = reklama. Skala (liczba reklam) nie jest wielkością szukaną | [LEAD] | decyzja zespołu, P06 | D2, D6 | wpisane |
| P28 | Czas życia reklamy. **Wpisane:** dni kalendarzowe (włącznie z pierwszym i ostatnim: pipeline, do potwierdzenia). **Otwarte:** definicja reklamy wciąż aktywnej (status „active” nie oznacza emisji w toku: 24 z 36 reklam „active” miało ostatni dzień emisji ponad 30 dni przed pobraniem) i reklam rozpoczętych przed oknem źródła | [LEAD] / [INŻ. DANYCH] | P06, P03 | D6 | częściowo |
| P29 | Ramka: jak zbudowano zbiór reklam kandydujących (kryteria, zapytania, lista) | [INŻ. DANYCH] / [LEAD] | źródło, P01 | D9 | otwarty |
| P30 | Czy populacja jest zawężona do deepfake'ów z wizerunkiem osoby publicznej (pytanie projektowe), czy obejmuje wszystkie deepfake scamy (pytanie badawcze); **wpisane:** deepfake (podejrzenie) jest kryterium populacji | [LEAD] | decyzja zespołu, D1 | D1 | częściowo |
| P31 | Stan wiedzy i uzasadnienie wartości badania | [LEAD] | lektura | — | otwarty |
| P32 | Reguła rozstrzygnięcia hipotezy (jej składowych: czas życia i intensywność; położenie przedziału ufności względem progów) | [LEAD] / [ANALITYK] | P13, P12 | D2 | otwarty |
| P33 | Miara intensywności: źródło daje unikalnych użytkowników (przedziały), nie impresje; czy hipoteza i próg 25 tys. dotyczą tej miary i jak obsłużyć przedziały (dolna/górna granica) | [LEAD] | P06 | D6 | otwarty |

## Punkty decyzyjne

Każdy punkt ma postać: jeśli (wynik z danych), to (zmiana planu). Progi pochodzące z literatury są oznaczone źródłem; progi własne są oznaczone jako heurystyka.

| ID | Pytanie | Jeśli TAK | Jeśli NIE |
|---|---|---|---|
| D1 | Czy kreacje (wideo/obraz) są legalnie dostępne i wolno je przetwarzać? (P04, P07) | włącz poziom L2 codebooka (podejrzenie deepfake'a oraz widoczna twarz oceniane przez annotatora referencyjnego; zob. 04); populację „deepfake scam” da się zidentyfikować | populacji „deepfake scam” nie da się zidentyfikować z tekstu i metadanych; lead zawęża pytanie (np. do reklam scamowych bez rozróżnienia deepfake'a) albo raportujemy wynik negatywny o pomiarze (P30) |
| D2 | Czy w próbie jest dość reklam deepfake scam, aby oszacować medianę czasu życia i udział reklam z I ≥ T_I z użytecznym przedziałem ufności? (P02, P09) | plan próby z 05 | zawęż zakres lub raportuj jako eksploracyjne; wynik negatywny o wykonalności jest pełnoprawnym wynikiem |
| D3 | Czy zmienne osiągają α ≥ 0,80 (wiarygodne) lub ≥ 0,667 (tylko wnioski wstępne)? (P13) | użyj zmiennej w analizie z odpowiednim zastrzeżeniem | popraw definicję i powtórz pilotaż; po drugiej nieudanej rundzie usuń zmienną z pomiaru |
| D4 | (wycofany: dowód zewnętrzny z listy CERT; źródło usunięte decyzją zespołu) | — | scam wyłącznie z oceny annotatorów referencyjnych według codebooka, z jawnym zastrzeżeniem o błędzie etykiety (06, R03) |
| D5 | Czy annotator oceniany jest wystarczająco zgodny z gold standardem? (P14) | użyj do całości z korektą błędu (05) | kodowanie ręczne mniejszej próby (wariant E w 04) lub zmiana annotatora ocenianego |
| D6 | Czy dostępne są daty początku i końca emisji (czas życia) oraz zasięg za okres (dzienna intensywność)? (P06, P28, P33) | zmienne wynikowe L i I z metadanych (`tools/outcomes.py`) | pomiar czasu życia lub intensywności niemożliwy; wynik negatywny o pomiarze (01, sekcja 8) |
| D7 | Czy liczba klastrów jest wystarczająca? (P11, P12) | bootstrap klastrowy lub efekty losowe | agreguj do poziomu reklamodawcy lub kampanii; przy bardzo małej liczbie klastrów wnioskowanie tylko opisowe [@cameron2015] |
| D8 | Czy udział reklam po polsku jest wystarczający? (P10) | analiza łączna | analizy osobno per język, wnioski ograniczone do języka z próbą |
| D9 | Czy ramka (P29) jest zbudowana niezależnie od wyniku annotatora ocenianego i od kryterium „scam”? | wyniki można interpretować względem ramki | wyniki raportujemy wyłącznie dla ramki, bez uogólnienia na populację reklam |
