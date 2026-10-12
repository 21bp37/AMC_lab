# Materiały M1: inżynier pipelinu (wersja finalna)

**Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

**Pytanie badawcze (z ustaleń zespołu):** Jaka jest mediana czasu życia reklam typu deepfake scam i jak kształtuje się ich dzienna intensywność wyświetleń (stosunek skumulowanych impresji do liczby aktywnych dni)?

**Hipoteza (z ustaleń zespołu):** Mediana czasu życia reklam typu deepfake scam nie przekracza 2 dni kalendarzowych, lecz mimo tak krótkiej obecności ponad 50% z nich osiąga szacunkowo 25 tys. impresji na dzień aktywności, co jest zgodne z taktyką agresywnego budżetu startowego (*burst-and-burn*). Progi (2 dni, 25 tys., 50%) mogą się jeszcze zmienić i są w kodzie parametrami.

**Źródło danych (z ustaleń zespołu):** głównie TikTok (Commercial Content Library i API; dane z UE). **Ograniczenie danych:** tylko wartości zagregowane (suma wyświetleń za okres podzielona przez liczbę dni), bez rozkładu godzinowego.

**Status:** zakres: codebook, gold standard, walidacja annotatora ocenianego, analiza błędów. Treści od leada i inżyniera danych wpisano tylko tam, gdzie wynikają one z ustaleń zespołu lub z oficjalnych stron TikToka; reszta pozostaje placeholderami.

## Legenda oznaczeń

- `{{Pnn: ...}}`: placeholder do uzupełnienia; właściciel w rejestrze 00.
- **[LEAD – DO WYPEŁNIENIA]**: miejsce należące do team leada (reguła decyzyjna hipotez, zawężenie populacji, traktowanie reklam aktywnych, skład annotatorów, stan wiedzy). Brak propozycji pipelinu poza wartością „domyślnie: brak”.
- **[INŻ. DANYCH – DO WYPEŁNIENIA]**: miejsce należące do inżyniera danych (znaczenie pól źródła, legalność, ramka, statystyki opisowe). Tylko placeholdery i fakty z oficjalnych stron.
- **[PIPELINE – DO WYPEŁNIENIA]**: wyniki z pilotażu i danych, które uzupełnia inżynier pipelinu.
- **[ANALITYK – DO WYPEŁNIENIA]**: modele przeżycia i korekty końcowe.
- Odwołania `[klucz]` odpowiadają wpisom w 07.

## Zakres względem M1 (karta eksploracji danych, bloki 1–2)

| Dokument | Zakres |
|---|---|
| 01 plan pomiaru, 06 ryzyka, 00 rejestr | rdzeń M1 |
| 02 codebook, 03 interfejs danych, 04 annotator oceniany | M1 w wersji skróconej (zmienne, źródła, wykonalność); szczegóły to przygotowanie kolejnych etapów |
| 05 gold standard i walidacja, 10 playbook (kroki 5–8), narzędzia (`tools/outcomes.py`) | bank na kolejne etapy; do M1 wystarczy 1–2 zdania planu walidacji |
| 07 bibliografia, 09 ujawnienie AI | wsparcie |

## Co wypełniono, a co czeka na właściciela

| Element | Stan | Właściciel |
|---|---|---|
| Pytanie badawcze i hipoteza (P26), definicja dziennej intensywności (P27) | wpisane z ustaleń zespołu | [LEAD] |
| Czas życia: jednostka (dni kalendarzowe) | wpisane; konwencja „włącznie” do potwierdzenia | [LEAD] |
| Źródło (TikTok), kraje (UE), retencja (do roku od ostatniego wyświetlenia) | wpisane z oficjalnych stron | [INŻ. DANYCH] |
| Znaczenie pól dat i wyświetleń, kreacje w API, warunki zapisu danych (P04, P06, P07) | otwarte | [INŻ. DANYCH] |
| Ramka, okno dat, języki, liczebności, statystyki opisowe (P01, P02, P10, P11, P17, P29) | otwarte | [INŻ. DANYCH] |
| Reklamy aktywne i obcięte (P28), zawężenie populacji (P30), reguła decyzyjna (P32), skład annotatorów (P21), stan wiedzy (P31) | otwarte | [LEAD] |
| Pilotaż, α, wyniki annotatora ocenianego, prevalence (P09, P13, P14, P15) | czekają na dane | [PIPELINE] |
| Model przeżycia, korekty końcowe (P12) | czekają na dane | [ANALITYK] |

## Spis treści
- 00. Rejestr placeholderów i punktów decyzyjnych
- 01. Plan pomiaru zjawiska (wkład inżyniera pipelinu do karty M1)
- 02. Codebook v0.1
- 03. Specyfikacja interfejsu: pipeline i inżynier danych
- 04. Plan instrumentu pomiarowego
- 05. Plan gold standardu i walidacji annotatora ocenianego
- 06. Rejestr ryzyk i ograniczeń
- 07. Bibliografia z adnotacjami i statusem weryfikacji
- 09. Ujawnienie użycia AI i dziennik wkładu
- 10. Playbook: co robić po otrzymaniu danych



---

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
| P01 | Okno dat i języki próby. **Wpisane:** źródło = TikTok Commercial Content Library / API; kraje = UE (zakres źródła) | [INŻ. DANYCH] | wybór źródła, dostępność | D2, D8 | częściowo |
| P02 | Liczba rekordów: reklam, unikatowych kreacji, reklamodawców (po deduplikacji) | [INŻ. DANYCH] | pobranie danych | D2, D7 | otwarty |
| P03 | Data pobrania (jest zmienną). **Wpisane:** retencja źródła = do roku od ostatniego wyświetlenia reklamy (oficjalna strona API) | [INŻ. DANYCH] | pobranie danych | D2, D6 | częściowo |
| P04 | Czy kreacje (obraz/wideo) są legalnie dostępne i na jakiej podstawie | [INŻ. DANYCH] | regulamin źródła, ewentualna zgoda prowadzącego | D1 | otwarty |
| P05 | Czy dostępny jest adres docelowy reklamy (domena); opcjonalny, tylko jako pole opisowe | [INŻ. DANYCH] | pola źródła | — | otwarty |
| P06 | Pola czasu emisji i wyświetleń w TikTok Commercial Content Library / API: czy daty to pierwszy i ostatni dzień wyświetlania, jak oznaczone są reklamy aktywne, czy „liczba osób, które zobaczyły reklamę” to wyświetlenia czy unikatowi odbiorcy, wartość czy przedział, suma za okres czy rozbicie. **Wpisane:** strona API wymienia datę publikacji, „last seen date” i liczbę osób; **ustalone przez zespół:** dane tylko zagregowane (suma za okres, nie rozkład godzinowy) | [INŻ. DANYCH] | oficjalna dokumentacja źródła | D6 | częściowo |
| P07 | Macierz legalności: źródło, podstawa prawna/ToS/licencja, pola, retencja, wolno zapisać | [INŻ. DANYCH] | lektura regulaminów | D1, D6 | otwarty |
| P08 | Data statement: link i wersja | [INŻ. DANYCH] | P07 | wszystkie | otwarty |
| P09 | Prevalence scamu i podejrzenia deepfake'a w próbie eksploracyjnej, z CI | [PIPELINE] | dane, pilotaż | D2 | otwarty |
| P10 | Rozkład języków i udział reklam po polsku | [INŻ. DANYCH] | dane | D8 | otwarty |
| P11 | Liczba klastrów (reklamodawców) i udział 10 największych | [INŻ. DANYCH] | dane | D7 | otwarty |
| P12 | Szacunek ICC i efektu projektu (deff) | [PIPELINE] / [ANALITYK] | dane z etykietami | D7 | otwarty |
| P13 | Wynik pilotażu annotacji: alpha per zmienna z CI | [PIPELINE] | pilotaż | D3 | otwarty |
| P14 | Wynik pierwszego testu annotatora ocenianego względem gold standardu | [PIPELINE] | pilotaż, wybór annotatora ocenianego | D5 | otwarty |
| P15 | Wybrany annotator oceniany: nazwa, wersja, parametry | [PIPELINE] | D1, D5, P20 | D5 | otwarty |
| P16 | Koszt i limity przetwarzania całości danych | [PIPELINE] | P02, P15 | D5 | otwarty |
| P17 | Wyniki eksploracji: rozkłady reklam w czasie, wstępne rozkłady czasu życia L i dziennej intensywności I | [INŻ. DANYCH] | dane | D2 | otwarty |
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
| P28 | Czas życia reklamy. **Wpisane:** dni kalendarzowe (włącznie z pierwszym i ostatnim: pipeline, do potwierdzenia). **Otwarte:** traktowanie reklam wciąż aktywnych w dniu pobrania i reklam rozpoczętych przed oknem źródła | [LEAD] / [INŻ. DANYCH] | P06, P03 | D6 | częściowo |
| P29 | Ramka: jak zbudowano zbiór reklam kandydujących (kryteria, zapytania, lista) | [INŻ. DANYCH] / [LEAD] | źródło, P01 | D9 | otwarty |
| P30 | Czy populacja jest zawężona do deepfake'ów z wizerunkiem osoby publicznej (pytanie projektowe), czy obejmuje wszystkie deepfake scamy (pytanie badawcze); **wpisane:** deepfake (podejrzenie) jest kryterium populacji | [LEAD] | decyzja zespołu, D1 | D1 | częściowo |
| P31 | Stan wiedzy i uzasadnienie wartości badania | [LEAD] | lektura | — | otwarty |
| P32 | Reguła rozstrzygnięcia hipotezy (jej składowych: czas życia i intensywność; położenie przedziału ufności względem progów) | [LEAD] / [ANALITYK] | P13, P12 | D2 | otwarty |

## Punkty decyzyjne

Każdy punkt ma postać: jeśli (wynik z danych), to (zmiana planu). Progi pochodzące z literatury są oznaczone źródłem; progi własne są oznaczone jako heurystyka.

| ID | Pytanie | Jeśli TAK | Jeśli NIE |
|---|---|---|---|
| D1 | Czy kreacje (wideo/obraz) są legalnie dostępne i wolno je przetwarzać? (P04, P07) | włącz poziom L2 codebooka (podejrzenie deepfake'a oraz widoczna twarz oceniane przez annotatora referencyjnego; zob. 04); populację „deepfake scam” da się zidentyfikować | populacji „deepfake scam” nie da się zidentyfikować z tekstu i metadanych; lead zawęża pytanie (np. do reklam scamowych bez rozróżnienia deepfake'a) albo raportujemy wynik negatywny o pomiarze (P30) |
| D2 | Czy w próbie jest dość reklam deepfake scam, aby oszacować medianę czasu życia i udział reklam z I ≥ T_I z użytecznym przedziałem ufności? (P02, P09) | plan próby z 05 | zawęż zakres lub raportuj jako eksploracyjne; wynik negatywny o wykonalności jest pełnoprawnym wynikiem |
| D3 | Czy zmienne osiągają α ≥ 0,80 (wiarygodne) lub ≥ 0,667 (tylko wnioski wstępne)? (P13) | użyj zmiennej w analizie z odpowiednim zastrzeżeniem | popraw definicję i powtórz pilotaż; po drugiej nieudanej rundzie usuń zmienną z pomiaru |
| D4 | (wycofany: dowód zewnętrzny z listy CERT; źródło usunięte decyzją zespołu) | — | scam wyłącznie z oceny annotatorów referencyjnych według codebooka, z jawnym zastrzeżeniem o błędzie etykiety (06, R03) |
| D5 | Czy annotator oceniany jest wystarczająco zgodny z gold standardem? (P14) | użyj do całości z korektą błędu (05) | kodowanie ręczne mniejszej próby (wariant E w 04) lub zmiana annotatora ocenianego |
| D6 | Czy dostępne są daty początku i końca emisji (czas życia) oraz skumulowane wyświetlenia za okres (dzienna intensywność)? (P06, P28) | zmienne wynikowe L i I z metadanych (`tools/outcomes.py`) | pomiar czasu życia lub intensywności niemożliwy; wynik negatywny o pomiarze (01, sekcja 8) |
| D7 | Czy liczba klastrów jest wystarczająca? (P11, P12) | bootstrap klastrowy lub efekty losowe | agreguj do poziomu reklamodawcy lub kampanii; przy bardzo małej liczbie klastrów wnioskowanie tylko opisowe [cameron2015] |
| D8 | Czy udział reklam po polsku jest wystarczający? (P10) | analiza łączna | analizy osobno per język, wnioski ograniczone do języka z próbą |
| D9 | Czy ramka (P29) jest zbudowana niezależnie od wyniku annotatora ocenianego i od kryterium „scam”? | wyniki można interpretować względem ramki | wyniki raportujemy wyłącznie dla ramki, bez uogólnienia na populację reklam |

---

# 01. Plan pomiaru zjawiska (wkład inżyniera pipelinu do karty M1)

Karta M1 jest oceniana za: konkretność pytania, jakość eksploracji i spójność planu badawczego, z jawnymi ograniczeniami danych, źródłami błędu i uzasadnieniem wykonalności. Ten dokument jest wkładem inżyniera pipelinu: **jak klasyfikujemy reklamy do populacji badanej, jak sprawdzimy, że annotator oceniany działa, jak analizujemy jego błędy i co może nas zatrzymać**. Oznaczenia właścicieli jak w 00: **[LEAD]**, **[INŻ. DANYCH]**, **[PIPELINE]**, **[ANALITYK]**. Treść wpisana na podstawie ustaleń zespołu (leada i inżyniera danych) jest oznaczona jako **wpisane z ustaleń leada**; liczby progowe mogą się jeszcze zmienić, dlatego są zebrane w jednej tabeli (sekcja 1) i podawane do narzędzi jako parametry.

## 1. Temat, pytanie badawcze i hipoteza

**Temat:** Oszustwa z deepfake'ami.

**Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

**Pytanie badawcze (wpisane z ustaleń leada):** Jaka jest mediana czasu życia reklam typu deepfake scam i jak kształtuje się ich dzienna intensywność wyświetleń (stosunek skumulowanych impresji do liczby aktywnych dni)?

**Hipoteza (wpisana z ustaleń leada):** Mediana czasu życia reklam typu deepfake scam nie przekracza 2 dni kalendarzowych, lecz mimo tak krótkiej obecności charakteryzują się one skrajnie wysoką dzienną intensywnością wyświetleń (ponad 50% z nich osiąga szacunkowo 25 tys. impresji na dzień aktywności), co potwierdza stosowanie taktyki agresywnego budżetu startowego (*burst-and-burn*).

**Parametry hipotezy** (wartości od leada; mogą się zmienić, więc kod i dokumenty odwołują się do nich jako do parametrów):

| Parametr | Wartość teraz | Użycie |
|---|---|---|
| T_L: próg mediany czasu życia | 2 dni kalendarzowe | składowa o czasie życia: mediana L ≤ T_L |
| T_I: próg dziennej intensywności | 25 000 wyświetleń na dzień | składowa o intensywności: udział reklam z I ≥ T_I |
| p_min: wymagany udział | 50% | składowa o intensywności: udział reklam z I ≥ T_I jest większy niż p_min |

**Operacjonalizacja przyjęta przez pipeline** (do potwierdzenia przez leada i analityka):

- **L (czas życia)** = liczba dni kalendarzowych od pierwszego do ostatniego dnia emisji, **włącznie z oboma** (`delivery_stop − delivery_start + 1`); reklama wyświetlana jednego dnia ma L = 1. To ważne dla progu T_L = 2, bo zmiana konwencji o jeden dzień zmienia wniosek.
- **I (dzienna intensywność)** = skumulowane wyświetlenia (`reach_total`) / L. Liczba „aktywnych dni” jest przybliżona rozpiętością od pierwszej do ostatniej emisji (źródło nie ujawnia dni przerwy, jeśli były).
- **Hipoteza jest jedna, o dwóch składowych:** (a) mediana L w populacji badanej ≤ T_L; (b) udział reklam populacji z I ≥ T_I jest większy niż p_min (równoważnie: mediana I ≥ T_I). Hipotezę uznajemy za wspartą w całości dopiero, gdy wspierane są obie składowe.
- Obie wielkości są liczone **na populacji badanej**, czyli na reklamach sklasyfikowanych jako deepfake scam (sekcja 4), z korektą błędu klasyfikacji (05, sekcja 6).

**Czego dane nie pozwolą ocenić (uczciwe zastrzeżenie dla karty M1).** Źródło daje **sumę wyświetleń za cały okres emisji**, a nie przebieg godzina po godzinie ani dzień po dniu. Dzienna intensywność jest więc wartością *średnią* (suma podzielona przez liczbę dni). Wysoka średnia intensywność przy krótkim życiu jest **zgodna z** taktyką *burst-and-burn*, ale jej nie dowodzi: ta taktyka dotyczy rozkładu w czasie (duży budżet na początku, potem wygaszenie), którego nie obserwujemy. Zdanie „co potwierdza stosowanie taktyki” w hipotezie jest interpretacją wykraczającą poza dane; w preprincie proponujemy sformułowanie „co jest zgodne z” (decyzja leada, R20). Dodatkowo krótkie życie może wynikać z szybkiego usuwania reklam przez platformę, a nie z decyzji reklamodawcy (R02).

