# 01. Plan pomiaru zjawiska (wkład inżyniera pipelinu do karty M1)

Karta M1 jest oceniana za: konkretność pytania, jakość eksploracji i spójność planu badawczego, z jawnymi ograniczeniami danych, źródłami błędu i uzasadnieniem wykonalności. Ten dokument jest wkładem inżyniera pipelinu: **jak klasyfikujemy reklamy, jak sprawdzimy, że annotator oceniany działa, jak analizujemy jego błędy i co może nas zatrzymać**. Oznaczenia właścicieli jak w 00: **[LEAD]**, **[INŻ. DANYCH]**, **[PIPELINE]**, **[ANALITYK]**. Miejsca innych ról są tylko placeholderami.

## 1. Temat i pytanie badawcze

**Temat (zadany):** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

> **[LEAD – DO WYPEŁNIENIA]** Pytanie badawcze i hipoteza w wersji ostatecznej: {{P26: pytanie badawcze i hipoteza | zależy od: lead | domyślnie: brak}}
>
> **[LEAD – DO WYPEŁNIENIA]** Definicja skali: {{P27: skala (jednostka liczenia, okno czasu, ewentualnie zasięg) | zależy od: lead, P06 | domyślnie: brak}}
>
> **[LEAD / INŻ. DANYCH – DO WYPEŁNIENIA]** Definicja czasu życia: {{P28: czas życia reklamy (początek, koniec, reklamy aktywne, reklamy sprzed okna źródła) | zależy od: lead, P06, P03 | domyślnie: brak}}
>
> **[LEAD – DO WYPEŁNIENIA]** Konstrukt wizerunku: {{P30: wzmianka, widoczna twarz czy oba | zależy od: lead, D1 | domyślnie: brak}}

**Czego pipeline potrzebuje od leada (pytania, nie odpowiedzi):** (a) jednostka, w której liczymy skalę; (b) jak traktować reklamy bez daty końca i reklamy rozpoczęte przed oknem źródła; (c) czy „wizerunek” oznacza wzmiankę w tekście, widoczną twarz, czy oba (zależy od dostępu do kreacji, D1); (d) czy pytanie jest wyłącznie opisowe, czy zawiera porównanie z reklamami scamowymi bez osoby publicznej. Od odpowiedzi zależą klasy, które walidujemy w 05.

## 2. Co mierzy pipeline, a co pochodzi skądinąd

| Wielkość | Skąd | Kto odpowiada |
|---|---|---|
| Przynależność reklamy do populacji badanej: (a) wzmianka lub wizerunek osoby publicznej, (b) scam | annotator oceniany, zwalidowany na gold standardzie | [PIPELINE] |
| Typ scamu (warstwa, do podziałów) | j.w. | [PIPELINE] |
| Dowód zewnętrzny scamu (domena docelowa, Lista Ostrzeżeń CERT) | dane i lista | [INŻ. DANYCH] dostarcza, [PIPELINE] zestawia |
| Skala (liczby reklam, kreacji, reklamodawców; ewentualnie zasięg) | liczone z tabeli po klasyfikacji | [PIPELINE] dostarcza estymatę z korektą błędu klasyfikacji; definicja: [LEAD] |
| Czas życia (początek i koniec emisji) | metadane źródła | [INŻ. DANYCH] dostarcza; obróbka (cenzurowanie, model czasu): [ANALITYK] |

Annotator oceniany nie mierzy ani skali, ani czasu życia. Mierzy **przynależność do klasy**, a zadaniem pipelinu jest pokazać, jak błąd tej klasyfikacji wpływa na oba wyniki (sekcja 7).

## 3. Jednostka analizy i ramka

- **Jednostka:** unikatowa kreacja (`creative_id`), z reklamodawcą jako klastrem. Reklamy nie są niezależnymi obserwacjami: w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [@gendigital2026]; dla naszych danych koncentrację policzy inżynier danych (P11).
- **Ramka (zbiór kandydujący):** > **[INŻ. DANYCH / LEAD – DO WYPEŁNIENIA]** {{P29: jak zbudowano zbiór reklam kandydujących | zależy od: źródło, P01 | domyślnie: brak}}. Źródło, kraje, języki, okno dat: {{P01: źródło, kraje, języki, okno dat | zależy od: macierz legalności (P07) | domyślnie: brak}}. Liczebność: {{P02: liczba reklam, kreacji, reklamodawców | zależy od: pobranie danych | domyślnie: nieznana}}.
- **Wymaganie pipelinu wobec ramki:** ramka nie może być zbudowana na wyniku annotatora ocenianego ani na kryterium „scam”; w przeciwnym razie skala dotyczy tylko ramki i nie uogólnia się na populację reklam (D9).
- Ramka jest **zbiorem cenzurowanym** (R01): wnioski dotyczą reklam widocznych w źródle w oknie jego retencji.

## 4. Definicje i dowód na scam

**Wizerunek znanej osoby (kryterium populacji).** Dwa poziomy (02):
- **L1 (wykonalny):** *wzmianka* o osobie publicznej w tekście, nagłówku, podpisie linku lub domenie reklamy (`celeb_mention`).
- **L2 (warunkowy, po D1):** *widoczna twarz* osoby, którą annotator referencyjny uznaje za osobę publiczną, bez ustalania tożsamości po twarzy (zob. 04, zasada 4), oraz podejrzenie syntetyczności kreacji. Bez legalnego dostępu do kreacji L2 jest wyłączony, a konstrukt zawęża się do wzmianki (ograniczenie opisane w R05; decyzja o temacie: P30). Dostępność: {{P04: dostępność kreacji | zależy od: regulamin źródła | domyślnie: niedostępne}}.

**Scam.** Dwie warstwy, rozdzielone celowo:
1. *Typ oferty* z treści reklamy (`scam_type`, kodowany przez annotatorów, łącznie z wartościami `not_scam` i `unclear`).
2. *Dowód zewnętrzny*: łańcuch reklama, domena docelowa, Lista Ostrzeżeń CERT Polska [@certlist]. Lista zawiera domeny wprowadzające w błąd i wyłudzające dane; według miesięcznych podsumowań CERT domeny są blokowane na 6 miesięcy, a jeśli nadal zawierają niebezpieczne treści, wpisuje się je ponownie. CSIRT KNF opisuje zgłaszanie do wpisu na tę listę domen z reklam fałszywych inwestycji publikowanych na Facebooku [@csirtknf2024]. Warunki: {{P18: warunki użycia Listy Ostrzeżeń | zależy od: inżynier danych | domyślnie: brak}}, {{P05: dostępność adresu docelowego | zależy od: pola źródła | domyślnie: nieznana}}, pokrycie: {{P19: odsetek domen z danych możliwych do zestawienia z listą | zależy od: P05, P18 | domyślnie: nieznane}}.
3. *Ocena annotatora referencyjnego* (`scam_judgement`) jest zmienną pomocniczą, nie dowodem.

**Dlaczego nie wystarczy usunięcie reklamy przez platformę jako definicja scamu.** Jeśli „scam” = „usunięta”, to **czas życia jest z definicji czasem do usunięcia**, więc pytanie o czas życia staje się tautologią, a skala dotyczy tylko reklam wykrytych przez platformę (R02, R03). Dodatkowo platforma ma dla reklam z osobami publicznymi osobny mechanizm wykrywania (porównywanie twarzy z reklam ze zdjęciami profilowymi) [@meta2024celebbait]. Dlatego scam etykietujemy niezależnie od decyzji platformy, a decyzję platformy (`platform_removal`) traktujemy jako zmienną do analizy wrażliwości. Jeśli nie ma adresu docelowego, łańcuch dowodu odpada (D4) i trzeba to zapisać jako jawne zastrzeżenie.

## 5. Zmienne kodowane przez annotatorów

| Zmienna | Rola w pytaniu o skalę i czas życia | Poziom |
|---|---|---|
| `celeb_mention` | kryterium populacji (wzmianka o osobie publicznej) | L1 |
| `scam_type`, `scam_judgement` | kryterium populacji (scam) i warstwy podziału skali | L1 |
| `celeb_category` | warstwa podziału (opis populacji) | L1 |
| `celeb_face_visible`, `media_type`, `media_synthetic_suspected` | kryterium populacji dla wizerunku (L2); dostępne tylko po D1 | L2 |
| `celeb_id` | pole robocze (dane osobowe, nie raportujemy) | L1 |
| `celeb_claim`, `fake_news_format`, `urgency_cue`, `guaranteed_return_claim`, `authority_cue`, `cta_type` | zmienne dodatkowe; poza rdzeniem pytania (opcjonalne, eksploracyjne) | L1 |

Skala i czas życia pochodzą z metadanych; **annotatorzy ich nie widzą** (kodowanie na ślepo).

## 6. Plan pomiaru i walidacji w skrócie

Szczegóły: 02 (codebook), 04 (annotator oceniany), 05 (próba i walidacja).

1. Pilotaż annotacji (30–50 reklam, dwie rundy), poprawa codebooka, zamrożenie.
2. Gold standard: losowanie warstwowe z limitem na reklamodawcę i zapisem prawdopodobieństw włączenia; annotatorzy referencyjni ({{P21: skład | zależy od: lead | domyślnie: nieznany}}); Krippendorff α jako miara główna z progami 0,80 i 0,667 [@krippendorff2004].
3. Annotator oceniany jest oceniany względem gold standardu; precision zawsze z prevalence; CI przez bootstrap po klastrach [@cameron2015].
4. Wrażliwość na parafrazy promptu i wersję modelu raportowana jako zakres [@baumann2025].
5. Skalę (liczbę reklam w klasie) szacujemy z korektą błędu klasyfikacji, bo liczba reklam oznaczonych przez annotatora ocenianego bez korekty daje obciążenie [@egami2025dsl]. Estymator różnicowy dla częstości jest w repozytorium; pełne metody do analizy czasu życia (np. model przeżycia z korektą błędu klasy) wdraża {{P12: ICC i deff; metoda dla czasu życia | zależy od: [ANALITYK] | domyślnie: nie wdrożono}}.