> **[LEAD – DO WYPEŁNIENIA]** Reguła rozstrzygnięcia hipotez (np. co uznajemy za wsparcie hipotezy i jej składowych: położenie przedziału ufności względem T_L, T_I i p_min): {{P32: reguła decyzyjna dla hipotezy (np. położenie przedziału ufności względem T_L, T_I i p_min) | zależy od: lead, analityk, P13 | domyślnie: brak}}
>
> **[LEAD / INŻ. DANYCH – DO WYPEŁNIENIA]** Traktowanie reklam wciąż aktywnych w dniu pobrania i reklam rozpoczętych przed oknem źródła (czas życia): {{P28: reklamy aktywne w dniu pobrania i obcięte przez okno źródła | zależy od: lead, P06, P03 | domyślnie: brak}}
>
> **[LEAD – DO WYPEŁNIENIA]** Czy populacja jest zawężona do deepfake'ów z wizerunkiem osoby publicznej (zgodnie z pytaniem projektowym), czy obejmuje wszystkie reklamy deepfake scam, a osoba publiczna jest warstwą: {{P30: zawężenie populacji do wizerunku osoby publicznej | zależy od: lead, D1 | domyślnie: brak}}

**Czego pipeline potrzebuje jeszcze od leada (pytania, nie odpowiedzi):** (a) czy przedział czasu życia „2 dni” liczymy włącznie (jak wyżej); (b) czy w preprincie rozróżniamy reklamy deepfake scam z wykorzystaniem wizerunku osoby publicznej i bez niej; (c) czy skala (liczba reklam w populacji) jest wynikiem głównym, czy tylko opisem próby — w obecnym pytaniu badawczym skala nie jest wielkością szukaną, a liczebność populacji służy do oceny precyzji (05, sekcja 3).

## 2. Co mierzy pipeline, a co pochodzi skądinąd

| Wielkość | Skąd | Kto odpowiada |
|---|---|---|
| Przynależność reklamy do populacji badanej: (a) scam, (b) podejrzenie deepfake'a | annotator oceniany, zwalidowany na gold standardzie; kreacja (wideo) wymaga D1 | [PIPELINE] |
| Typ scamu, obecność osoby publicznej (warstwy do podziałów) | j.w. | [PIPELINE] |
| Czas życia L (początek i koniec emisji) | metadane źródła (daty pierwszego i ostatniego wyświetlenia) | [INŻ. DANYCH] dostarcza; obróbka (cenzurowanie, przeżycie): [ANALITYK] |
| Skumulowane wyświetlenia → dzienna intensywność I | metadane źródła (liczba osób lub wyświetleń za okres) | [INŻ. DANYCH] dostarcza; I = suma / L liczy `tools/outcomes.py` |
| Mediana L, udział I ≥ T_I, przedziały ufności | liczone na populacji badanej z korektą błędu klasyfikacji | [PIPELINE] estymata prosta, [ANALITYK] modele |

Annotator oceniany nie mierzy ani czasu życia, ani intensywności. Mierzy **przynależność do klasy** (deepfake scam), a zadaniem pipelinu jest pokazać, jak błąd tej klasyfikacji wpływa na oba wyniki (sekcja 7).

## 3. Jednostka analizy i ramka

- **Jednostka:** unikatowa reklama w źródle (`ad_id`), z reklamodawcą jako klastrem; kreacje są deduplikowane (`creative_id`). Reklamy nie są niezależnymi obserwacjami: w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [gendigital2026]; dla naszych danych koncentrację policzy inżynier danych (P11).
- **Źródło (wpisane z ustaleń zespołu):** głównie **TikTok**, czyli Commercial Content Library i powiązane API (Commercial Content API). Według oficjalnych stron TikToka biblioteka zawiera kreacje, daty emisji, targetowanie i „liczbę osób, które zobaczyły reklamę”, obejmuje obecnie dane z Europy, a dane są dostępne do roku od ostatniego wyświetlenia reklamy; API jest otwarte dla publiczności i badaczy po wniosku przez konto deweloperskie [tiktokcca; tiktokcclnews2023]. Szczegóły pól i warunków potwierdza inżynier danych (P06, P07).
- **Ramka (zbiór kandydujący):** > **[INŻ. DANYCH / LEAD – DO WYPEŁNIENIA]** {{P29: jak zbudowano zbiór reklam kandydujących (kryteria, zapytania po słowach kluczowych lub reklamodawcach) | zależy od: źródło, P01 | domyślnie: brak}}. Okno dat i języki: {{P01: okno dat i języki | zależy od: macierz legalności (P07) | domyślnie: kraje UE (zakres źródła); okno i języki brak}}. Liczebność: {{P02: liczba reklam, kreacji, reklamodawców | zależy od: pobranie danych | domyślnie: nieznana}}.
- **Wymaganie pipelinu wobec ramki:** ramka nie może być zbudowana na wyniku annotatora ocenianego ani na kryterium „scam”; w przeciwnym razie wnioski dotyczą tylko ramki i nie uogólniają się na populację reklam (D9). Wyszukiwanie po słowach kluczowych wyznacza ramkę, więc słowa kluczowe i daty zapytań trzeba zapisać.
- Ramka jest **zbiorem cenzurowanym** (R01, R17): obserwujemy reklamy, które źródło zachowało i udostępniło, tylko do roku od ostatniego wyświetlenia.

## 4. Definicje i dowód na scam

**Populacja badana („reklama typu deepfake scam”).** Reklama spełniająca jednocześnie dwa kryteria:
1. **scam** (poniżej),
2. **podejrzenie deepfake'a**: `media_synthetic_suspected` ∈ {`yes`, `suspected`} (02). Przy `yes` wymagana jest nazwana przesłanka (`media_synthetic_cue`). Analiza wrażliwości: tylko `yes`.

Deepfake nie jest tu ustalany, tylko **podejrzewany** na podstawie kreacji (R19). Pytanie „typu deepfake scam” w obecnym brzmieniu wymaga dostępu do kreacji (wideo): bez D1 populacji nie da się zidentyfikować (sekcja 8). Wizerunek osoby publicznej (`celeb_mention`, `celeb_face_visible`, `celeb_category`) jest warstwą opisową, chyba że lead zawęży populację (P30).

**Scam.** Etykieta scamu pochodzi **wyłącznie z oceny annotatorów referencyjnych** według jawnej reguły codebooka (02): `scam_type` (typ oferty, łącznie z wartościami `not_scam` i `unclear`) oraz `scam_judgement` (czy reklama wygląda na oszukańczą). Zespół nie korzysta z zewnętrznej listy domen ani innego zewnętrznego dowodu scamu, więc nie ma niezależnego sprawdzianu etykiety; błąd etykiety jest jawnym ograniczeniem (R03) i jest szacowany pośrednio przez zgodność między annotatorami (α dla `scam_type` i `scam_judgement`).

**Dlaczego nie wystarczy usunięcie reklamy przez platformę jako definicja scamu.** Jeśli „scam” = „usunięta”, to **czas życia jest z definicji czasem do usunięcia**, więc pytanie o czas życia staje się tautologią, a hipoteza o krótkim życiu byłaby spełniona z konstrukcji (R02, R03). Dlatego scam etykietujemy niezależnie od decyzji platformy, a decyzję platformy (`platform_removal`) traktujemy jako zmienną do analizy wrażliwości.

## 5. Zmienne kodowane przez annotatorów