## 7. Analiza błędów (wkład pipelinu)

1. **Macierz pomyłek per klasa** z precision, recall, F1 i prevalence (05, sekcja 5).
2. **Błąd w podziale na warstwy:** język, `scam_type`, kategoria osoby, typ kreacji, reklamodawca (klaster) oraz **przedział czasu emisji** (reklamy krótkotrwałe i długotrwałe).
3. **Wpływ na skalę:** porównanie liczby reklam w klasie według annotatora ocenianego (estymata naiwna) z estymatą z korektą na gold standardzie, z przedziałem po klastrach.
4. **Wpływ na czas życia:** sprawdzenie, czy błąd klasyfikacji zależy od czasu emisji lub od reklamodawcy. Jeśli tak, korekta globalna nie wystarcza (R08), a wnioski o czasie życia trzeba opatrzyć zastrzeżeniem.
5. **Wrażliwość:** zakres wyników po konfiguracjach (parafrazy, wersje).

## 8. Wykonalność

| Pytanie | Co wiemy | Kto rozstrzyga | Co rozstrzygną dane |
|---|---|---|---|
| Czy jest legalne źródło reklam komercyjnych? | Oficjalne API biblioteki reklam i Meta Content Library istnieją; dostęp i zakres są opisane głównie w dokumentacji firm trzecich i w komunikatach (ICPSR, deweloperska Meta); **nie potwierdzone w oficjalnej dokumentacji dla reklam komercyjnych** | [INŻ. DANYCH] | P04, P06, P07, P20 |
| Czy dostępne są daty początku i końca emisji? | Nie potwierdzone; zależy od pól udostępnianych legalnie przez źródło; **do ustalenia w oficjalnej dokumentacji** | [INŻ. DANYCH] | D6, P06, P28 |
| Czy dostępne są kreacje? | Pobieranie mediów ze stron reklam jest według przewodników poza zakresem API i problemem regulaminowym; **nie używamy** | [INŻ. DANYCH] | D1 |
| Czy jest dość przypadków do oszacowania skali? | Nieznane; zależy od prevalence wzmianki i scamu | [PIPELINE] | D2, P09, P02 |
| Czy annotator oceniany zadziała? | Literatura dla tekstu, angielskiego; **brak równorzędnej walidacji dla reklam z obrazem po polsku** [@gilardi2023; @ziems2024] | [PIPELINE] | D5, P14 |

**Wynik negatywny jest planowany, nie tylko dopuszczany.** Jeśli D6 = NIE, rezultatem projektu jest uzasadniony wniosek, że pomiar czasu życia z danych publicznych nie jest możliwy, wraz z opisem, jakie dane byłyby potrzebne. Zasady kursu oceniają taki wynik na równych prawach.

## 9. Wyniki wstępnej eksploracji (uzupełnić po otrzymaniu danych)

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** statystyki opisowe zbioru:
> - Zakres i rozkład w czasie, po platformach: {{P17: rozkład reklam w czasie i po platformach | zależy od: dane | domyślnie: brak}}
> - Języki: {{P10: rozkład języków | zależy od: dane | domyślnie: brak}}
> - Koncentracja reklamodawców: {{P11: liczba klastrów i udział 10 największych | zależy od: dane | domyślnie: brak}}

> **[PIPELINE – DO WYPEŁNIENIA po pilotażu]**
> - Prevalence wzmianki o osobie publicznej i typów scamu (z ręcznie przejrzanych 50–100 losowych rekordów, z CI): {{P09: prevalence | zależy od: dane, pilotaż | domyślnie: brak}}
> - Notatki z ręcznego przeglądu (co zaskoczyło, co poprawić w codebooku): {{P23: notatki i przykłady z pilotażu | zależy od: dane | domyślnie: brak}}

Narzędzie pomocnicze do statystyk opisowych: `python tools/audit_dataset.py dane.csv` (w tym udział reklam bez daty końca i rozkład czasu emisji reklam zakończonych, jako opis bez korekty cenzurowania).

## 10. Ograniczenia i źródła błędu (wersja do karty)

Pełny rejestr w 06. Najważniejsze dla pytania o skalę i czas życia: (1) czas życia jako czas do usunięcia, jeśli scam definiuje usunięcie (R03); (2) cenzurowanie prawostronne (reklamy wciąż aktywne) i lewostronne (reklamy sprzed okna źródła) oraz retencja źródła (R01, R17); (3) skala jako liczba w ramce, a nie w populacji (R18); (4) błąd klasyfikacji wizerunku na poziomie L1 (R05); (5) klastrowanie (R06); (6) dane osobowe i regulaminy (R09, R10).

## 11. Stan wiedzy i uzasadnienie wartości badania

> **[LEAD – DO WYPEŁNIENIA]** {{P31: stan wiedzy, luka, uzasadnienie wartości badania | zależy od: lead | domyślnie: brak}}

Źródła zebrane w ramach pracy pipelinu (metody pomiaru, annotacja, ocena): 07.