| Zmienna | Rola w pytaniu badawczym | Poziom |
|---|---|---|
| `scam_type`, `scam_judgement` | kryterium populacji (scam) i warstwy | L1 |
| `media_synthetic_suspected`, `media_synthetic_cue` | kryterium populacji (podejrzenie deepfake'a); niska oczekiwana wiarygodność | L2 |
| `media_type` | opis i kontrola dostępności kreacji | L2 |
| `celeb_mention`, `celeb_category`, `celeb_face_visible` | warstwy opisowe (osoba publiczna w reklamie); kryterium populacji tylko po decyzji P30 | L1, L2 |
| `celeb_id` | pole robocze (dane osobowe, nie raportujemy) | L1 |
| `celeb_claim`, `fake_news_format`, `urgency_cue`, `guaranteed_return_claim`, `authority_cue`, `cta_type` | zmienne dodatkowe; poza rdzeniem pytania (opcjonalne, eksploracyjne) | L1 |

Czas życia i intensywność pochodzą z metadanych; **annotatorzy ich nie widzą** (kodowanie na ślepo).

## 6. Plan pomiaru i walidacji w skrócie

Szczegóły: 02 (codebook), 04 (annotator oceniany), 05 (próba i walidacja).

1. Pilotaż annotacji (30–50 reklam, dwie rundy), poprawa codebooka, zamrożenie.
2. Gold standard: losowanie warstwowe z limitem na reklamodawcę i zapisem prawdopodobieństw włączenia; annotatorzy referencyjni ({{P21: skład | zależy od: lead | domyślnie: nieznany}}); Krippendorff α jako miara główna z progami 0,80 i 0,667 [krippendorff2004].
3. Annotator oceniany jest oceniany względem gold standardu; precision zawsze z prevalence; CI przez bootstrap po klastrach [cameron2015].
4. Wrażliwość na parafrazy promptu i wersję modelu raportowana jako zakres [baumann2025].
5. Wyniki (mediana L, udział I ≥ T_I) liczymy na populacji badanej, a błąd klasyfikacji populacji uwzględniamy (05, sekcja 6): w pierwszej kolejności estymata ważona z gold standardu (wagi 1/p), przedziały bootstrapem po reklamodawcach (`tools/outcomes.py`). Pełne metody (model przeżycia, korekta DSL) wdraża {{P12: ICC i deff; metoda dla czasu życia | zależy od: [ANALITYK] | domyślnie: nie wdrożono}}.

## 7. Analiza błędów (wkład pipelinu)

1. **Macierz pomyłek per klasa** z precision, recall, F1 i prevalence (05, sekcja 5) dla klasy „deepfake scam” oraz osobno dla jej składników (scam, podejrzenie deepfake'a).
2. **Błąd w podziale na warstwy:** język, `scam_type`, obecność osoby publicznej, typ kreacji, reklamodawca (klaster) oraz **przedział czasu emisji** (reklamy krótkotrwałe i długotrwałe).
3. **Wpływ na medianę L i udział I ≥ T_I:** porównanie wyniku na reklamach wskazanych przez annotatora ocenianego (estymata naiwna) z wynikiem z gold standardu; porównanie rozkładów L i I u fałszywych pozytywów, fałszywych negatywów i prawdziwych pozytywów.
4. **Błąd zależny od wyniku:** jeśli fałszywe pozytywy lub negatywy mają inny L lub I niż prawdziwe pozytywy (np. annotator częściej myli krótkotrwałe reklamy), korekta globalna nie wystarcza (R08), a wnioski o medianie L i I trzeba opatrzyć zastrzeżeniem.
5. **Wrażliwość:** zakres wyników po konfiguracjach (parafrazy, wersje) oraz po definicji populacji (`yes` albo `yes` ∪ `suspected`).

## 8. Wykonalność

| Pytanie | Co wiemy | Kto rozstrzyga | Co rozstrzygną dane |
|---|---|---|---|
| Czy jest legalne źródło reklam? | TikTok Commercial Content Library i API: publiczny dostęp, API po wniosku dla badaczy, dane z UE [tiktokcca; tiktokcclnews2023]; warunki dla zapisu i publikacji danych do sprawdzenia w regulaminie | [INŻ. DANYCH] | P07, P20 |
| Czy dostępne są daty początku i końca emisji? | Strona API wymienia datę publikacji i „last seen date”; **nie potwierdzono**, że to pierwszy i ostatni dzień wyświetlania i jak oznaczane są reklamy wciąż aktywne | [INŻ. DANYCH] | D6, P06, P28 |
| Czy dostępna jest liczba wyświetleń? | Strona API wymienia „liczbę osób, które zobaczyły reklamę”; **nie potwierdzono**, czy to wyświetlenia czy unikatowi odbiorcy, czy podawana jest wartość czy przedział i czy jest to suma za okres | [INŻ. DANYCH] | D6, P06 |
| Czy dostępne są kreacje (wideo), potrzebne do wskazania deepfake'a? | Biblioteka zawiera kreacje; **nie potwierdzono** zakresu w API ani prawa do zapisu i przetwarzania | [INŻ. DANYCH] | D1, P04 |
| Czy jest dość reklam deepfake scam do oszacowania mediany i udziału? | Nieznane; zależy od prevalence deepfake scamów w ramce | [PIPELINE] | D2, P09, P02 |
| Czy annotator oceniany zadziała? | Literatura dla tekstu, angielskiego; **brak równorzędnej walidacji dla reklam wideo i dla wykrywania deepfake'ów** [gilardi2023; ziems2024] | [PIPELINE] | D5, P14 |

**Wynik negatywny jest planowany, nie tylko dopuszczany.** Jeśli D6 = NIE (brak dat lub brak wyświetleń), rezultatem projektu jest uzasadniony wniosek, że pomiar czasu życia lub intensywności z danych publicznych nie jest możliwy, wraz z opisem, jakie dane byłyby potrzebne. Jeśli D1 = NIE (brak legalnego dostępu do kreacji), populacji „deepfake scam” nie da się zidentyfikować i trzeba zawęzić pytanie (np. do reklam scamowych bez rozróżnienia deepfake'a; decyzja leada). Zasady kursu oceniają taki wynik na równych prawach.

## 9. Wyniki wstępnej eksploracji (uzupełnić po otrzymaniu danych)

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** statystyki opisowe zbioru:
> - Zakres i rozkład w czasie: {{P17: rozkład reklam w czasie, w tym wstępne rozkłady L i I | zależy od: dane | domyślnie: brak}}
> - Języki: {{P10: rozkład języków | zależy od: dane | domyślnie: brak}}
> - Koncentracja reklamodawców: {{P11: liczba klastrów i udział 10 największych | zależy od: dane | domyślnie: brak}}

> **[PIPELINE – DO WYPEŁNIENIA po pilotażu]**
> - Prevalence scamu i podejrzenia deepfake'a (z ręcznie przejrzanych 50–100 losowych rekordów, z CI): {{P09: prevalence | zależy od: dane, pilotaż | domyślnie: brak}}
> - Notatki z ręcznego przeglądu (co zaskoczyło, co poprawić w codebooku): {{P23: notatki i przykłady z pilotażu | zależy od: dane | domyślnie: brak}}

Narzędzia pomocnicze: `python tools/audit_dataset.py dane.csv` (statystyki opisowe, udział reklam bez daty końca) i `python tools/outcomes.py dane.csv --class-col gold --weight-col weight` (mediana L, udział I ≥ T_I, pasmo dla reklam aktywnych). Liczb z eksploracji nie wpisujemy do karty bez uruchomienia zapisanego w dzienniku.

## 10. Ograniczenia i źródła błędu (wersja do karty)

Pełny rejestr w 06. Najważniejsze dla pytania badawczego:

1. **Dane zagregowane (ustalone przez zespół):** nie ma oceny godzina po godzinie, tylko suma wyświetleń podzielona przez liczbę dni. Dzienna intensywność to średnia, więc nie pokazuje, czy ruch był skoncentrowany na początku (R20).
2. **Interpretacja *burst-and-burn* wykracza poza dane** (R20); krótkie życie może wynikać z moderacji platformy (R02, R03).
3. **Zależność L i I:** I = suma / L, więc przy L = 1 dzienna intensywność jest równa całej sumie, a krótkie reklamy mają mechanicznie wyższą i bardziej zmienną I (R21). Raportujemy także skumulowane wyświetlenia.
4. **Definicja pola wyświetleń:** osoby czy wyświetlenia, wartość czy przedział; próg 25 tys. może wypaść w przedziale (R22).
5. **Cenzurowanie** reklam wciąż aktywnych i retencja źródła do roku od ostatniego wyświetlenia (R01, R17).
6. **Deepfake jest podejrzewany, nie ustalony** (R19); klasyfikacja wideo bez rozpoznawania twarzy (R09).
7. **Klastrowanie** reklamodawców (R06) i **ramka** zależna od zapytań (R18).
8. Dane osobowe i regulaminy (R09, R10).
9. Mała liczba reklam w populacji (R12): wyniki mogą mieć szerokie przedziały, co jest wynikiem, nie błędem.

## 11. Stan wiedzy i uzasadnienie wartości badania

> **[LEAD – DO WYPEŁNIENIA]** {{P31: stan wiedzy, luka, uzasadnienie wartości badania | zależy od: lead | domyślnie: brak}}

Źródła zebrane w ramach pracy pipelinu (metody pomiaru, annotacja, ocena): 07.

---

# 02. Codebook v0.1

**Status:** wersja robocza przed pilotażem. Zmiany tylko przez dziennik zmian (`templates/codebook_changelog.md`) i podniesienie wersji. Lista dozwolonych wartości jest w `tools/schema.yaml` (źródło prawdy); po zmianie uruchom `python tools/checks.py consistency`.

**Dlaczego tak:** codebook jest jedną instrukcją dla wszystkich annotatorów (referencyjnych i ocenianego); ta sama wersja służy do annotacji referencyjnej i do promptu annotatora ocenianego, co jest wzorcem z prac porównujących LLM z annotatorami [gilardi2023; halterman2025].

**Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”. **Pytanie badawcze (wpisane z ustaleń leada):** jaka jest mediana czasu życia reklam typu deepfake scam i jaka jest ich dzienna intensywność wyświetleń (01). Codebook służy do zaklasyfikowania reklamy do **populacji badanej**: scam (`scam_type`, `scam_judgement`) oraz podejrzenie deepfake'a (`media_synthetic_suspected` ∈ {`yes`, `suspected`}, z nazwaną przesłanką w `media_synthetic_cue`), i do podziału na warstwy (typ scamu, obecność osoby publicznej). Czas życia i dzienna intensywność pochodzą z metadanych, nie z codebooka. Czy populacja jest dodatkowo zawężona do wizerunku osoby publicznej, rozstrzyga lead: {{P30: zawężenie populacji do wizerunku osoby publicznej | zależy od: lead, D1 | domyślnie: brak}}.

**Rdzeń i zmienne dodatkowe.** Rdzeń (kryteria populacji): `scam_type`, `scam_judgement` oraz (po D1) `media_synthetic_suspected` z pomocniczą `media_synthetic_cue`; rdzeń opisowy: `celeb_mention`, `celeb_category`, a po D1 `celeb_face_visible`, `media_type`. Zmienne oznaczone „(dodatkowa)” są poza rdzeniem pytania: opcjonalne i eksploracyjne, kodowane tylko jeśli starczy czasu na pilotaż. Codebook przechodzi co najmniej dwie rundy pilotażu, zanim zostanie zamrożony (05).

**Przykłady poniżej są wymyślone** (fikcyjne osoby, fikcyjne marki) i służą wyłącznie do zilustrowania reguł. Zostaną zastąpione zanonimizowanymi przykładami z pilotażu: {{P23: przykłady z pilotażu do uzupełnienia | zależy od: pilotaż, P07 | domyślnie: przykłady fikcyjne}}.

## Nomenklatura

- **Annotator:** każdy podmiot (osoba lub narzędzie), który stosuje definicje z tego codebooka do pojedynczej reklamy i przypisuje wartości zmiennych. Nie ustala „prawdy”, tylko stosuje zasady.
- **Annotator referencyjny (R1, R2, …):** annotator, którego uzgodnione etykiety tworzą gold standard.
- **Annotator oceniany (O):** annotator, którego jakość sprawdzamy względem gold standardu (w 04 opisany jako wariant A–E).
- **Pilotaż:** próbne kodowanie małej próby reklam przed zamrożeniem codebooka; służy do poprawy definicji, a nie do uzyskania wyników badania.
- **Krippendorff α (alfa):** miara zgodności między kodującymi, skorygowana o zgodność przypadkową. Wartość 1 to pełna zgodność, 0 to zgodność na poziomie losowym. Przyjęte progi [krippendorff2004]: α ≥ 0,80 zmienna wiarygodna; 0,667 ≤ α < 0,80 tylko wnioski wstępne; α < 0,667 zmiennej nie uznajemy za mierzalną. Dla rzadkich kategorii α może być niskie mimo dobrego kodowania, dlatego sprawdzamy też zgodność pozytywną i negatywną (05).
- **Cohen κ (kappa):** podobna miara dla dwóch kodujących; wymaga tych samych dwóch osób dla całej próby.
- **Gold standard:** próba reklam zakodowana ręcznie i uzgodniona (adjudykowana), względem której oceniamy instrument (05).
- **Zamrożenie codebooka:** po pilotażu wersja i jej hash są ustalone; zmiana wymaga nowej wersji i wpisu w dzienniku zmian.

Jeśli kodowanie wykonuje jedna osoba, α między kodującymi nie da się policzyć; stosujemy wtedy powtórne kodowanie tej samej próby po przerwie i opisujemy to jako ograniczenie (05).

## Zasady ogólne

1. **Jednostka kodowania:** pojedyncza unikatowa kreacja (`creative_id`); kopie tej samej kreacji u tego samego reklamodawcy są deduplikowane przed losowaniem (03, 05).
2. **Kodowanie na ślepo:** annotator nie widzi zasięgu, czasu emisji, wyniku annotatora ocenianego ani informacji zewnętrznych (usunięcie reklamy przez platformę). Powód: znajomość wyniku obciążałaby kodowanie kryteriów populacji.
3. **Kodujemy to, co widać w reklamie**, nie to, co annotator wie z zewnątrz. Wyjątek: rozpoznanie osoby po opisie (`implied`) wymaga jednoznaczności opisu, a nie wiedzy specjalnej.
4. **Kategoria `unsure` jest pełnoprawna.** Wybieraj ją zamiast zgadywać. Odsetek `unsure` jest raportowany; wysoki odsetek oznacza zbyt niejasną definicję.
5. **Dwa poziomy:**
   - **L1** (z tekstu i metadanych): wykonalny bez dostępu do kreacji.
   - **L2** (wizualne): kodowany wyłącznie po potwierdzeniu punktu decyzyjnego D1 (legalny dostęp do kreacji): {{P04: dostępność kreacji i podstawa prawna | zależy od: regulamin źródła | domyślnie: brak dostępu, L2 wyłączony}}.
6. **Ograniczenie konstruktu L1:** wizerunek osoby publicznej poziom L1 mierzy tylko jako *wzmiankę* w tekście. Reklama z twarzą osoby publicznej i bez nazwiska w tekście zostanie na L1 zakodowana jako `none`. Dla pytania badawczego (populacja = deepfake scam) to błąd klasyfikacji *warstwy* „osoba publiczna”, a nie populacji; staje się błędem populacji dopiero, jeśli lead zawęzi populację do wizerunku osoby publicznej (P30; 06, R05).

## Zmienne poziomu L1

### `celeb_mention` (kryterium populacji)

Czy tekst reklamy (treść, nagłówek, podpis linku, nazwa strony reklamodawcy, widoczna domena) odnosi się do osoby publicznej.

| Wartość | Definicja | Przykład (fikcyjny) | Kontrprzykład |
|---|---|---|---|
| `explicit_name` | Nazwisko, imię i nazwisko lub powszechnie znany pseudonim osoby publicznej występuje w tekście, nagłówku, podpisie linku lub domenie | „Jan Przykładowski ujawnia metodę na 500 zł dziennie" | „Eksperci radzą" (brak osoby) |
| `implied` | Brak nazwiska, ale opis jednoznacznie wskazuje konkretną osobę publiczną | „Prezes największego banku w kraju zdradza..." (jednoznaczne w kontekście) | „Znany biznesmen" (niejednoznaczne; wybierz `unsure` lub `none`) |
| `none` | Brak odniesienia do osoby publicznej | reklama suplementu bez odwołania do osoby | — |
| `unsure` | Nie da się rozstrzygnąć | tekst wspomina „znaną prezenterkę" bez możliwości ustalenia, czy to konkretna osoba | — |

**Przypadki graniczne.** (a) Właściciel marki o tym samym nazwisku co celebryta: `none`, jeśli nic nie wskazuje na osobę publiczną. (b) Postać fikcyjna lub maskotka: `none`. (c) Osoba publiczna wymieniona neutralnie jako element newsa bez sugestii poparcia: `explicit_name`, a rodzaj użycia koduje `celeb_claim`. (d) Osoba zmarła: kodujemy jak żywą. (e) Wymienione kilka osób: `explicit_name`, w `celeb_id` pierwsza wymieniona, reszta w `notes`.

### `celeb_id`

Tekst wolny, znormalizowane nazwisko ("Imię Nazwisko") albo `unrecognized`. Wymagane, gdy `celeb_mention` ∈ {`explicit_name`, `implied`}; puste lub `na`, gdy `none`. **Dane osobowe:** to pole zawiera dane osób, więc jest przechowywane tylko w pliku roboczym i nie trafia do materiałów publicznych; raportujemy tylko `celeb_category` i zagregowane liczby: {{P07: podstawa prawna przetwarzania nazwisk osób publicznych | zależy od: ocena inżyniera danych | domyślnie: pole nieraportowane publicznie}}.

### `celeb_category`

| Wartość | Definicja |
|---|---|
| `politician` | polityk, urzędnik, osoba pełniąca funkcję publiczną |
| `business_finance` | przedsiębiorca, bankier, osoba ze świata finansów |
| `sport` | sportowiec, trener |
| `media_entertainment` | aktor, prezenter, artysta, dziennikarz |
| `influencer` | twórca internetowy znany głównie z platform |
| `other` | osoba publiczna spoza powyższych |
| `na` | gdy `celeb_mention` = `none` albo `unsure` |

Przypadek graniczny: osoba należąca do dwóch kategorii. Wybierz tę, w której osoba występuje w reklamie.

### `celeb_claim` (mechanizm; dodatkowa)

Co reklama każe zrozumieć o stosunku osoby do oferty.

| Wartość | Definicja | Przykład (fikcyjny) |
|---|---|---|
| `fabricated_quote` | Reklama przypisuje osobie cytat lub wypowiedź | „Jan Przykładowski: «To zmieniło moje życie»" |
| `fabricated_event` | Reklama opisuje zdarzenie z udziałem osoby (rzekomy wywiad, skandal, program TV) | „Po wizycie w studiu prezenter ujawnił..." |
| `product_recommendation` | Osoba rzekomo poleca lub używa produktu bez cytatu | „Ulubiony suplement Jana Przykładowskiego" |
| `none` | Osoba wymieniona, ale bez przypisanego stosunku do oferty | |
| `unsure` | Nie da się rozstrzygnąć | |

Gdy `celeb_mention` = `none`, zostaw puste. Reguła pierwszeństwa przy kilku mechanizmach: `fabricated_quote` > `fabricated_event` > `product_recommendation`.

### `fake_news_format` (dodatkowa)

`yes`, jeśli reklama naśladuje artykuł prasowy, wiadomość lub wywiad (nagłówek w stylu serwisu informacyjnego, „źródło: ..."), `no`, jeśli to czytelna reklama produktu, `unsure` przy wątpliwości. Przypadek graniczny: reklama z ramką „artykuł sponsorowany" ale stylizacją newsa: `yes`.

### `scam_type`

Typ oferty wynikający z treści reklamy.

| Wartość | Definicja |
|---|---|
| `investment_crypto` | inwestycje, kryptowaluty, „platformy", obietnica zysku z kapitału |
| `health_supplements` | suplementy, „cudowne" kuracje, produkty zdrowotne z nierealnymi obietnicami |
| `giveaway_contest` | rzekome nagrody, konkursy, rozdawanie produktów |
| `benefits_subsidies` | rzekome dopłaty, świadczenia, odszkodowania |
| `shop_counterfeit` | sklep z nierealnie niskimi cenami, podróbki |
| `other` | inny rodzaj oferty |
| `not_scam` | oferta wygląda na legalną |
| `unclear` | nie da się ustalić typu oferty |

Zmienna oznacza *typ oferty*, a nie dowód oszustwa. `not_scam` i `unclear` pozwalają zakodować również reklamy, które okażą się legalne. Przypadek graniczny: oferta łącząca dwa typy (np. suplement z konkursem): typ głównej obietnicy w nagłówku.

### `scam_judgement`

Ocena annotatora, czy reklama wygląda na oszukańczą (`scam`, `not_scam`, `unclear`) na podstawie wyłącznie reklamy. Razem z `scam_type` (wartość inna niż `not_scam` i `unclear`) tworzy etykietę scamu, bo nie ma zewnętrznego dowodu. Reguła: reklama jest scamem, gdy annotator referencyjny zakoduje `scam_judgement` = `scam`; `scam_type` opisuje jego rodzaj. Niezgodność `scam_judgement` = `scam` i `scam_type` = `not_scam` jest błędem kodowania do wyjaśnienia na pilotażu. Brak niezależnego dowodu oznacza, że etykieta jest tak wiarygodna, jak zgodność annotatorów (α), i jest to jawne ograniczenie (06, R03).

### `urgency_cue` (dodatkowa)

`yes`, jeśli reklama stosuje presję czasu lub rzadkości („tylko dziś", „zostało 3 sztuki", odliczanie), `no`, jeśli nie, `unsure` przy wątpliwości.

### `guaranteed_return_claim` (dodatkowa)

`yes`, jeśli reklama obiecuje pewny zysk, brak ryzyka lub konkretną stopę zwrotu („gwarantowany zysk", „bez ryzyka", „2000 zł tygodniowo"), `no`, jeśli nie, `unsure` przy wątpliwości.

### `authority_cue` (dodatkowa)

Na czym reklama opiera wiarygodność.

| Wartość | Definicja |
|---|---|
| `celebrity` | wiarygodność oparta na osobie publicznej (jej opinii, doświadczeniu) |
| `institution_or_expert` | instytucja, rzekomy ekspert, „badania naukowe", lekarz |
| `none` | brak odwołania do autorytetu |
| `unsure` | nie da się rozstrzygnąć |

Reguła: jeśli występują oba, wybierz dominujący (wyróżniony w nagłówku lub pierwszy w tekście). Zmienna jest zależna od `celeb_mention` (przy `celeb_mention` = `none` wartość `celebrity` jest niedozwolona; to jest też kontrola jakości).

### `cta_type` (dodatkowa)

Wezwanie do działania: `learn_more`, `sign_up`, `buy`, `download`, `contact`, `other`, `none`. Jeśli jest kilka, wybierz główne (przycisk reklamy ma pierwszeństwo przed tekstem).

## Zmienne poziomu L2 (tylko po D1)

Kodowane wyłącznie wtedy, gdy kreacje są legalnie dostępne: {{P04: dostępność kreacji | zależy od: regulamin źródła | domyślnie: niedostępne}}.

### `media_type`

`image`, `video`, `carousel`, `text_only`, `unavailable` (kreacja nie jest dostępna mimo włączonego L2).

### `celeb_face_visible` (kryterium populacji L2)

`yes`, jeśli na kreacji widać twarz osoby, którą annotator referencyjny uznaje za osobę publiczną **bez** pomocy zewnętrznych narzędzi rozpoznawania twarzy i bez ustalania, kim jest; `no`; `unsure`; `na_no_media`. **Nie używamy automatycznego rozpoznawania twarzy** (identyfikacja po twarzy to przetwarzanie danych biometrycznych objęte zakazem z art. 9 ust. 1 RODO bez przesłanki z ust. 2; szczegóły w 04, zasada 4). Zmienną koduje wyłącznie annotator referencyjny (osoba); annotator oceniany jej nie koduje. Wartością rezerwową jest `unsure`.

### `media_synthetic_suspected`

Ocena annotatora referencyjnego, czy kreacja (obraz lub wideo) wygląda na wygenerowaną lub zmanipulowaną (deepfake, obraz wygenerowany, podmiana twarzy lub głosu). Zmienna oznacza **podejrzenie, nie ustalenie**: z samego materiału nie da się wiarygodnie stwierdzić, że jest deepfake'iem (06, R19), a wartość `yes` nie znaczy „dowiedziono deepfake'a”. Zmienna jest **kryterium populacji badanej** („deepfake scam”): wartości `yes` i `suspected` włączają reklamę do populacji (wrażliwość: tylko `yes`); `no`, `unsure` i `na_no_media` wyłączają lub oznaczają brak oceny. Ponieważ jest tylko podejrzeniem i ma niską oczekiwaną zgodność, jej błąd jest jednym z głównych źródeł niepewności wyników (06, R19). Reklamy z wartością `unsure` nie wchodzą do populacji, ale ich udział raportujemy, a w analizie wrażliwości traktujemy je kolejno jako włączone i wyłączone.

| Wartość | Definicja |
|---|---|
| `yes` | co najmniej jedna wyraźna przesłanka, którą można wskazać w kreacji (zob. `media_synthetic_cue`), bez równie prawdopodobnego wyjaśnienia innego niż synteza |
| `suspected` | słaba lub niejednoznaczna przesłanka (np. wygładzona skóra, dziwny ruch warg w jednym ujęciu), możliwe też inne wyjaśnienie (filtr, kompresja, retusz, animacja) |
| `no` | kreacja wyświetlona dobrej jakości, bez przesłanek syntezy |
| `unsure` | nie da się ocenić: niska rozdzielczość, bardzo krótki kadr, brak dźwięku przy ocenie ruchu ust, kreacja uszkodzona |
| `na_no_media` | brak obrazu lub wideo (kreacja tylko tekstowa albo niedostępna) |

Zasady rozstrzygania:
1. Oceniamy to, co widać i słychać w kreacji. Nie szukamy źródła obrazu, nie używamy narzędzi do wykrywania deepfake'ów ani rozpoznawania twarzy, nie ustalamy, kim jest osoba na materiale (04, zasada 4).
2. `yes` wymaga przesłanki, którą annotator potrafi nazwać w `media_synthetic_cue`; samo „wygląda dziwnie” to najwyżej `suspected`.
3. Jeśli reklama zawiera tylko obraz statyczny, ocena dotyczy obrazu; brak możliwości oceny ruchu ust nie jest przesłanką za ani przeciw (wtedy `no` albo `unsure`, zależnie od jakości obrazu).
4. W razie wahania między `yes` a `suspected` wybierz `suspected`; między `suspected` a `no`, gdy nie umiesz nazwać żadnej przesłanki, wybierz `no`; gdy jakość uniemożliwia ocenę, wybierz `unsure`, nie `no`.
5. Karuzela: oceń wszystkie karty; wartość to najwyższy poziom podejrzenia spośród nich (kolejność `yes` > `suspected` > `no`), `unsure` tylko gdy żadna karta nie pozwala na ocenę.

Przypadki brzegowe:
- **Znana osoba z ewidentnie nierealnego kontekstu** (np. wypowiada się w sprawie inwestycji, której nigdy nie promowała): to treść fałszywego poparcia (`celeb_claim`), nie dowód syntezy obrazu; sama treść nie uzasadnia `yes`.
- **Retusz, filtr beauty, sztuka cyfrowa, ilustracja, animacja, grafika AI wyraźnie niefotograficzna**: kodujemy `no` dla deepfake'a w sensie wizerunku osoby; jeśli kreacja jest jawnie oznaczona jako wygenerowana, patrz `platform_label` poniżej.
- **Oznaczenie przez platformę lub reklamodawcę** („wygenerowano przez AI”): zapisz `platform_label` w `media_synthetic_cue`; wartość `media_synthetic_suspected` ustaw na `yes`, jeśli oznaczenie dotyczy osoby na materiale, w pozostałych przypadkach `no`. Brak oznaczenia nie jest przesłanką za `no`.
- **Montaż z archiwalnych nagrań** (zmiana głosu, przycięty wywiad) bez oznak syntezy: `suspected` tylko wtedy, gdy ruch warg lub głos wyraźnie nie pasują; inaczej `no`.
- **Podróbka, sobowtór, aktor**: z materiału nie da się odróżnić od syntezy; `no` albo `suspected`, zależnie od przesłanek. Nie ustalamy tożsamości.
- **Wideo bez dźwięku lub z wyciętą ścieżką**: ruch ust nie może być jedyną przesłanką; ocena na podstawie obrazu, a przy złej jakości `unsure`.

### `media_synthetic_cue`

Zmienna pomocnicza do `media_synthetic_suspected`: **główna przesłanka**, na której oparto ocenę (jeśli kilka, wybierz najsilniejszą). Pozwala sprawdzić, na czym annotator opiera podejrzenie, i analizować niezgodności między annotatorami.

| Wartość | Definicja |
|---|---|
| `visual_artifact` | artefakty obrazu: zniekształcone dłonie, zęby, uszy, okulary, krawędzie twarzy, niespójne światło lub cienie, mrugnięcie lub mimika nienaturalne |
| `lip_audio_mismatch` | ruch warg nie pasuje do wypowiadanego tekstu |
| `voice_unnatural` | głos metaliczny, monotonny lub niespójny z osobą i obrazem |
| `platform_label` | oznaczenie treści jako wygenerowanej lub zmanipulowanej (platforma lub reklamodawca) |
| `other` | inna przesłanka (opisz w `notes`) |
| `none` | brak przesłanki (przy `no`, `unsure`) |
| `na` | brak mediów (przy `na_no_media`) |

Reguły spójności (sprawdza `python tools/checks.py sheet`): przy `yes` i `suspected` wartość `none` i `na` jest niedozwolona; przy `no` i `na_no_media` przesłanka musi być `none` lub `na` (albo pusta).

## Pola zewnętrzne (nie kodowane przez annotatorów)

Wypełnia pipeline na podstawie danych źródła, po zakończeniu kodowania kryteriów populacji: `dest_domain` (opcjonalnie, jeśli źródło ją podaje), `platform_removal` (definicje w `tools/schema.yaml`). Dostępność zależy od P05 i P06. Zewnętrznej listy scamów nie używamy.

## Procedura

1. Pilotaż 1 (30–50 reklam, każdy annotator referencyjny koduje samodzielnie), potem omówienie niezgodności, korekta definicji, wersja 0.2 z wpisem w dzienniku zmian.
2. Pilotaż 2 na nowej próbie; jeśli zmienna wciąż nie osiąga α ≥ 0,667, usuń ją z pomiaru (10, punkt D3).
3. Dopiero po zamrożeniu codebooka losowanie i annotacja zbioru gold standardu (05).
4. Każda zmiana po zamrożeniu = nowa wersja + powtórna ocena na próbie kontrolnej.

---

# 03. Specyfikacja interfejsu: pipeline i inżynier danych

Ten dokument mówi, **czego pipeline potrzebuje od inżyniera danych** i **co pipeline sprawdzi po otrzymaniu danych**. Treść merytoryczną dotyczącą źródeł, podstaw prawnych, ramki i data statementu uzupełnia inżynier danych; w miejscach, które do niego należą (oznaczone **[INŻ. DANYCH – DO WYPEŁNIENIA]**), są placeholdery i nie są wypełnione propozycją. **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”; definicje wielkości mierzonych (czas życia, dzienna intensywność) są ustalone z leadem w 01 (P27, P28). **Źródło główne (ustalone przez zespół): TikTok Commercial Content Library i Commercial Content API** [tiktokcca; tiktokcclnews2023].

## 1. Zasada nadrzędna

Wszystkie dane pochodzą z legalnych źródeł, zgodnie z regulaminami stron i licencjami. **Nie używamy scrapowania ani narzędzi do masowego pobierania mediów ze stron**, nawet gdy są popularne w pracach badawczych, jeśli regulamin źródła tego nie dopuszcza. Pierwszym zadaniem inżyniera danych jest macierz legalności (sekcja 3); pipeline nie rusza danych, zanim ją zobaczy.

## 2. Wymagany schemat tabeli (jedna wiersz = jedna reklama w źródle)

Kolumny **wymagane** to minimum do wykonania planu pomiaru (01). Kolumny **warunkowe** zależą od tego, co źródło legalnie udostępnia (punkty D1, D6). Nazwy kolumn można zmienić, ale mapowanie musi być opisane.

| Kolumna | Opis | Wymagana? | Uwagi |
|---|---|---|---|
| `ad_id` | stabilny identyfikator reklamy w źródle | tak | klucz główny |
| `creative_id` | identyfikator unikatowej kreacji po deduplikacji (ten sam tekst/obraz u tego samego reklamodawcy = jedna kreacja) | tak | metoda deduplikacji opisana w data statement |
| `advertiser_id` | stabilny identyfikator reklamodawcy (strony) | tak | klaster w analizie; pseudonimizacja, jeśli wymagana |
| `platform` | platforma emisji | tak | |
| `delivery_start`, `delivery_stop` | pierwszy i ostatni dzień emisji (koniec pusty = reklama aktywna lub brak danych; znaczenie opisuje data statement) | tak | czas życia L = stop − start + 1 (P28); brak = D6. Strona API wymienia datę publikacji i „last seen date”: czy to jest to samo, potwierdza P06 |
| `retrieval_date` | data pobrania rekordu | tak | stan źródła w tym dniu; konieczna do oceny cenzurowania prawostronnego |
| `countries_delivered` | kraje dostarczenia | tak | zakres próby (P01) |
| `ad_text`, `headline`, `link_caption` | tekst reklamy | tak | wejście dla poziomu L1 |
| `language` | język tekstu (metoda detekcji opisana) | tak | D8 |
| `cta_label` | etykieta przycisku wezwania do działania | jeśli dostępna | |
| `dest_url` lub `dest_domain` | adres docelowy | opcjonalna | tylko pole opisowe (zewnętrznej listy scamów nie używamy); P05 |
| `reach_total` | skumulowana liczba wyświetleń (lub osób, które zobaczyły reklamę) za cały okres emisji, jako liczba lub przedział | tak | dzienna intensywność I = reach_total / L (P27); ustalono, że źródło daje tylko sumę za okres, bez rozkładu godzinowego ani dziennego. Czy to wyświetlenia czy unikatowi odbiorcy, wartość czy przedział: P06. Przy przedziałach: kolumny `reach_min`, `reach_max` |
| `reach_*` (inne) | rozbicia zasięgu (kraj, wiek, płeć), jeśli źródło je zwraca | jeśli dostępne | opis, nie wymagane do pytania |
| `frame_source` | kryterium lub zapytanie, przez które reklama trafiła do ramki | warunkowa | niezależność ramki od annotatora ocenianego (D9, P29) |
| `creative_available` | czy kreacja (obraz/wideo) jest legalnie dostępna | tak | D1 |
| `creative_path` | ścieżka do pliku kreacji | warunkowa | tylko jeśli legalnie wolno |
| `source_removed_flag` | czy źródło oznacza reklamę jako usuniętą/naruszającą zasady | jeśli dostępne | dowód zewnętrzny, nie wynik; R03 |
| `source_name`, `source_version` | skąd i w jakiej wersji | tak | odtwarzalność |

Dostępność poszczególnych pól (według oficjalnej dokumentacji, nie scraperów): {{P06: znaczenie pól czasu emisji i wyświetleń w TikTok Commercial Content Library / API | zależy od: oficjalna dokumentacja źródła | domyślnie: nieznane}}. Wiadomo z oficjalnej strony API: pola daty publikacji i „last seen date”, „liczba osób, które zobaczyły reklamę”, targetowanie dla reklam płatnych, metadane reklamy i reklamodawcy; dane tylko z UE; dostęp do roku od ostatniego wyświetlenia [tiktokcca].

## 3. Macierz legalności: szkielet

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** Cała macierz.

Jeden wiersz = jedno źródło. Bez wypełnionej macierzy nie rozpoczynamy pracy na danych.

| Źródło | Kto udostępnia | Podstawa (regulamin, licencja, umowa) | Wymagania dostępu (tożsamość, wniosek, umowa uczelni) | Pola dostępne | Kreacje? | Retencja | Co wolno zapisać i publikować | Dane osobowe? | Ocena |
|---|---|---|---|---|---|---|---|---|---|
| TikTok Commercial Content Library i Commercial Content API [tiktokcca; tiktokcclnews2023] | TikTok | {{P07: podstawa (Developer Terms of Service, warunki biblioteki) \| zależy od: inżynier danych \| domyślnie: brak}} | konto TikTok for Developers z oficjalnym adresem e-mail i wniosek; odpowiedź deklarowana w ciągu 2 dni roboczych; API dla publiczności i badaczy | data publikacji, „last seen date”, liczba osób, targetowanie, metadane reklamy i reklamodawcy (dokładna lista: P06) | biblioteka: tak; API: {{P04: kreacje w API \| zależy od: dokumentacja \| domyślnie: niedostępne}} | do roku od ostatniego wyświetlenia | {{P07: co wolno zapisać i publikować \| zależy od: inżynier danych \| domyślnie: brak}} | nazwy reklamodawców; wizerunek osób | {{P07: ocena \| zależy od: inżynier danych \| domyślnie: brak}} |
| {{P07: ewentualne źródło dodatkowe (np. biblioteka reklam Meta; tylko jeśli zespół je włącza) \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |

Pytania, na które macierz musi odpowiedzieć (lista pytań jest moja, odpowiedzi należą do inżyniera danych):

1. Czy TikTok Commercial Content API zwraca pełny zestaw pól potrzebnych do pytania: tekst, daty pierwszego i ostatniego wyświetlenia, skumulowane wyświetlenia, adres docelowy, kreację? Oficjalna strona wymienia datę publikacji, „last seen date” i liczbę osób; **znaczenie tych pól i adres docelowy wymagają potwierdzenia w oficjalnej dokumentacji** (P05, P06).
2. Czy regulamin pozwala na zapis i dalsze przetwarzanie kreacji (obraz/wideo)? (D1)
3. Kto i kiedy składa wniosek o dostęp do API (konto deweloperskie, opis celu badawczego) i czy wystarcza wniosek indywidualny, czy potrzebna jest zgoda uczelni? (P20)
4. Czy źródło podaje adres docelowy reklamy (pole opisowe)? (P05)
5. Czy nazwiska osób publicznych w tekście reklam są danymi osobowymi wymagającymi dodatkowej podstawy w kontekście RODO i jak ograniczyć ich przetwarzanie? (R09)
6. Jakie są ograniczenia retencji i do kiedy dane trzeba pobrać, aby nie zniknęły? (R01)
7. Które pola określają początek i koniec emisji, co oznacza pusty koniec emisji, i czy źródło zwraca reklamy już zakończone lub usunięte oraz na jak długo? (czas życia: P28, R01, R17)
8. Jak zbudowano zbiór reklam kandydujących (kryteria, zapytania, listy) i czy jest to opisane w data statement? (P29, D9)

## 4. Data statement

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** Cały data statement.

Szkielet na podstawie praktyk dokumentacji danych [bender2018; gebru2021]. Link i wersja: {{P08: data statement | zależy od: P07 | domyślnie: brak}}. Minimalne pola: cel zbioru, źródło i sposób dostępu, okno dat, kraje i języki, metoda deduplikacji, znane luki i obciążenia, dane osobowe i sposób ich ograniczenia, licencja i warunki użycia, wersja i data pobrania.

## 5. Co pipeline sprawdzi po otrzymaniu danych

Narzędzie: `python tools/audit_dataset.py dane.csv` (opis w README). Sprawdzenia:

1. Zgodność schematu: kolumny wymagane, typy, klucze, duplikaty `ad_id` i `creative_id`.
2. Zakres dat, odsetek brakujących dat końca i pól warunkowych.
3. Liczba reklam, unikatowych kreacji, reklamodawców; koncentracja (udział 10 największych, indeks Herfindahla, efektywna liczba klastrów); wyniki trafiają do P02 i P11.
4. Rozkład języków i krajów (P10, D8), rozkład miesięcy.
5. Dostępność pól czasu emisji, wyświetleń i adresu docelowego (P05, P06), dostępność kreacji (P04); udział reklam bez daty końca emisji i rozkład czasu emisji reklam zakończonych (jako opis, bez korekty cenzurowania; P28, D6); wartości `reach_total` równe zero lub brakujące; przedziały zamiast liczb.
6. Czy jest data statement i wpis w macierzy legalności; **jeśli nie, pipeline zatrzymuje pracę i zgłasza to**.

Wyniki audytu są wpisywane do rejestru placeholderów (00) z odwołaniem do uruchomienia (hash danych w dzienniku).

---

# 04. Plan instrumentu pomiarowego

Instrument, czyli **annotator oceniany (O)**, koduje zmienne codebooka (02) na dużej liczbie reklam. Klasyfikuje reklamy do populacji badanej, czyli **reklam typu deepfake scam** (scam oraz podejrzenie deepfake'a), i do warstw (typ scamu, obecność osoby publicznej). **Czas życia i dzienna intensywność wyświetleń pochodzą z metadanych** (01), nie od annotatora ocenianego, więc jego zadanie jest wąskie i walidowalne. **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”
## Nomenklatura

- **Annotator:** każdy podmiot (osoba lub narzędzie), który stosuje codebook do reklamy i przypisuje wartości zmiennych.
- **Annotator referencyjny (R):** tworzy gold standard. **Annotator oceniany (O):** to, co sprawdzamy (instrument); wariant A–E poniżej opisuje, czym jest O.- **Poziom L1 / L2:** L1 to zmienne mierzalne z tekstu i metadanych; L2 to zmienne wymagające obrazu lub wideo, dostępne tylko po decyzji D1.
- **Gold standard:** próba reklam zakodowana ręcznie i uzgodniona, względem której oceniamy instrument (05).
- **Prevalence:** udział reklam z daną cechą w próbie lub populacji. Precision zależy od prevalence, więc bez niej nie da się jej interpretować.
- **CI (przedział ufności):** zakres prawdopodobnych wartości wielkości w populacji; szeroki przy małej próbie. W ocenie instrumentu liczymy go bootstrapem po klastrach (reklamodawcach), bo reklamy tego samego reklamodawcy nie są niezależne.
- **Flip rate:** odsetek reklam, którym zmiana promptu lub konfiguracji modelu zmienia etykietę; miara wrażliwości instrumentu.

## 1. Zasady

1. Annotator oceniany jest **hipotezą do sprawdzenia**, a nie założeniem. Literatura o LLM jako annotatorach dotyczy głównie **tekstu i angielskiego**: Gilardi i in. (tweety i artykuły, n = 6183 łącznie) [gilardi2023], Ziems i in. (benchmarki tekstowe, angielskie; według streszczenia wtórnego κ w zakresie 0,40–0,65 w 8 z 17 zadań klasyfikacji, a LLM zwykle nie zastępują w pełni annotacji ludzkiej) [ziems2024]. Dla reklam z obrazem i polskim tekstem nie mamy równorzędnego wsparcia, więc zgodność trzeba zmierzyć u siebie (05).
2. Ten sam codebook dla wszystkich annotatorów, wersjonowany i zamrożony przed oceną [gilardi2023; halterman2025].
3. Każde uruchomienie jest zapisane w dzienniku (`tools/run_log.py`): model, wersja, parametry, seed, hash promptu, hash danych, hash codebooka. Powód: wyniki modeli z API zmieniają się w czasie, a konfiguracja wpływa na wnioski [baumann2025].
4. **Bez rozpoznawania twarzy.** Identyfikacja celebryty opiera się na tekście; na poziomie L2 wizualnym ocenia wyłącznie annotator referencyjny (02, `celeb_face_visible`), bez ustalania tożsamości po twarzy. Powód prawny: automatyczne rozpoznawanie osoby po twarzy to przetwarzanie danych biometrycznych w celu jednoznacznej identyfikacji, czyli szczególnej kategorii danych, której przetwarzanie **jest zakazane na podstawie art. 9 ust. 1 RODO**, chyba że zachodzi jeden z wyjątków z art. 9 ust. 2 (np. wyraźna zgoda, cele naukowe z podstawą w prawie i zabezpieczeniami); sama fotografia nie jest daną biometryczną, dopóki nie jest przetwarzana specjalnym środkiem technicznym umożliwiającym jednoznaczną identyfikację (motyw 51). Organ holenderski uznał w 2024 r. przetwarzanie danych biometrycznych przez Clearview AI za naruszenie art. 9 ust. 1 i nałożył karę 30,5 mln EUR [edpb2024clearview; rodo2016motyw51]. **Nie znaleźliśmy w tym projekcie przesłanki z art. 9 ust. 2, która pozwalałaby na takie rozpoznawanie** (ocena własna, nie opinia prawna; potwierdzić z IOD uczelni, P07), więc **nie stosujemy żadnego narzędzia (w tym VLM) do ustalania tożsamości osoby na podstawie twarzy**, ani w kodzie, ani w promptach. Prompty VLM nie mogą zawierać pytań o to, kim jest osoba na obrazie; zob. też 06, R09.
5. **Bez scrapowania.** Annotator oceniany działa na tabeli dostarczonej przez inżyniera danych z legalnego źródła (03). Nie pobieramy mediów ze stron reklam, jeśli regulamin źródła tego nie dopuszcza ({{P04: legalność pobierania kreacji | zależy od: regulamin źródła | domyślnie: nie pobieramy}}).

## 2. Macierz alternatyw

Ocena jakościowa do wypełnienia po pilotażu; kolumny „ryzyka" to ustalenia już teraz.

| Wariant | Poziom | Zalety | Ograniczenia i ryzyka | Warunek użycia |
|---|---|---|---|---|
| A. Baseline słownikowy: lista osób publicznych + dopasowanie wzorców | L1 | Prosty, w pełni odtwarzalny, tani; konieczny jako punkt odniesienia | Nie wykryje wariantów pisowni, odmian, opisów (`implied`); zależy od jakości listy: {{P25: źródło i licencja listy osób publicznych \| zależy od: licencja \| domyślnie: brak}} | zawsze |
| B. LLM tekstowy z promptem z codebooka | L1 | Radzi sobie z opisami i odmianami; wzorzec jak w literaturze [gilardi2023; ziems2024] | Wrażliwość na prompt i wersję [baumann2025]; koszt i limity: {{P16: koszt i limity \| zależy od: P02, P15 \| domyślnie: nieznane}}; polski mniej przebadany niż angielski | domyślny wariant dla L1 |
| C. Model otwarty uruchamiany lokalnie | L1/L2 | Pełna kontrola wersji, odtwarzalność, brak wysyłania danych na zewnątrz; ewentualnie jedyny wariant w środowisku bez eksportu | Zwykle słabszy; wymaga zasobów obliczeniowych; mniej wygodny | gdy środowisko danych wyklucza zewnętrzne API: {{P20: środowisko analizy \| zależy od: uczelnia \| domyślnie: nieznane}} |
| D. Multimodalny LLM (VLM) dla obrazu i tekstu | L2 | Jedyny wariant do kryterium populacji `media_synthetic_suspected` i `media_synthetic_cue` oraz do `media_type`; dla wideo wymaga klatek lub wideo i ewentualnie dźwięku (niezweryfikowane, jakie wejście przyjmie wybrany model: {{P15: wybrany annotator oceniany | zależy od: D1, D5, P20 | domyślnie: brak}}) | **Brak równorzędnej walidacji w literaturze dla tego zadania**; zbiory pokrewne to chińskie media społecznościowe i inne zadania [chasm2026; adsprofiles2025], przeczytaj je w całości przed użyciem jako wzorca; ryzyko dla `media_synthetic_suspected` (wykrywanie deepfake'ów jest trudne; wartość `suspected` to podejrzenie, R19) | tylko po D1 (legalny dostęp do kreacji) |
| E. Annotacja wyłącznie przez annotatorów referencyjnych na próbie + estymacja korygowana | L1/L2 | Najlepsza wiarygodność | Mała próba, szerokie CI | wariant zapasowy, gdy B/C/D nie osiągną zgodności (D5) |

## 3. Drzewo decyzji

1. **D1: czy kreacje są legalnie dostępne?**
   - **Nie** (scenariusz domyślny, dopóki nie ma dowodu): dostępny jest tylko poziom L1 (tekst i metadane). Z samego tekstu nie da się wskazać deepfake'a, więc populacji „deepfake scam” nie da się zidentyfikować: lead decyduje o zawężeniu pytania (P30) albo raportujemy wynik negatywny. Warianty A, B lub C dalej służą do klasyfikacji scamu i wzmianki o osobie publicznej (02, zasada 6).
   - **Tak:** dodatkowo L2; wariant D dla `media_synthetic_suspected`, `media_synthetic_cue` i `media_type`, a `celeb_face_visible` koduje wyłącznie annotator referencyjny (annotator oceniany nie ocenia tożsamości osób na obrazie). Jeśli wolno tylko oglądać kreacje w interfejsie źródła (bez zapisu pliku), kreacje oglądają annotatorzy referencyjni, a wariant D jest niedostępny: zostaje wariant E (annotacja próby przez annotatorów referencyjnych z estymacją korygowaną).
2. **Środowisko analizy** (P20): jeśli dane są dostępne wyłącznie w środowisku bez eksportu i bez wywołań zewnętrznych API, wariant C lub E.
3. **D5 po pilotażu:** jeśli zgodność annotatora ocenianego z gold standardem jest zbliżona do zgodności annotatorów referencyjnych między sobą (kryterium: 05, sekcja 5), użyj do całości z korektą błędu; w przeciwnym razie wariant E.

## 4. Prompt: reguły wersjonowania

- Prompty są plikami w repozytorium (`prompts/`), nazwa `prompt_<zmienna>_v<N>.txt`. Zmiana = nowy plik, nie nadpisanie.
- Treść promptu zawiera codebook dla zmiennej (definicje, wartości, przykłady, kontrprzykłady, reguły graniczne) bez dodawania własnych reguł, których nie ma w codebooku. Prompt nie jest drugim codebookiem.
- Dla każdej zmiennej: wartości dozwolone wymuszamy formatem wyjścia (np. JSON z listą wartości), odpowiedź spoza listy jest błędem i jest liczona.
- Parafrazy: dla każdego promptu przygotowujemy co najmniej 2 parafrazy do oceny wrażliwości (05, sekcja 5, punkt 3) [baumann2025].
- Dobór promptu odbywa się na zbiorze rozwijania; zbiór testowy jest nietykalny do końca (05).

## 5. Dziennik uruchomień

Pola: czas UTC, kto, model i wersja, parametry, seed, plik i hash promptu, plik i hash danych wejściowych, plik i hash codebooka, wersja Pythona, uwagi. Komenda: `python tools/run_log.py ...` (opis w pliku). Dziennik jest też materiałem dowodowym przy obronie indywidualnej (09).

## 6. Wybór annotatora ocenianego: do wypełnienia po pilotażu

> **[PIPELINE – DO WYPEŁNIENIA po pilotażu]**

- Wybrany annotator oceniany (wariant) i uzasadnienie: {{P15: instrument (nazwa, wersja, parametry) | zależy od: D1, D5, P20 | domyślnie: wariant A + B}}
- Wynik pierwszego testu względem gold standardu: {{P14: P/R/F1 z CI, zgodność z annotatorami | zależy od: pilotaż | domyślnie: brak}}
- Koszt i czas przetworzenia całości: {{P16: koszt i limity | zależy od: P02, P15 | domyślnie: nieznane}}

---

# 05. Plan gold standardu i walidacji annotatora ocenianego

Cel: wykazać (albo wykazać brak), że annotator oceniany klasyfikuje reklamy do populacji badanej (reklamy typu deepfake scam: scam oraz podejrzenie deepfake'a) z błędem, który znamy i który uwzględniamy przy szacowaniu mediany czasu życia i udziału reklam o wysokiej dziennej intensywności wyświetleń. Miara sukcesu to wiarygodny wniosek, nie wysokie F1 (zasady kursu). **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” **Pytanie badawcze (01):** jaka jest mediana czasu życia reklam deepfake scam i ich dzienna intensywność wyświetleń.
Mierzymy jakość annotatora ocenianego (O), a nie cechy reklam. Dla każdej zmiennej priorytetowej (`scam_type`, `media_synthetic_suspected`) osobna wartość jest klasą, np. `media_synthetic_suspected = yes`. Annotatorzy referencyjni kodują próbę reklam, a ich uzgodnione etykiety tworzą gold standard; reklama, której gold standard przypisuje daną wartość, jest *pozytywem* tej klasy. Annotator oceniany koduje te same reklamy, a recall to odsetek pozytywów, które też oznaczył. Liczą się oba kierunki błędu: fałszywe pozytywy wprowadzają do populacji reklamy, które nią nie są (precision), a pominięte pozytywy wypychają z niej reklamy, które do niej należą (recall); oba zniekształcają medianę czasu życia i udział reklam o wysokiej intensywności, jeśli te reklamy różnią się czasem życia lub intensywnością od reszty. Klasą o największym znaczeniu jest przynależność do populacji badanej, czyli łączne spełnienie kryteriów scamu i podejrzenia deepfake'a (wymaga D1). Poniższe wartości mówią, ile pozytywów danej klasy musi mieć gold standard, żeby ten recall zmierzyć z założoną dokładnością.

Kolejność jest wiążąca: **pilotaż, korekta codebooka, zamrożenie codebooka, losowanie, annotacja, zamrożenie gold standardu, dopiero potem pierwsze uruchomienie annotatora ocenianego na zbiorze testowym.** Zbiór rozwijania promptu i zbiór testowy są rozłączne; po obejrzeniu wyników na zbiorze testowym prompt się nie zmienia (powód: strojenie na zbiorze oceniającym zawyża jakość; wzorzec zamrożonej instrukcji i oceny na danych niewidzianych przy budowie codebooka: [halterman2025]).

### Nomenklatura

- **Gold standard:** próba reklam zakodowana ręcznie i uzgodniona; to względem niej oceniamy annotatora ocenianego.
- **Recall (czułość):** spośród reklam rzeczywiście pozytywnych, odsetek wykrytych przez annotatora ocenianego. Recall = 0,8 znaczy, że znajduje 8 na 10 prawdziwych pozytywów i pomija 2.
- **Przedział ufności (CI, 95%):** zakres, w którym przy założonym modelu leży prawdziwy recall w całej populacji reklam, a nie tylko w próbie. „Połowa szerokości” (±) to odległość od środka do krańca przedziału. Tabela mówi więc, jak dokładnie da się zmierzyć recall, mając daną liczbę pozytywów. Przykład: 50 pozytywów i recall 0,8 daje ±0,109, czyli prawdziwy recall to mniej więcej 0,69–0,91.
- **Przedział Wilsona:** metoda liczenia CI dla odsetków, która jest wiarygodniejsza niż prosta metoda przy małych próbach i wartościach bliskich 0 lub 1.
- **Klaster:** grupa reklam jednego reklamodawcy.
- **ICC (współczynnik korelacji wewnątrzklasowej):** jak bardzo reklamy w tym samym klastrze są do siebie podobne. 0 to brak podobieństwa, 1 to identyczność.
- **Efekt projektu (deff):** ile razy próba klastrowa jest „mniej warta” niż próba niezależna. Efektywna liczba niezależnych obserwacji to n / deff. Np. deff = 1,9 przy 300 reklamach oznacza, że informację niesie ok. 158 niezależnych reklam.
- **m w deff = 1 + (m − 1)·ICC:** średnia liczba reklam w klastrze.
- **Bootstrap po klastrach:** metoda liczenia CI, w której losujemy ze zwracaniem całe klastry (reklamodawców), a nie pojedyncze reklamy; uwzględnia podobieństwo reklam z jednego klastra.
- **Klasa raportowana osobno:** kategoria zmiennej (np. jeden typ scamu), dla której podajemy własne wyniki. Przy mniej niż 60 pozytywach (nasza heurystyka) raportujemy ją jako eksploracyjną.

## 1. Jednostka i ramka losowania

- Jednostka: unikatowa kreacja (`creative_id`), po deduplikacji kopii. Liczebność i okno dat: {{P02: liczba reklam, kreacji i reklamodawców | zależy od: pobranie danych | domyślnie: nieznana}}.
- Reklamodawca jest klastrem. Ruch scamowy jest skoncentrowany: w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [gendigital2026]; to wynik dla angielskich reklam w UE i Wielkiej Brytanii, więc dla naszych danych koncentrację trzeba policzyć ({{P11: liczba klastrów i udział 10 największych | zależy od: dane | domyślnie: nieznane}}).
- Ramka jest zbiorem cenzurowanym (06, R01): obserwujemy to, co biblioteka reklam zachowała i udostępniła. Luki w bibliotece reklam opisano dla amerykańskich reklam politycznych [edelson2020; lepochat2022]; przeniesienie na reklamy komercyjne w UE nie jest ustalone.

## 2. Projekt próby (dwufazowe losowanie warstwowe z limitem na reklamodawcę)

Implementacja: `tools/sampling.py`. Każdy rekord w próbie ma zapisane prawdopodobieństwo włączenia i wagę 1/p.

1. **Warstwy** definiujemy wyłącznie z cech znanych przed annotacją: miesiąc, język, typ scamu z baseline'u, wynik baseline'u słownikowego (np. słowa kluczowe scamu i obecność nazwiska z listy osób publicznych), ewentualnie predykcja annotatora ocenianego, a także długość emisji i wyświetlenia z metadanych **tylko jeśli** nie wprowadzi to zależności próby od wyniku (patrz uwaga niżej). Powód: rzadką klasę (deepfake scam) trzeba nadpróbkować (losowanie proste dałoby zbyt mało pozytywów), a metody korekty błędu klasyfikatora wymagają próby ze znanymi prawdopodobieństwami [egami2025dsl].
2. **Limit na reklamodawcę** w komórce (warstwa x reklamodawca): wartość limitu jest parametrem; wybór: {{P24: limit reklam na reklamodawcę w komórce | zależy od: rozkład reklamodawców w danych | domyślnie: heurystyka własna, bez źródła; ustaw tak, aby żaden reklamodawca nie przekraczał 5% próby}}.
3. **Nadpróbkowanie warstw z rzadką klasą** i warstwa z predykcją negatywną (żeby oszacować recall, trzeba mieć etykiety także tam, gdzie annotator oceniany mówi „nie").
4. **Uwaga:** warstwowanie po czasie życia lub intensywności jest dozwolone, bo wagi 1/p je uwzględniają, ale zmienia efektywną liczebność; annotatorzy referencyjni nadal nie widzą wartości wyniku (kodowanie na ślepo).
5. Seed, parametry i hash danych wejściowych zapisujemy w dzienniku uruchomień (`tools/run_log.py`).

Test narzędzia na danych syntetycznych: estymator Horvitza-Thompsona z wagami odtwarza prawdziwą sumę (test `TestSampling`), a limit na reklamodawcę jest respektowany.

## 3. Liczebność

Nie ma w literaturze uniwersalnej liczby. Podejście, które obronimy: liczebność wynika z docelowej szerokości przedziału ufności, jak w planowaniu badań zgodności [donner1987; rotondi2012]. Poniższe wartości są policzone przez `tools/sample_size.py` i dotyczą przedziałów Wilsona przy założeniu niezależności obserwacji.

**Szerokość 95% CI recallu a liczba pozytywów w gold standardzie** (połowa szerokości):

| liczba pozytywów | recall = 0,7 | recall = 0,8 | recall = 0,9 |
|---|---|---|---|
| 20 | ±0,187 | ±0,168 | ±0,137 |
| 30 | ±0,156 | ±0,139 | ±0,111 |
| 50 | ±0,123 | ±0,109 | ±0,085 |
| 75 | ±0,102 | ±0,089 | ±0,067 |
| 100 | ±0,088 | ±0,078 | ±0,060 |
| 150 | ±0,073 | ±0,064 | ±0,048 |

**Interpretacja tabeli.** Wartości recall w kolumnach (0,7; 0,8; 0,9) są założeniami planistycznymi (wartościami a priori), a nie wynikami: prawdziwego recallu annotatora ocenianego jeszcze nie znamy. Połowa szerokości przedziału (margines błędu) zależy od liczby pozytywów i od samego recallu (im bliżej 1, tym węższy przedział), dlatego podajemy kilka scenariuszy, a do planowania przyjmujemy zachowawczo 0,8. Faktyczny recall wyznaczamy dopiero na zbiorze testowym.

**Rola przedziału ufności w tym projekcie.** Estymacja przedziałowa zamiast punktowej pozwala: (a) ocenić, czy annotator oceniany jest wystarczająco zgodny z gold standardem (D5), uwzględniając niepewność próby; (b) zaplanować liczebność gold standardu z docelowego marginesu błędu; (c) oznaczyć klasy o zbyt szerokim przedziale jako eksploracyjne, bez wniosków wprost; (d) unikać nadinterpretacji różnic między grupami, gdy przedziały się w dużej mierze pokrywają; (e) jawnie pokazać niepewność w karcie M1, gdzie próba jest mała. Przedział Wilsona zachowuje się poprawnie przy małych próbach i dla odsetków (recall, precision, prevalence) bliskich 0 lub 1, w odróżnieniu od przedziału normalnego (Walda), który może wychodzić poza [0, 1] i ma niedostateczne pokrycie [brown2001].

Przy recall ≈ 0,8: ±0,10 wymaga ok. 60 pozytywów, ±0,075 ok. 109, ±0,05 ok. 245.

**Wybór docelowy (heurystyka własna, nie z literatury):** celujemy w co najmniej 60 pozytywów w każdej klasie raportowanej osobno (połowa szerokości ok. ±0,10); klasy z mniejszą liczbą raportujemy jako eksploracyjne. Liczba pozytywów, nie łączne n, decyduje o precyzji. Wartość docelowa: {{P09: liczba pozytywów osiągalna w próbie | zależy od: prevalence, D2 | domyślnie: 60 na klasę}}.

**Uzasadnienie wyboru:** przy recall ≈ 0,8 przedział Wilsona o połowie szerokości ±0,10 wymaga ok. 60 pozytywów; zawężenie do ±0,075 wymaga ok. 109, a do ±0,05 ok. 245, więc koszt ręcznej annotacji rośnie szybciej niż zysk w precyzji. Wartość ±0,10 jest decyzją zespołu (pozwala odróżnić annotatora wykrywającego większość pozytywów od pomijającego połowę), a nie wartością z literatury; metoda wyboru liczebności z docelowej szerokości przedziału pochodzi z planowania badań zgodności [donner1987; rotondi2012]. Rachunek zakłada niezależne obserwacje i recall 0,8; przy klastrowaniu (deff > 1) i innym recallu margines będzie szerszy, dlatego wartość weryfikujemy na danych (P09, P12).

**Liczebność dla hipotezy (populacja badana).** Obie składowe hipotezy sprowadzają się do udziału w populacji: składowa o czasie życia (mediana L ≤ T_L) jest równoważna temu, że co najmniej 50% reklam ma L ≤ T_L, a składowa o intensywności mówi, że więcej niż p_min = 50% reklam ma I ≥ T_I. Precyzja zależy więc od liczby reklam *w populacji badanej* (liczby pozytywów gold standardu), a nie od łącznej liczby reklam. Połowa szerokości 95% CI Wilsona dla udziału bliskiego 0,5 (wyliczenie: `tools/sample_size.py wilson`, obserwacje niezależne):

| liczba reklam w populacji | udział 0,5 | udział 0,7 |
|---|---|---|
| 30 | ±0,168 | ±0,156 |
| 60 | ±0,123 | ±0,113 |
| 100 | ±0,096 | ±0,088 |
| 150 | ±0,079 | ±0,073 |
| 250 | ±0,062 | ±0,056 |
| 400 | ±0,049 | ±0,045 |

Znaczenie: jeśli prawdziwy udział jest bliski progu 50% (np. 0,55), przedział o połowie szerokości ±0,10 nie rozstrzygnie hipotezy; potrzeba wtedy kilkuset reklam w populacji. Jeśli udział jest wyraźnie dalej od progu (np. 0,8), wystarcza kilkadziesiąt. Przy klastrowaniu połowa szerokości rośnie o czynnik √deff (wzór niżej). Mediana czasu życia mierzonego w pełnych dniach jest zmienną dyskretną, więc przedział mediany może być bardzo wąski lub zdegenerowany (np. samo „1–2 dni”); dlatego główny wniosek formułujemy przez udział reklam z L ≤ T_L.

**Korekta na klastrowanie.** Przedziały Wilsona zakładają niezależne obserwacje. Przy klastrach efektywna liczba obserwacji jest mniejsza o efekt projektu. Wzór deff = 1 + (m − 1)·ICC (Kish; **do sprawdzenia w źródle**): dla klastrów średniej wielkości 10 i ICC = 0,1 deff = 1,9, czyli 300 reklam odpowiada ok. 158 niezależnym; dla ICC = 0,3 deff = 3,7 i ok. 81. ICC z naszych danych: {{P12: ICC i deff | zależy od: dane | domyślnie: nieznane}}. Dlatego przedziały ufności liczymy bootstrapem po klastrach (`tools/evaluation.py`), co jest zgodne z zaleceniami dla danych grupowanych [cameron2015].

## 4. Annotacja referencyjna

- Plan zakłada co najmniej 2 niezależnych annotatorów referencyjnych, kodowanie na ślepo (codebook, zasada 2), rozstrzyganie niezgodności przez trzecią osobę lub dyskusję z zapisem decyzji. Skład: > **[LEAD – DO WYPEŁNIENIA]** {{P21: annotatorzy referencyjni (ilu, którzy) | zależy od: lead | domyślnie: nieznany}}.
- **Jeden annotator referencyjny:** zgodności R–R nie da się wtedy policzyć. Stosujemy powtórne kodowanie tej samej próby przez R1 po przerwie i w innej kolejności, liczymy α między pierwszym a drugim przejściem i zapisujemy w ograniczeniach, że mierzy to stabilność jednej osoby, a nie jednoznaczność definicji. Progi α poniżej dotyczą zgodności między annotatorami; przy jednym annotatorze zmienne raportujemy jako wstępne.
- Miara główna: **Krippendorff α** (dowolna liczba annotatorów, braki dozwolone), uzupełniająco kappa Cohena i, dla zmiennych binarnych, prevalence index, bias index oraz zgodność pozytywna i negatywna [cicchetti1990; byrt1993; chen2009]. Surowej zgodności procentowej nie raportujemy jako głównej miary.
- Progi: α ≥ 0,80 wiarygodne, 0,667–0,80 tylko wnioski wstępne, poniżej 0,667 odrzucić; autor zaleca dobierać próg do kosztu błędnych wniosków, więc to konwencja, a nie prawo [krippendorff2004].
- **Uwaga: paradoks kappa.** Symulacja (`tools/sample_size.py alpha-sim`, dwóch annotatorów, każdy z trafnością 95%, błędy niezależne, czyli założenie optymistyczne) daje oczekiwane α ≈ 0,60 przy częstości zjawiska 0,1 i ok. 0,78 przy 0,3, **niezależnie od liczby jednostek**:

| n | częstość 0,1: oczekiwane α | połowa szer. 95% CI | częstość 0,3: oczekiwane α | połowa szer. 95% CI |
|---|---|---|---|---|
| 60 | 0,585 | ±0,306 | 0,771 | ±0,170 |
| 100 | 0,608 | ±0,228 | 0,781 | ±0,132 |
| 200 | 0,606 | ±0,160 | 0,784 | ±0,091 |
| 400 | 0,604 | ±0,112 | 0,779 | ±0,066 |

Znaczenie: dla rzadkiej zmiennej niskie α może wynikać z niezrównoważenia kategorii, a nie z niskiej jakości kodowania [feinstein1990; cicchetti1990]. Dlatego (a) raportujemy α razem z prevalence i zgodnością pozytywną/negatywną, (b) zgodność dla zmiennych rzadkich liczymy także na podpróbie wzbogaconej o pozytywy (z zaznaczeniem, że miara dotyczy tej podpróby), (c) nie usuwamy zmiennej tylko dlatego, że α < 0,80 przy bardzo rzadkiej kategorii; patrz D3 w `10_playbook`. Ostrzeżenie: PABAK nie mierzy tego samego co kappa przy niskiej prevalence [chen2009], więc nie zastępuje α.
- Pilotaż: 30–50 reklam, dwie rundy (02, Procedura). Wyniki: {{P13: α per zmienna z CI | zależy od: pilotaż | domyślnie: brak}}. Przy 30–50 jednostkach przedziały są bardzo szerokie (tabela powyżej); pilotaż służy do poprawiania codebooka, nie do dowodzenia wiarygodności.

## 5. Ocena annotatora ocenianego

Narzędzia: `tools/evaluation.py` (macierz pomyłek, P/R/F1 z wagami 1/p, bootstrap klastrowy), `tools/prompt_robustness.py` (wrażliwość na prompt i powtórzenie).

1. **Annotator oceniany jako kolejny annotator.** Zgodność O–gold porównujemy ze zgodnością annotatorów referencyjnych między sobą (R–R; α, kappa). O nie jest oceniany surowszym kryterium niż R. Formalna procedura uzasadniania zastąpienia annotatora przez LLM na niewielkim podzbiorze istnieje w literaturze [calderon2025]; zastosowanie do naszych zmiennych do ustalenia po lekturze pracy.
2. **Metryki per klasa:** precision, recall, F1, prevalence, każda z 95% CI z bootstrapu po klastrach. **Precision zawsze razem z prevalence w próbie**: przy rzadkiej klasie precision spada, nawet gdy recall jest dobry (przykład niskiego precision w pracy nierecenzowanej: [radboud2025]).
3. **Wrażliwość na konfigurację:** to samo zadanie z kilkoma parafrazami promptu, z powtórzeniami i, jeśli możliwe, z więcej niż jednym modelem; raportujemy odsetek elementów, w których etykieta się zmienia, zakres kappa między konfiguracjami i zakres prevalence. Powód: replikacja 37 zadań adnotacji z 21 badań pokazała, że konfiguracja potrafi zmienić wniosek (ok. 31% hipotez z błędnym wnioskiem dla najlepszych modeli) [baumann2025]. Wynik końcowy raportujemy jako zakres po konfiguracjach.
4. **Analiza błędów w warstwach:** wg języka, `scam_type`, kategorii osoby, typu kreacji, reklamodawcy (klastra) oraz **przedziału czasu emisji** (reklamy krótko- i długotrwałe). Sprawdzamy, czy błędy annotatora ocenianego zależą od cech powiązanych z wynikiem (czas życia); to krytyczne, bo błąd zależny od wyniku daje obciążenie, którego korekta globalna nie usunie (R08).
5. **Wpływ na wyniki:** (a) mediana L i udział reklam z I ≥ T_I: porównanie estymaty naiwnej (na reklamach wskazanych przez O) z estymatą z gold standardu (wagi 1/p; `tools/outcomes.py`), z przedziałem po klastrach; (b) porównanie rozkładów L i I u prawdziwych pozytywów, fałszywych pozytywów i fałszywych negatywów oraz sprawdzenie, czy błąd różni się między reklamami krótko- i długotrwałymi; (c) opcjonalnie liczebność populacji (częstość klasy × liczebność ramki; `tools/estimators.py`). Obróbka cenzurowania i model czasu życia: > **[ANALITYK – DO WYPEŁNIENIA]**.
6. **Zmienna deepfake (`media_synthetic_suspected`, `media_synthetic_cue`).** Jest kryterium populacji, więc jej błąd bezpośrednio wpływa na wyniki. Oceniamy ją osobno, jako zmienną porządkową o niskiej oczekiwanej wiarygodności: α/κ między annotatorami referencyjnymi (R–R) per wartość oraz odsetek `unsure`. Gold standardem jest tu zgodna ocena R, a nie prawda o syntezie materiału, więc zgodność z gold nie dowodzi, że kreacja jest deepfake'iem (06, R19). Jeśli α < 0,667, wyniki dla populacji definiowanej tą zmienną raportujemy jako wstępne i pokazujemy wrażliwość (tylko `yes`; `yes` ∪ `suspected`; `unsure` włączone lub wyłączone); przy bardzo niskiej zgodności populacja „deepfake scam” nie jest wiarygodnie mierzalna i to jest wynik.
7. Wynik pierwszego testu: > **[PIPELINE – DO WYPEŁNIENIA]** {{P14: zgodność annotatora ocenianego z gold standardem | zależy od: pilotaż, P15 | domyślnie: brak}}. Decyzja: D5.

## 6. Korekta błędu pomiaru w analizie końcowej

Wniosek z literatury: predykcje modelu analizowane tak, jakby były obserwacjami bez błędu, dają obciążenie i nieprawidłowe przedziały ufności nawet przy dokładności powyżej 90%; metoda DSL łączy predykcje z mniejszą próbą etykiet eksperckich losowaną ze znanymi prawdopodobieństwami [egami2025dsl].

- **Co mamy dla mediany i udziałów:** `tools/outcomes.py` (L, I, ważona mediana, ważone udziały, pasmo dla reklam aktywnych, bootstrap po reklamodawcach). Estymata jest liczona na reklamach z gold standardu zaklasyfikowanych jako populacja badana, z wagami 1/p; jest nieobciążona co do doboru próby, ale nie wykorzystuje predykcji annotatora ocenianego na całej ramce, więc ma większą wariancję niż metoda łącząca oba (DSL).
- **Co mamy dla częstości klasy:** `tools/estimators.py`, estymator różnicowy dla prostego parametru (liczbę reklam w klasie dostajemy mnożąc częstość przez liczebność ramki P02). Test na danych syntetycznych (300 powtórzeń): błąd naiwnej estymaty −0,029 (SE 0,0008), po korekcie −0,002 (SE 0,0017), czyli brak wykrywalnego obciążenia; estymator po korekcie ma jednak ok. dwukrotnie większe odchylenie standardowe niż naiwny (0,029 vs 0,014). To kompromis obciążenie–wariancja, o którym trzeba pisać w preprincie.
- **Czego nie mamy:** pełnego DSL dla regresji z kowariatami ani korekty dla modelu czasu życia. Będą potrzebne, jeśli analiza obejmie związek czasu życia lub intensywności z cechami reklamy (np. typ scamu, obecność osoby publicznej) albo model przeżycia dla reklam aktywnych (Kaplan–Meier; w repozytorium jest tylko pasmo mediany). To jest zadanie dla analityka po lekturze pracy [egami2025dsl]: > **[ANALITYK – DO WYPEŁNIENIA]**; status: do wdrożenia.
- Analiza wrażliwości: `prevalence_from_sens_spec` pozwala sprawdzić, jak zmieniałaby się częstość przy założonej czułości i swoistości z przedziału ufności walidacji. Używać z zakresem wartości.

## 7. Co jest przyjęte bez źródła (heurystyka własna)

1. Docelowa liczba 60 pozytywów na klasę raportowaną osobno.
2. Limit 5% próby na reklamodawcę.
3. Dwie rundy pilotażu po 30–50 reklam.

Każdą z tych wartości trzeba uzasadnić lub zmienić na podstawie danych (P09, P11, P13) i opisać w preprincie jako decyzję własną.

---

# 06. Rejestr ryzyk i ograniczeń

Ryzyka są wpisem do karty M1 (jawne ograniczenia i źródła błędu to kryterium oceny). **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” **Pytanie badawcze (01):** mediana czasu życia reklam deepfake scam i ich dzienna intensywność wyświetleń; hipoteza: mediana ≤ 2 dni, ponad 50% reklam ≥ 25 tys. wyświetleń na dzień. Znacznik na początku ryzyka wskazuje, kto je rozstrzyga lub potwierdza: **[PIPELINE]**, **[INŻ. DANYCH]**, **[LEAD]**; ryzyka danych i projektu zgłosił pipeline z własnej perspektywy, a ich opis i ocenę muszą potwierdzić wskazane role. Prawdopodobieństwo i wpływ to **ocena własna** (niski/średni/wysoki) do rewizji po danych; nie są oparte na pomiarze. „Wskaźnik z danych" mówi, co sprawdzić, gdy dane już są.

| ID | Ryzyko | Skutek dla wniosku | Praw. | Wpływ | Środek zaradczy | Wskaźnik z danych |
|---|---|---|---|---|---|---|
| R01 | **[INŻ. DANYCH]** **Biblioteka reklam jako zbiór cenzurowany**: widzimy to, co platforma zachowała i udostępniła; TikTok udostępnia dane tylko do roku od ostatniego wyświetlenia reklamy [tiktokcca]; reklamy usunięte mogą znikać. Luki bibliotek opisano dla amerykańskich reklam politycznych na Facebooku [edelson2020; lepochat2022]; dla reklam komercyjnych TikToka w UE nie jest to ustalone | Obciążenie selekcją: jeśli reklamy usunięte szybko znikają z biblioteki, mediana czasu życia może być zawyżona | wysokie | wysoki | Jawnie ograniczyć wnioski do reklam widocznych w źródle w oknie dat; zapisywać datę pobrania; nie uogólniać na wszystkie reklamy | rozkład czasu między końcem emisji a pobraniem; udział reklam bez daty końca (P03) |
| R02 | **[INŻ. DANYCH / LEAD]** **Czas życia zniekształcony przez egzekwowanie**: platforma może szybciej usuwać reklamy z osobą publiczną (ma do tego dedykowany mechanizm porównania twarzy [meta2024celebbait]), więc czas życia zależy od polityki egzekwowania, a nie tylko od „trwałości” zjawiska | Błędna interpretacja czasu emisji | wysokie | wysoki | Opisać czas życia jako czas widoczności w źródle; zestawić z `platform_removal`; zastrzeżenie w karcie | rozkład czasu emisji reklam usuniętych i nieusuniętych |
| R03 | **[PIPELINE / INŻ. DANYCH]** **Etykieta scamu zależna od usunięcia przez platformę**: jeśli „scam" = usunięcie, to czas życia jest czasem do usunięcia (tautologia), a hipoteza o krótkim życiu byłaby spełniona z konstrukcji, bo populacja to reklamy wykryte i usunięte; dodatkowo reklamy z osobą publiczną są wykrywane osobnym mechanizmem; ponieważ nie ma zewnętrznego dowodu scamu (lista CERT nie jest używana), etykieta zależy wyłącznie od oceny annotatorów | Czas życia nie do zinterpretowania | wysokie | wysoki | Scam etykietować niezależnie od decyzji platformy, wyłącznie według reguły codebooka (`scam_judgement`, `scam_type`); brak zewnętrznego dowodu jest jawnym ograniczeniem; analiza wrażliwości na definicję | α dla `scam_type` i `scam_judgement`; zgodność `scam_judgement` z `platform_removal` (informacyjnie) |
| R04 | **[PIPELINE]** **Brak niezależnego dowodu scamu**: etykieta scamu pochodzi wyłącznie z oceny annotatorów referencyjnych (bez zewnętrznej listy domen) | Błąd etykiety nie jest mierzalny wprost; część reklam „scam” może być legalna lub odwrotnie; populacja zależy od subiektywnej oceny | średnie | wysoki | Jawna reguła w codebooku; dwie rundy pilotażu; α z prevalence i zgodnością pozytywną/negatywną; adjudykacja trzeciej osoby; scam jako zmienna z poziomem pewności (`unclear`) | α dla `scam_type` i `scam_judgement`; odsetek `unclear` |
| R05 | **[PIPELINE]** **Błąd pomiaru warstwy „osoba publiczna” (L1 mierzy wzmiankę, nie wizerunek)**: reklamy z twarzą bez nazwiska są kodowane jako `none`. Dla pytania badawczego dotyczy to podziału na warstwy, nie populacji; staje się błędem populacji, jeśli lead zawęzi populację do wizerunku osoby publicznej (P30) | Zaniżona liczebność warstwy „osoba publiczna”; porównania warstw obciążone | średnie | średni | Walidacja `celeb_mention`; korekta błędu (05, sekcja 6); jawne ograniczenie konstruktu; decyzja leada o konstrukcie (P30) | recall `celeb_mention` w gold standardzie |
| R06 | **[PIPELINE / INŻ. DANYCH]** **Koncentracja u kilku reklamodawców**: efektywna liczba obserwacji = liczba klastrów, nie reklam; przy niewielkiej liczbie klastrów standardowe błędy odporne na klastrowanie zaniżają niepewność [cameron2015] | Zawyżona pewność wniosków | wysokie | wysoki | Bootstrap po klastrach lub agregacja do reklamodawcy; limit w losowaniu; D7 | P11, P12 |
| R07 | **[LEAD]** **Dzienna intensywność zależy od budżetu i algorytmu dostarczania, nie tylko od kreacji ani od „taktyki”**: wysoka intensywność może wynikać z dużego budżetu, targetowania lub konta o dużej wiarygodności | Interpretacja intensywności jako strategii reklamodawcy jest niepewna | wysokie | wysoki | Opisywać I jako wielkość obserwowaną; nie wnioskować o intencji (R20); budżet dla reklam komercyjnych prawdopodobnie niedostępny (P06) | dostępność pól budżetu i targetowania (P06) |
| R08 | **[PIPELINE]** **Błąd instrumentu zależny od cech powiązanych z wynikiem** | Obciążenie, którego globalna korekta nie usunie | średnie | wysoki | Analiza błędów wg warstw; próba z etykietami w każdej warstwie (05) | zgodność model–gold wg `scam_type`, języka, kategorii celebryty |
| R09 | **[INŻ. DANYCH / PIPELINE]** **Dane osobowe** (nazwiska osób publicznych; wizerunek). **Rozpoznawanie twarzy jest niezgodne z RODO w naszych warunkach, bo to dane biometryczne z art. 9 ust. 1 bez przesłanki z ust. 2 (04, zasada 4; [edpb2024clearview])**; Meta wstrzymała tę technologię w 2021 r. z powodu obaw społecznych i braku jasnych reguł, a obecnie stosuje ją z natychmiastowym usuwaniem danych twarzy [meta2024celebbait] | Naruszenie RODO/regulaminu, wyłączenie danych z użycia | średnie | wysoki | Bez automatycznego rozpoznawania twarzy; `celeb_id` tylko w pliku roboczym; raportowanie zagregowane po kategoriach; ocena prawna przez inżyniera danych (P07) | wynik oceny w macierzy legalności |
| R10 | **[INŻ. DANYCH]** **Regulamin i licencje**: warunki API/Content Library (zakaz eksportu, publikacji danych osobowych) | Niemożność użycia lub publikacji danych | średnie | wysoki | Macierz legalności przed jakąkolwiek pracą na danych (03, P07); wynik negatywny o dostępie jest pełnoprawny | wypełniona macierz |
| R11 | **[PIPELINE]** **Dryf definicji i konfiguracji**: zmiana promptu lub wersji modelu zmienia wynik [baumann2025] | Niepowtarzalność | średnie | średni | Zamrożenie codebooka i zbioru testowego; dziennik uruchomień; raport zakresu po konfiguracjach | flip rate między konfiguracjami (`prompt_robustness.py`) |
| R12 | **[PIPELINE]** **Rzadkie klasy**: deepfake scamy mogą stanowić niewielki odsetek ramki, więc za mało pozytywów w gold standardzie; paradoks kappa maskuje jakość kodowania [feinstein1990] | Szerokie CI mediany i udziałów; fałszywe odrzucenie zmiennej | wysokie | wysoki | Losowanie warstwowe z nadpróbkowaniem; α z prevalence i zgodnością pozytywną/negatywną; klasy z małą liczbą pozytywów jako eksploracyjne (05); tabela liczebności dla hipotezy (05, sekcja 3) | P09 |
| R13 | **[PIPELINE]** **Język**: instrument i literatura głównie dla angielskiego; część reklam może być w innych językach | Niższa jakość dla polskiego | średnie | średni | Analiza błędów wg języka; D8 | P10 |
| R14 | **[LEAD]** **Nadinterpretacja**: opis czasu życia i intensywności może zostać odebrany jako wniosek o intencjach reklamodawców (*burst-and-burn*) lub skuteczności; ocena kursu wymaga rozróżnienia opisu od przyczynowości | Nadinterpretacja | wysokie | średni | Język tezy („zgodne z”, nie „potwierdza”; decyzja leada, P26); sekcja ograniczeń w preprincie | — |
| R15 | **[PIPELINE]** **Koszt, limity i czas** przetwarzania | Niemożność przetworzenia całości | średnie | średni | Kodowanie próby zamiast całości (wariant E) i estymacja korygowana | P16 |
| R16 | **[INŻ. DANYCH / LEAD]** **Niewykonalność pomiaru czasu życia lub intensywności**: daty emisji lub skumulowane wyświetlenia mogą być niedostępne albo inaczej zdefiniowane, niż zakładamy (P06) | Brak zmiennej wynikowej | do ustalenia | wysoki | D6; wynik negatywny o pomiarze jest pełnoprawnym wynikiem (zasady kursu) | P06 |
| R17 | **[INŻ. DANYCH / LEAD]** **Cenzurowanie i obcięcie czasu życia**: reklamy wciąż aktywne (brak końca emisji) i reklamy rozpoczęte przed oknem źródła; retencja źródła obcina historię | Zaniżony lub zniekształcony czas życia | wysokie | wysoki | Jawna definicja czasu życia (P28); raportowanie udziału reklam bez końca; metody analizy przeżycia (analityk) | udział reklam bez daty końca (`audit_dataset.py`), rozkład `delivery_start` względem okna źródła |
| R18 | **[INŻ. DANYCH / LEAD]** **Wyniki dotyczą ramki, nie populacji reklam**: ramka powstała z zapytań (słowa kluczowe, reklamodawcy), więc mediana i udziały dotyczą tylko reklam, które te zapytania znalazły | Zawyżone lub zaniżone wartości względem populacji | wysokie | wysoki | Opis ramki (P29, D9); wyniki raportowane względem ramki | opis ramki w data statement |
| R19 | **[PIPELINE / LEAD]** **Deepfake nie jest mierzony bezpośrednio, a jest kryterium populacji**: annotator referencyjny i oceniany nie potrafią wiarygodnie stwierdzić, że materiał jest syntetyczny; `media_synthetic_suspected` to tylko podejrzenie. Błąd tej klasyfikacji wchodzi bezpośrednio do populacji badanej | Populacja „deepfake scam” może zawierać reklamy bez syntezy i pomijać reklamy z syntezą; wnioski o deepfake'ach mogą być nadinterpretacją | wysokie | wysoki | Nazwana przesłanka (`media_synthetic_cue`); α i odsetek `unsure` (05); wrażliwość na definicję populacji (tylko `yes`; `yes` ∪ `suspected`); wnioski o „reklamach z podejrzeniem deepfake'a” | α dla `media_synthetic_suspected` (P13); udział `unsure`; różnica wyników między definicjami populacji |
| R20 | **[LEAD / PIPELINE]** **Dane zagregowane: brak rozkładu w czasie.** Źródło daje sumę wyświetleń za okres, a nie wartości godzinowe czy dzienne; dzienna intensywność to średnia. Interpretacja *burst-and-burn* dotyczy przebiegu (budżet na początku), którego nie obserwujemy | Hipoteza o taktyce nie może być potwierdzona danymi, tylko uznana za zgodną lub niezgodną z nimi | wysokie | wysoki | Formułować wniosek jako „zgodne z” (decyzja leada, P26); nie używać słowa „potwierdza”; jeśli źródło daje rozbicie po dniach, wykorzystać je (P06) | dostępność wartości dziennych (P06) |
| R21 | **[PIPELINE / ANALITYK]** **Zależność mechaniczna L i I**: I = suma / L, więc dla L = 1 intensywność równa jest całej sumie; krótkie reklamy mają większą i bardziej zmienną I; konwencja liczenia dni (włącznie lub nie) zmienia wniosek przy progu 2 dni | Przeszacowanie lub niedoszacowanie udziału I ≥ T_I; wrażliwość składowej o czasie życia na konwencję | wysokie | wysoki | Konwencja jawna (01); raportowanie także skumulowanych wyświetleń; analiza wrażliwości na konwencję (L bez dnia pierwszego) i na minimalną długość emisji | rozkład L; udział reklam z L = 1; mediana `reach_total` |
| R22 | **[INŻ. DANYCH / PIPELINE]** **Definicja i dokładność pola wyświetleń**: „liczba osób, które zobaczyły reklamę” może być zasięgiem unikatowym, nie wyświetleniami; wartość może być przedziałem lub zaokrągleniem; próg 25 tys. może wypaść wewnątrz przedziału | Niepewna klasyfikacja reklam względem T_I; nazwa „impresje” może być nieścisła | średnie | wysoki | Ustalić znaczenie pola (P06); przy przedziałach policzyć udział dla dolnej i górnej granicy; nazwać wielkość tak, jak definiuje ją źródło | udział przedziałów obejmujących T_I; wartości zero lub brakujące |

## Wnioski do karty M1

1. Najpoważniejsze zagrożenia dla pytania o medianę czasu życia i dzienną intensywność to R19 (deepfake tylko podejrzewany, a jest kryterium populacji), R20 (dane zagregowane), R21 (zależność L i I), R02 i R03 (egzekwowanie platformy a czas życia), R17 (cenzurowanie) i R18 (ramka). Są strukturalne (wynikają z konstrukcji badania i danych), nie techniczne.
2. Część z nich nie jest usuwalna; jest jawnie opisywana jako ograniczenie, a sformułowanie wniosków (decyzja leada, P26) ma to odzwierciedlać, zwłaszcza w kwestii *burst-and-burn*.
3. Ryzyka R10, R16, R17 i R22 mogą zawęzić albo uniemożliwić badanie; plan zakłada rozstrzygnięcie ich przed zbieraniem danych (D1, D6, macierz legalności).

---

# 07. Bibliografia z adnotacjami i statusem weryfikacji

Oceniane jest poprawne cytowanie, więc każda pozycja ma status. **Zweryfikowane** oznacza: tytuł, autorzy i dane bibliograficzne potwierdzone w źródle w tej sesji (strona wydawcy, repozytorium preprintów lub spis literatury innej pracy), ale nie oznacza, że przeczytałem całą pracę. **Do sprawdzenia** oznacza: informacja z pamięci albo z drugorzędnego źródła; otwórz oryginał przed wpisaniem do preprintu. **Przeczytaj w całości** dotyczy prac, na których opiera się decyzja metodologiczna: znam z abstraktów i opisów, a nie z pełnego tekstu.

Klucze (`@klucz`) są używane w pozostałych dokumentach i w komentarzach narzędzi.

## A. Zgodność annotatorów i walidacja

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `krippendorff2004` | Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage. | Progi α: ≥ 0,800 dane wiarygodne, 0,667–0,800 tylko wnioski wstępne, < 0,667 odrzucić; autor zaleca dobierać próg do kosztu błędnych wniosków | Do sprawdzenia: progi potwierdzone w kilku źródłach wtórnych, nie w samej książce; sprawdź wydanie i numer strony |
| `feinstein1990` | Feinstein, A. R., Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. *J Clin Epidemiol* 43(6), 543–549. | Niska kappa przy wysokiej zgodności i niezrównoważonych brzegach | Zweryfikowane (dane z listy literatury w PMC) |
| `cicchetti1990` | Cicchetti, D. V., Feinstein, A. R. (1990). High agreement but low kappa: II. Resolving the paradoxes. *J Clin Epidemiol* 43(6), 551–558. | Zgodność pozytywna i negatywna jako uzupełnienie kappa | Zweryfikowane (j.w.) |
| `byrt1993` | Byrt, T., Bishop, J., Carlin, J. B. (1993). Bias, prevalence and kappa. *J Clin Epidemiol* 46(5), 423–429. | Indeksy prevalence i bias; zalecenie raportowania ich razem z kappa | Tytuł i autorzy zweryfikowani; czasopismo, tom i strony do sprawdzenia |
| `chen2009` | Chen, G. i in. (2009). Measuring agreement of administrative data with chart data using prevalence unadjusted and adjusted kappa. *BMC Med Res Methodol* 9, 5. doi:10.1186/1471-2288-9-5 | Raportuj kappa, prevalence, zgodność pozytywną i negatywną; PABAK nie mierzy tego samego co kappa przy niskiej prevalence | Tytuł, czasopismo i DOI zweryfikowane; lista autorów do sprawdzenia |
| `donner1987` | Donner, A., Eliasziw, M. (1987). Sample size requirements for reliability studies. *Stat Med* 6, 441–448. | Liczebność badania zgodności przez oczekiwaną szerokość przedziału | Zweryfikowane (spis literatury pakietu kappaSize) |
| `rotondi2012` | Rotondi, M. A., Donner, A. A confidence interval approach to sample size estimation for interobserver agreement studies with multiple raters and outcomes. *J Clin Epidemiol* | j.w. dla wielu annotatorów i kategorii | Tytuł zweryfikowany (pakiet kappaSize); rok, tom i strony do sprawdzenia |

## B. LLM jako annotator w naukach społecznych

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `gilardi2023` | Gilardi, F., Alizadeh, M., Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *PNAS* 120(30), e2305016120. doi:10.1073/pnas.2305016120 | Ten sam codebook dla ludzi i modelu; porównanie z referencją ludzką; **dotyczy tekstu** (tweety, artykuły), n = 6183 łącznie | Zweryfikowane; autorzy sami ostrzegają, że to za wcześnie na zastępowanie annotatorów |
| `ziems2024` | Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., Yang, D. (2024). Can large language models transform computational social science? *Computational Linguistics* 50(1), 237–291. | Realistyczne oczekiwania: LLM nie zastępują w pełni annotacji ludzkiej; κ w zakresie 0,40–0,65 w 8 z 17 zadań (wartość ze streszczenia wtórnego); **tylko zadania tekstowe, angielski** | Zweryfikowane; zakres κ do sprawdzenia w pełnym tekście |
| `halterman2025` | Halterman, A., Keith, K. A. Codebook LLMs: Evaluating LLMs as measurement tools for political science concepts. arXiv:2407.10747 (wersja czasopiśmiennicza: Cambridge University Press) | Ramy pomiaru: przygotuj codebook dla ludzi i modelu, przetestuj podstawowe zdolności, oceń dokładność zero-shot; pozostałe etapy ramy do przeczytania | Preprint zweryfikowany; czasopismo, rok i strony do sprawdzenia; **przeczytaj w całości** |
| `baumann2025` | Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., Hovy, D. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv:2509.08825 | Konfiguracja (prompt, model) zmienia wnioski; ok. 31% hipotez z błędnym wnioskiem dla najlepszych modeli; adnotacje ludzkie zmniejszają ryzyko fałszywie pozytywnych wyników | Preprint zweryfikowany; liczba 31% z abstraktu wersji 2; **przeczytaj w całości** |
| `egami2025dsl` | Egami, N., Hinck, M., Stewart, B. M., Wei, H. Using large language model annotations for the social sciences: A general framework of using predicted variables in downstream analyses. (nagroda Gosnell Prize 2025) | Predykcje modelu analizowane jak obserwacje bez błędu dają obciążenie i nieprawidłowe CI nawet przy dokładności > 90%; metoda DSL łączy predykcje z mniejszą próbą etykiet eksperckich losowaną ze znanymi prawdopodobieństwami | Istnienie, autorzy i teza potwierdzone (abstrakty seminariów, strona nagrody); **wersja wydawnicza, tytuł wersji konferencyjnej i rok do sprawdzenia**; przeczytaj w całości, bo od niej zależy plan analizy |
| `calderon2025` | Calderon, N., Reichart, R., Dror, R. (2025). The alternative annotator test for LLM-as-a-judge: How to statistically justify replacing human annotators with LLMs. *Proc. ACL 2025* (long), 2025.acl-long.782. doi:10.18653/v1/2025.acl-long.782 | Procedura statystyczna uzasadniająca zastąpienie annotatora przez LLM na niewielkim podzbiorze; obejmuje też zadania wizualno-językowe | Zweryfikowane; szczegóły testu (alt-test) do przeczytania |

## C. Reklamy, scam i biblioteki reklam

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `meta2024celebbait` | Bickert, M. (21.10.2024). Wpis Meta o teście rozpoznawania twarzy przeciw „celeb-bait". Meta Newsroom. | Definicja „celeb-bait"; zastrzeżenie, że celebryci występują też w legalnych reklamach; porównywanie twarzy z reklam ze zdjęciami profilowymi | Treść potwierdzona w kilku omówieniach (TechCrunch i inne); **cytuj oryginał**, nie omówienie; adres oryginału do uzupełnienia |
| `gendigital2026` | Gen Digital, Gen Threat Labs. *The Scam Ad Machine*. Raport branżowy (witryna Gen Digital). | Pipeline pomiarowy na Meta Ad Transparency API; reklamy z angielskim tekstem w UE i Wielkiej Brytanii; 10 największych reklamodawców scamowych = 56,1% reklam scamowych | Zweryfikowane jako raport branżowy (nierecenzowany); data publikacji do sprawdzenia na stronie |
| `edpb2024clearview` | EDPB (2024). *Dutch Supervisory Authority imposes a fine on Clearview because of illegal data collection for facial recognition*. Komunikat, edpb.europa.eu (Autoriteit Persoonsgegevens: kara 30,5 mln EUR; naruszenie m.in. art. 9 ust. 1). | Przykład egzekwowania zakazu przetwarzania danych biometrycznych | Treść komunikatu odczytana; data publikacji i adres do uzupełnienia; **nie jest to opinia prawna** |
| `rodo2016motyw51` | Rozporządzenie (UE) 2016/679 (RODO), art. 9 i motyw 51. | Fotografia jest daną biometryczną tylko przy przetwarzaniu specjalnym środkiem technicznym umożliwiającym jednoznaczną identyfikację; dane biometryczne to szczególna kategoria | Motyw 51 odczytany przez omówienie na stronie trzeciej; **cytuj tekst w EUR-Lex** |
| `ttp2025` | Tech Transparency Project (2025). Raport o reklamach scamowych z deepfake'ami polityków na platformach Meta. | 63 reklamodawców scamowych, 150 tys. reklam politycznych; scam operacjonalizowany przez usunięcie reklam przez platformę (przykład ryzyka R03: czas życia jako czas do usunięcia); **reklamy polityczne w USA** | Widziałem tylko omówienie (Biometric Update); **znajdź raport TTP**, sprawdź tytuł i datę |
| `edelson2020` | Edelson, L., Lauinger, T., McCoy, D. (2020). A security analysis of the Facebook Ad Library. *IEEE Symposium on Security and Privacy*, 661–678. | Biblioteka reklam ma luki (np. częściowa awaria, reklamy bez ujawnienia); **dotyczy amerykańskich reklam politycznych** | Zweryfikowane (dane bibliograficzne z dblp i streszczenie) |
| `lepochat2022` | Le Pochat, V., Edelson, L., Van Goethem, T., Joosen, W., McCoy, D., Lauinger, T. (2022). An audit of Facebook's political ad policy enforcement. *USENIX Security Symposium*, 607–624. | Egzekwowanie zasad platformy jest niedoskonałe i może być audytowane; **reklamy polityczne** | Zweryfikowane (j.w.) |
| `radboud2025` | Kablan, L. (2025). *Misleading ad detection: Cryptocurrency scam ad classification on Facebook's ad library*. Praca licencjacka, Radboud University. | Przykład pipeline'u z Meta Ad Library i LLM; precision niskie przy rzadkich pozytywach; deduplikacja zmniejszyła zbiór z ok. 100 tys. do 25 671 reklam, z czego 2454 unikatowe | Zweryfikowane jako praca nierecenzowana; użyj tylko jako przykład poglądowy |
| `zeng2021` | Zeng, E., Wei, M., Gregersen, T., Kohno, T., Roesner, F. (2021). Polls, clickbait, and commemorative $2 bills: Problematic political advertising on news and media websites around the 2020 US elections. *ACM IMC*, 507–525. | Badanie reklam problematycznych metodą pomiarową | Dane bibliograficzne potwierdzone w spisach literatury innych prac; **treści (codebook) nie czytałem** |
| `chasm2026` | Chasm: Unveiling covert advertisements on Chinese social media. arXiv:2604.20511 | Zbiór do oceny multimodalnych LLM w wykrywaniu ukrytych reklam; metryki P, R, F1, AUC; zero-shot, uczenie w kontekście, fine-tuning | Preprint zweryfikowany; autorów i rok do uzupełnienia; **czytaj w całości, zanim użyjesz jako wzorca** |
| `adsprofiles2025` | When ads become profiles: Large-scale audit of algorithmic biases and LLM profiling risks. arXiv:2509.18874 | Multimodalny LLM stosowany do reklam z Facebooka (zadanie inne niż nasze) | Preprint zweryfikowany; autorów do uzupełnienia |
| `clark2026` | Clark, S., Lewandowsky, S. (2026). The continued influence of AI-generated deepfake videos despite transparency warnings. *Communications Psychology* 4. doi:10.1038/s44271-025-00381-9 | Perswazyjność deepfake'a nie znika po ostrzeżeniu (trzy eksperymenty, N = 175, 275, 223); autorzy zastrzegają, że wyjaśnienia związane z ramowaniem zadania nie są wykluczone; **dotyczy wideo i oceny winy, nie reklam**; nie jest używane w dokumentach pipelinu, do decyzji leada o przeglądzie literatury (P31) | Zweryfikowane |
| `tiktokcca` | TikTok for Developers. *Commercial Content API* (strona produktu), developers.tiktok.com/products/commercial-content-api. | Pola: data publikacji i „last seen date”, liczba osób, które zobaczyły reklamę, targetowanie dla reklam płatnych, metadane reklamy i reklamodawcy; dane z UE; dostęp do roku od ostatniego wyświetlenia; API dla publiczności i badaczy po wniosku | Strona odczytana w tej sesji; **nie rozstrzyga znaczenia pól ani warunków zapisu danych (Developer Terms of Service do przeczytania, P06, P07)**; dodaj datę dostępu |
| `tiktokcclnews2023` | TikTok Newsroom (2023-07-20). *TikTok's Research API and Commercial Content Library*, newsroom.tiktok.com. | Biblioteka zawiera kreację reklamy, daty emisji, targetowanie i liczbę osób, którym wyświetlono reklamę; dostępne dane z Europy | Strona odczytana w tej sesji (omówienie pól); sprawdź aktualność, bo komunikat jest z 2023 r. |

## D. Wnioskowanie i dokumentacja danych

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `cameron2015` | Cameron, A. C., Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. *Journal of Human Resources* 50(2), 317–372. doi:10.3368/jhr.50.2.317 | Wnioskowanie przy danych klastrowych; przy niewielkiej liczbie klastrów standardowe błędy odporne na klastrowanie zaniżają niepewność i trzeba stosować korekty | Zweryfikowane |
| `gebru2021` | Gebru, T. i in. (2021). Datasheets for datasets. *Communications of the ACM* 64(12), 86–92. | Dokumentacja zbioru danych | Zweryfikowane |
| `bender2018` | Bender, E. M., Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *TACL* 6. | Data statement dla zbiorów językowych | Zweryfikowane |

## E. Źródła do uzupełnienia przez inżyniera danych

Oficjalna dokumentacja TikToka (źródło główne): odczytałem strony produktu i komunikat z 2023 r. (pozycje `tiktokcca`, `tiktokcclnews2023`), ale **nie** Developer Terms of Service ani pełnej specyfikacji pól API; znaczenia pól i warunków zapisu nie rozstrzygam. Do uzupełnienia: {{P07: adresy i wersje oficjalnej dokumentacji TikTok Commercial Content API i Library, Developer Terms of Service, ewentualnych źródeł dodatkowych | zależy od: inżynier danych | domyślnie: brak}}.

Jeśli zespół włączy źródło dodatkowe, np. Meta Content Library: znana jest procedura wnioskowa (wniosek przez ICPSR, umowa o korzystaniu z danych między ICPSR a instytucją, zakaz eksportu i wgrywania danych do platformy badawczej, zakaz publikowania danych osobowych) według dokumentacji deweloperskiej Mety i komunikatu ICPSR; zakres pokrycia reklam nie został przeze mnie potwierdzony.

## Czego nie znalazłem

Nie znalazłem recenzowanej pracy, która koduje reklamy typu celeb-bait multimodalnym LLM z walidacją na gold standardzie, ani pracy szacującej skalę i czas życia reklam scamowych z wizerunkiem osób publicznych. To wynik wyszukiwania w tej sesji, a nie dowód, że takich prac nie ma; sprawdź Google Scholar i bazy ACM/IEEE przed napisaniem w preprincie, że istnieje luka w literaturze.

---

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

---

# 10. Playbook: co robić po otrzymaniu danych

Kroki w kolejności. Każdy krok kończy się wpisem w rejestrze placeholderów (00) i, jeśli dotyczy, uruchomieniem zapisanym w dzienniku (`tools/run_log.py`). Punkty D1–D9 są zdefiniowane w 00. **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” **Pytanie badawcze (01):** mediana czasu życia reklam deepfake scam i ich dzienna intensywność wyświetleń (hipoteza: mediana ≤ 2 dni, ponad 50% reklam ≥ 25 tys. wyświetleń na dzień; progi są parametrami).

## Krok 0. Bramka legalności (przed otwarciem danych)

- Jest macierz legalności i data statement od inżyniera danych? ({{P07: macierz legalności | zależy od: inżynier danych | domyślnie: brak}}, {{P08: data statement | zależy od: P07 | domyślnie: brak}})
- Jeśli nie: **stop**, pracujemy tylko na narzędziach i danych syntetycznych. Wynik negatywny o dostępie do danych jest pełnoprawnym wynikiem projektu.

## Krok 1. Audyt tabeli

`python tools/audit_dataset.py dane.csv` → wpisz do P01, P02, P03, P05, P06, P10, P11. Zapisz hash pliku wejściowego w dzienniku.

Reakcje:
- brakuje kolumn wymaganych → zwróć do inżyniera danych z listą (03, sekcja 2);
- nie ma dat początku i końca emisji albo skumulowanych wyświetleń (`reach_total`) → D6 = NIE (czas życia lub dzienna intensywność niemierzalne);
- wyświetlenia podane jako przedziały → zapisz granice (`reach_min`, `reach_max`) i sprawdź, w ilu przypadkach próg T_I wypada w przedziale (R22);
- duży udział reklam bez daty końca → zgłoś do leada i analityka (cenzurowanie, P28, R17);
- adres docelowy niedostępny → tylko adnotacja w opisie zbioru (pole opisowe, P05);
- kreacje (wideo) niedostępne → D1 = NIE: populacji „deepfake scam” nie da się zidentyfikować, zgłoś do leada (P30).

## Krok 2. Eksploracja do karty M1

1. Rozkład w czasie, po platformach, krajach i językach (P17, P10; statystyki opisowe dostarcza inżynier danych, pipeline może użyć `audit_dataset.py`).
2. Losowo wybrane 50–100 rekordów przejrzyj ręcznie; zapisz, co zaskoczyło (P17). To jest materiał do poprawy codebooka, nie do dowodzenia.
3. Szacunek prevalence scamu i podejrzenia deepfake'a na tej próbie (P09). Przedział ufności Wilsona: `python tools/sample_size.py wilson --k ... --n ...`. Przy małej próbie przedział jest szeroki; zapisz go.
4. Koncentracja reklamodawców (P11), przybliżone ICC z danych (P12).
5. Wstępne rozkłady L i I na całej ramce (opis, bez korekty): `python tools/outcomes.py dane.csv` (P17); sprawdź udział L = 1 i reklam aktywnych (R17, R21).
6. Decyzja D2: czy jest dość przypadków do planu z 05 (tabela liczebności dla hipotezy).

## Krok 3. Pilotaż codebooka

1. Wylosuj 30–50 reklam (`tools/sampling.py`, bez limitu warstw; seed w dzienniku).
2. Dwóch annotatorów koduje niezależnie w `templates/annotation_sheet_template.csv`; walidacja: `python tools/checks.py sheet arkusz.csv`.
3. Zgodność: `python tools/agreement.py arkusz.csv --vars celeb_mention scam_type ...` → P13.
4. Spotkanie: omów niezgodności, popraw definicje, wpis w `templates/codebook_changelog.md`, wersja 0.2.
5. Pilotaż 2 na nowej próbie. D3: dla każdej zmiennej wg poniższej tabeli.

## Krok 4. Decyzje po pilotażu

| Wynik | Działanie | Podstawa |
|---|---|---|
| α ≥ 0,80 | zmienna wiarygodna, użyj w analizie | [krippendorff2004] |
| 0,667 ≤ α < 0,80 | tylko wnioski wstępne; opisz jako takie | [krippendorff2004] |
| α < 0,667, kategoria rzadka (prevalence < ok. 10–20% w próbie) | sprawdź zgodność pozytywną/negatywną i prevalence index; niskie α może wynikać z niezrównoważenia, a nie z jakości kodowania; nie usuwaj automatycznie | [feinstein1990; cicchetti1990; chen2009]; symulacja w 05 |
| α < 0,667, kategorie zrównoważone, po drugiej rundzie | usuń zmienną z pomiaru; nie nazywaj jej mierzalną (wynik negatywny jest pełnoprawny) | zasady kursu; [krippendorff2004] |

Progi dotyczące „rzadkiej kategorii" są moją heurystyką, nie progiem z literatury.

## Krok 5. Zamrożenie i gold standard

1. Zamroź codebook (wersja i hash).
2. Losowanie dwufazowe: `python tools/sampling.py ...` (limit P24, liczebność z 05); zapis prawdopodobieństw włączenia.
3. Annotacja na ślepo, adjudykacja, zamrożenie gold standardu (hash).
4. Podział: zbiór rozwijania promptu i zbiór testowy rozłączne.

## Krok 6. Instrument

1. Baseline słownikowy (04, wariant A) na całości i na gold standardzie.
2. Prompt na zbiorze rozwijania; wersjonowanie; uruchomienia w dzienniku.
3. Ocena na zbiorze testowym (raz): `python tools/evaluation.py ...` → P14.
4. Wrażliwość: `python tools/prompt_robustness.py ...`.
5. D5: zgodność annotatora ocenianego z gold standardem względem zgodności annotatorów referencyjnych między sobą.

## Krok 7. Wyniki na populacji badanej

1. Populacja = gold standard sklasyfikowany jako deepfake scam (wagi 1/p): `python tools/outcomes.py gold.csv --class-col in_population --weight-col weight --cluster advertiser_id --thr-days 2 --thr-intensity 25000`. Progi to parametry od leada i mogą się zmienić.
2. Ten sam skrypt na reklamach wskazanych przez annotatora ocenianego (estymata naiwna) i porównanie z wynikiem z gold standardu (05, sekcja 5).
3. Wrażliwość: definicja populacji (tylko `yes`; `yes` ∪ `suspected`; `unsure` włączone lub wyłączone), konwencja liczenia dni, granice przedziałów wyświetleń.
4. Pasmo mediany L przy reklamach aktywnych: dolne (obserwowane do dnia pobrania) i górne (nieskończone) ograniczenie. Jeśli pasmo obejmuje próg T_L, składowa hipotezy o czasie życia nie jest rozstrzygnięta.
5. Wpis do rejestru (P32 czeka na regułę decyzyjną od leada i analityka).

## Krok 8. Przekazanie analitykowi

Przekaż: tabelę z predykcjami i etykietami, wagami włączenia, klastrami; opis zmiennych; wyniki walidacji z CI; medianę L i udział I ≥ T_I naiwne i z gold standardu; wyniki analizy błędów po warstwach, po czasie emisji i po intensywności (05, sekcja 5); zakres wrażliwości; ograniczenia. Analityk wdraża model przeżycia dla reklam aktywnych (Kaplan–Meier) i pełną korektę błędu pomiaru dla regresji [egami2025dsl] (w repozytorium są tylko: wersja uproszczona dla częstości i `tools/outcomes.py` z pasmem mediany; 05, sekcja 6).

## Lista kontrolna przed oddaniem raportu

- [ ] każdy wynik z liczbą ma odtwarzalne uruchomienie w dzienniku
- [ ] precision zawsze razem z prevalence
- [ ] CI przez bootstrap po klastrach
- [ ] zakres po konfiguracjach, nie jedna liczba
- [ ] ograniczenia z 06 przeniesione do preprintu
- [ ] użycie AI opisane (09)
