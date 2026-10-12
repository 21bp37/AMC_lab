# Materiały M1: inżynier pipelinu

*Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”*

**Status:** szkice do redakcji, bez dostępu do danych. Zakres: codebook, gold standard, walidacja annotatora ocenianego, analiza błędów.

## Legenda oznaczeń

- `{{Pnn: ...}}`: placeholder do uzupełnienia; właściciel w rejestrze 00.
- **[LEAD – DO WYPEŁNIENIA]**: miejsce należące do team leada (pytanie, hipoteza, definicje skali i czasu życia, konstrukt wizerunku, skład annotatorów, stan wiedzy). Nie ma tu propozycji pipelinu.
- **[INŻ. DANYCH – DO WYPEŁNIENIA]**: miejsce należące do inżyniera danych (źródła, legalność, ramka, pola, statystyki opisowe). Tylko placeholdery.
- **[PIPELINE – DO WYPEŁNIENIA]**: wyniki z pilotażu i danych, które uzupełnia inżynier pipelinu.
- **[ANALITYK – DO WYPEŁNIENIA]**: modele czasu życia i korekty końcowe.
- Odwołania `[klucz]` odpowiadają wpisom w 07.
- 
## Nomenklatura

**Dane i jednostki**
- **Reklama:** pojedynczy rekord w źródle (`ad_id`).
- **Kreacja:** treść reklamy widoczna dla odbiorcy (tekst, nagłówek, obraz lub wideo); ta sama treść emitowana wielokrotnie przez tego samego reklamodawcę liczy się jako jedna kreacja (`creative_id`, po deduplikacji kopii).
- **Reklamodawca (klaster):** podmiot emitujący reklamy (`advertiser_id`); reklamy jednego reklamodawcy nie są niezależnymi obserwacjami.
- **Ramka:** zbiór reklam kandydujących, z którego losujemy i na którym szacujemy; wnioski dotyczą ramki, a nie wszystkich reklam.
- **Zbiór cenzurowany:** zbiór, w którym widzimy tylko to, co źródło zachowało i udostępniło (np. w oknie retencji).
- **Skala, czas życia reklamy:** definicje ustala lead (P27, P28).

**Zjawisko**
- **Scam:** reklama oszukańcza; rozróżniamy typ oferty z treści reklamy (`scam_type`) i dowód zewnętrzny (domena docelowa na Liście Ostrzeżeń CERT Polska).
- **Wizerunek osoby publicznej:** poziom L1 to wzmianka w tekście, nagłówku, podpisie linku lub domenie; poziom L2 to widoczna twarz osoby publicznej, oceniana przez annotatora referencyjnego bez ustalania tożsamości po twarzy.
- **Populacja badana:** reklamy spełniające łącznie kryterium wizerunku (wzmianka lub twarz) i kryterium scamu.

**Pomiar**
- **Codebook:** instrukcja kodowania (zmienne, wartości, przykłady, przypadki graniczne), wspólna dla wszystkich annotatorów.
- **Annotator:** podmiot (osoba lub narzędzie), który stosuje codebook do reklamy; **referencyjny (R)** tworzy gold standard, **oceniany (O)** jest sprawdzany względem niego.
- **Gold standard:** próba reklam zakodowana ręcznie i uzgodniona, względem której oceniamy annotatora ocenianego.
- **Pilotaż:** próbne kodowanie 30–50 reklam przed zamrożeniem codebooka; służy do poprawy definicji, a nie do uzyskania wyników.
- **Zamrożenie codebooka:** ustalenie wersji (z hashem); zmiana wymaga nowej wersji i wpisu w dzienniku zmian.
- **Prompt:** instrukcja dla annotatora ocenianego, zawierająca wyłącznie treść codebooka.
- **Dziennik uruchomień:** zapis każdego uruchomienia annotatora ocenianego (model, wersja, parametry, hashe promptu, danych i codebooka).

**Miary**
- **Krippendorff α, Cohen κ:** miary zgodności między annotatorami skorygowane o zgodność przypadkową; progi α: ≥ 0,80 wiarygodne, 0,667–0,80 tylko wnioski wstępne, poniżej 0,667 odrzucić.
- **Pozytyw, klasa:** klasa to jedna wartość zmiennej (np. `celeb_mention = explicit_name`); pozytyw to reklama, której gold standard przypisuje tę wartość.
- **Precision, recall, F1:** odsetek trafnych wśród oznaczonych pozytywów, odsetek wykrytych wśród prawdziwych pozytywów oraz ich średnia harmoniczna.
- **Prevalence:** udział reklam z daną cechą; precision bez prevalence nie jest interpretowalna.
- **Przedział ufności (CI), przedział Wilsona:** zakres prawdopodobnych wartości w populacji; Wilson jest wiarygodny przy małych próbach i odsetkach bliskich 0 lub 1.
- **ICC, efekt projektu (deff):** podobieństwo reklam w obrębie klastra oraz krotność, o jaką próba klastrowa jest mniej informatywna niż niezależna.
- **Bootstrap po klastrach:** liczenie CI przez losowanie całych reklamodawców.
- **Flip rate:** odsetek reklam, którym zmiana promptu lub konfiguracji zmienia etykietę.
- **Cenzurowanie prawostronne:** brak końca emisji (reklama wciąż aktywna lub brak danych); lewostronne: początek przed oknem źródła.
- 
## Zakres względem M1 (karta eksploracji danych, bloki 1–2)

| Dokument | Zakres |
|---|---|
| 01 plan pomiaru, 06 ryzyka, 00 rejestr | rdzeń M1 |
| 02 codebook, 03 interfejs danych, 04 annotator oceniany | M1 w wersji skróconej (zmienne, źródła, wykonalność); szczegóły to przygotowanie kolejnych etapów |
| 05 gold standard i walidacja, 10 playbook (kroki 5–7), narzędzia | bank na kolejne etapy; do M1 wystarczy 1–2 zdania planu walidacji |
| 07 bibliografia, 09 ujawnienie AI | wsparcie |

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
| D7 | Czy liczba klastrów jest wystarczająca? (P11, P12) | bootstrap klastrowy lub efekty losowe | agreguj do poziomu reklamodawcy lub kampanii; przy bardzo małej liczbie klastrów wnioskowanie tylko opisowe [cameron2015] |
| D8 | Czy udział reklam po polsku jest wystarczający? (P10) | analiza łączna | analizy osobno per język, wnioski ograniczone do języka z próbą |
| D9 | Czy ramka (P29) jest zbudowana niezależnie od wyniku annotatora ocenianego i od kryterium „scam”? | skalę można interpretować względem ramki | skalę raportujemy wyłącznie jako liczbę w ramce, bez uogólnienia na populację reklam |

---

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

## 2. Co mierzy pipeline

| Wielkość | Skąd | Kto odpowiada |
|---|---|---|
| Przynależność reklamy do populacji badanej: (a) wzmianka lub wizerunek osoby publicznej, (b) scam | annotator oceniany, zwalidowany na gold standardzie | [PIPELINE] |
| Typ scamu (warstwa, do podziałów) | j.w. | [PIPELINE] |
| Dowód zewnętrzny scamu (domena docelowa, Lista Ostrzeżeń CERT) | dane i lista | [INŻ. DANYCH] dostarcza, [PIPELINE] zestawia |
| Skala (liczby reklam, kreacji, reklamodawców; ewentualnie zasięg) | liczone z tabeli po klasyfikacji | [PIPELINE] dostarcza estymatę z korektą błędu klasyfikacji; definicja: [LEAD] |
| Czas życia (początek i koniec emisji) | metadane źródła | [INŻ. DANYCH] dostarcza; obróbka (cenzurowanie, model czasu): [ANALITYK] |

Annotator oceniany nie mierzy ani skali, ani czasu życia. Mierzy **przynależność do klasy**, a zadaniem pipelinu jest pokazać, jak błąd tej klasyfikacji wpływa na oba wyniki (sekcja 7).

## 3. Jednostka analizy i ramka

- **Jednostka:** unikatowa kreacja (`creative_id`), z reklamodawcą jako klastrem. Reklamy nie są niezależnymi obserwacjami: w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [gendigital2026]; dla naszych danych koncentrację policzy inżynier danych (P11).
- **Ramka (zbiór kandydujący):** > **[INŻ. DANYCH / LEAD – DO WYPEŁNIENIA]** {{P29: jak zbudowano zbiór reklam kandydujących | zależy od: źródło, P01 | domyślnie: brak}}. Źródło, kraje, języki, okno dat: {{P01: źródło, kraje, języki, okno dat | zależy od: macierz legalności (P07) | domyślnie: brak}}. Liczebność: {{P02: liczba reklam, kreacji, reklamodawców | zależy od: pobranie danych | domyślnie: nieznana}}.
- **Wymaganie pipelinu wobec ramki:** ramka nie może być zbudowana na wyniku annotatora ocenianego ani na kryterium „scam”; w przeciwnym razie skala dotyczy tylko ramki i nie uogólnia się na populację reklam (D9).
- Ramka jest **zbiorem cenzurowanym** (R01): wnioski dotyczą reklam widocznych w źródle w oknie jego retencji.

## 4. Definicje i dowód na scam

**Wizerunek znanej osoby (kryterium populacji).** Dwa poziomy (02):
- **L1 (wykonalny):** *wzmianka* o osobie publicznej w tekście, nagłówku, podpisie linku lub domenie reklamy (`celeb_mention`).
- **L2 (warunkowy, po D1):** *widoczna twarz* osoby, którą annotator referencyjny uznaje za osobę publiczną, bez ustalania tożsamości po twarzy (zob. 04, zasada 4), oraz podejrzenie syntetyczności kreacji. Bez legalnego dostępu do kreacji L2 jest wyłączony, a konstrukt zawęża się do wzmianki (ograniczenie opisane w R05; decyzja o temacie: P30). Dostępność: {{P04: dostępność kreacji | zależy od: regulamin źródła | domyślnie: niedostępne}}.

**Scam.** Dwie warstwy, rozdzielone celowo:
1. *Typ oferty* z treści reklamy (`scam_type`, kodowany przez annotatorów, łącznie z wartościami `not_scam` i `unclear`).
2. *Dowód zewnętrzny*: łańcuch reklama, domena docelowa, Lista Ostrzeżeń CERT Polska [certlist]. Lista zawiera domeny wprowadzające w błąd i wyłudzające dane; według miesięcznych podsumowań CERT domeny są blokowane na 6 miesięcy, a jeśli nadal zawierają niebezpieczne treści, wpisuje się je ponownie. CSIRT KNF opisuje zgłaszanie do wpisu na tę listę domen z reklam fałszywych inwestycji publikowanych na Facebooku [csirtknf2024]. Warunki: {{P18: warunki użycia Listy Ostrzeżeń | zależy od: inżynier danych | domyślnie: brak}}, {{P05: dostępność adresu docelowego | zależy od: pola źródła | domyślnie: nieznana}}, pokrycie: {{P19: odsetek domen z danych możliwych do zestawienia z listą | zależy od: P05, P18 | domyślnie: nieznane}}.
3. *Ocena annotatora referencyjnego* (`scam_judgement`) jest zmienną pomocniczą, nie dowodem.

**Dlaczego nie wystarczy usunięcie reklamy przez platformę jako definicja scamu.** Jeśli „scam” = „usunięta”, to **czas życia jest z definicji czasem do usunięcia**, więc pytanie o czas życia staje się tautologią, a skala dotyczy tylko reklam wykrytych przez platformę (R02, R03). Dodatkowo platforma ma dla reklam z osobami publicznymi osobny mechanizm wykrywania (porównywanie twarzy z reklam ze zdjęciami profilowymi) [meta2024celebbait]. Dlatego scam etykietujemy niezależnie od decyzji platformy, a decyzję platformy (`platform_removal`) traktujemy jako zmienną do analizy wrażliwości. Jeśli nie ma adresu docelowego, łańcuch dowodu odpada (D4) i trzeba to zapisać jako jawne zastrzeżenie.

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
2. Gold standard: losowanie warstwowe z limitem na reklamodawcę i zapisem prawdopodobieństw włączenia; annotatorzy referencyjni ({{P21: skład | zależy od: lead | domyślnie: nieznany}}); Krippendorff α jako miara główna z progami 0,80 i 0,667 [krippendorff2004].
3. Annotator oceniany jest oceniany względem gold standardu; precision zawsze z prevalence; CI przez bootstrap po klastrach [cameron2015].
4. Wrażliwość na parafrazy promptu i wersję modelu raportowana jako zakres [baumann2025].
5. Skalę (liczbę reklam w klasie) szacujemy z korektą błędu klasyfikacji, bo liczba reklam oznaczonych przez annotatora ocenianego bez korekty daje obciążenie [egami2025dsl]. Estymator różnicowy dla częstości jest w repozytorium; pełne metody do analizy czasu życia (np. model przeżycia z korektą błędu klasy) wdraża {{P12: ICC i deff; metoda dla czasu życia | zależy od: [ANALITYK] | domyślnie: nie wdrożono}}.

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
| Czy annotator oceniany zadziała? | Literatura dla tekstu, angielskiego; **brak równorzędnej walidacji dla reklam z obrazem po polsku** [gilardi2023; ziems2024] | [PIPELINE] | D5, P14 |

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

---

# 02. Codebook v0.1

**Status:** wersja robocza przed pilotażem. Zmiany tylko przez dziennik zmian (`templates/codebook_changelog.md`) i podniesienie wersji. Lista dozwolonych wartości jest w `tools/schema.yaml` (źródło prawdy); po zmianie uruchom `python tools/checks.py consistency`.

**Dlaczego tak:** codebook jest jedną instrukcją dla wszystkich annotatorów (referencyjnych i ocenianego); ta sama wersja służy do annotacji referencyjnej i do promptu annotatora ocenianego, co jest wzorcem z prac porównujących LLM z annotatorami [gilardi2023; halterman2025].

**Temat:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” Codebook służy do zaklasyfikowania reklamy do populacji badanej (wzmianka lub wizerunek osoby publicznej, scam) i do podziału na warstwy. Skala i czas życia pochodzą z metadanych, nie z codebooka. Definicje skali, czasu życia i konstruktu „wizerunek” należą do leada (P27, P28, P30): {{P30: konstrukt wizerunku: wzmianka, twarz czy oba | zależy od: lead, D1 | domyślnie: brak}}.

**Rdzeń i zmienne dodatkowe.** Rdzeń: `celeb_mention`, `scam_type`, `scam_judgement`, `celeb_category` oraz (po D1) `celeb_face_visible`, `media_type`, `media_synthetic_suspected`. Zmienne oznaczone „(dodatkowa)” są poza rdzeniem pytania: opcjonalne i eksploracyjne, kodowane tylko jeśli starczy czasu na pilotaż. Codebook przechodzi co najmniej dwie rundy pilotażu, zanim zostanie zamrożony (05).

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
2. **Kodowanie na ślepo:** annotator nie widzi zasięgu, czasu emisji, wyniku annotatora ocenianego ani dowodów zewnętrznych (lista CERT, usunięcie przez platformę). Powód: znajomość wyniku obciążałaby kodowanie kryteriów populacji.
3. **Kodujemy to, co widać w reklamie**, nie to, co annotator wie z zewnątrz. Wyjątek: rozpoznanie osoby po opisie (`implied`) wymaga jednoznaczności opisu, a nie wiedzy specjalnej.
4. **Kategoria `unsure` jest pełnoprawna.** Wybieraj ją zamiast zgadywać. Odsetek `unsure` jest raportowany; wysoki odsetek oznacza zbyt niejasną definicję.
5. **Dwa poziomy:**
   - **L1** (z tekstu i metadanych): wykonalny bez dostępu do kreacji.
   - **L2** (wizualne): kodowany wyłącznie po potwierdzeniu punktu decyzyjnego D1 (legalny dostęp do kreacji): {{P04: dostępność kreacji i podstawa prawna | zależy od: regulamin źródła | domyślnie: brak dostępu, L2 wyłączony}}.
6. **Ograniczenie konstruktu L1:** temat mówi o *wizerunku*, a poziom L1 mierzy tylko *wzmiankę* o osobie publicznej w tekście. Reklama z twarzą osoby publicznej i bez nazwiska w tekście zostanie na L1 zakodowana jako `none` i wypadnie z populacji, co zaniża skalę. To jest błąd pomiaru kryterium populacji (06, R05) i jest opisany jako ograniczenie, dopóki L2 nie jest dostępny.

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

Ocena annotatora, czy reklama wygląda na oszukańczą (`scam`, `not_scam`, `unclear`) na podstawie wyłącznie reklamy. **Nie zastępuje dowodu zewnętrznego.** Służy jako zmienna pomocnicza i do analizy zgodności między oceną annotatora referencyjnego a dowodem zewnętrznym (sprawdzian, czy łatwo odróżnić scam od legalnej reklamy).

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

`yes`, jeśli kreacja wygląda na wygenerowaną lub zmanipulowaną (artefakty obrazu, niezgodność ruchu ust i głosu), `no`, `unsure`, `na_no_media`. Zmienna oznacza *podejrzenie* annotatora, a nie ustalenie; wiarygodność oceny annotatora referencyjnego przy deepfake'ach jest ograniczona i jest raportowana jako zmienna o niskim oczekiwanym α.

## Pola z dowodami zewnętrznymi (nie kodowane przez annotatorów)

Wypełnia pipeline na podstawie danych i list publicznych, po zakończeniu kodowania kryteriów populacji: `dest_domain`, `domain_on_cert_list`, `cert_list_interval`, `platform_removal` (definicje w `tools/schema.yaml`). Dostępność zależy od P05, P18, P19.

## Procedura

1. Pilotaż 1 (30–50 reklam, każdy annotator referencyjny koduje samodzielnie), potem omówienie niezgodności, korekta definicji, wersja 0.2 z wpisem w dzienniku zmian.
2. Pilotaż 2 na nowej próbie; jeśli zmienna wciąż nie osiąga α ≥ 0,667, usuń ją z pomiaru (10, punkt D3).
3. Dopiero po zamrożeniu codebooka losowanie i annotacja zbioru gold standardu (05).
4. Każda zmiana po zamrożeniu = nowa wersja + powtórna ocena na próbie kontrolnej.

---

# 03. Specyfikacja interfejsu: pipeline i inżynier danych

Ten dokument mówi, **czego pipeline potrzebuje od inżyniera danych** i **co pipeline sprawdzi po otrzymaniu danych**. Treść merytoryczną dotyczącą źródeł, podstaw prawnych, ramki i data statementu uzupełnia inżynier danych; w miejscach, które do niego należą (oznaczone **[INŻ. DANYCH – DO WYPEŁNIENIA]**), są placeholdery i nie są wypełnione propozycją. Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”; definicje skali i czasu życia należą do leada (P27, P28).

## 1. Zasada nadrzędna

Wszystkie dane pochodzą z legalnych źródeł, zgodnie z regulaminami stron i licencjami. **Nie używamy scrapowania ani narzędzi do masowego pobierania mediów ze stron**, nawet gdy są popularne w pracach badawczych, jeśli regulamin źródła tego nie dopuszcza. Pierwszym zadaniem inżyniera danych jest macierz legalności (sekcja 3); pipeline nie rusza danych, zanim ją zobaczy.

## 2. Wymagany schemat tabeli (jedna wiersz = jedna reklama w źródle)

Kolumny **wymagane** to minimum do wykonania planu pomiaru (01). Kolumny **warunkowe** zależą od tego, co źródło legalnie udostępnia (punkty D1, D4, D6). Nazwy kolumn można zmienić, ale mapowanie musi być opisane.

| Kolumna | Opis | Wymagana? | Uwagi |
|---|---|---|---|
| `ad_id` | stabilny identyfikator reklamy w źródle | tak | klucz główny |
| `creative_id` | identyfikator unikatowej kreacji po deduplikacji (ten sam tekst/obraz u tego samego reklamodawcy = jedna kreacja) | tak | metoda deduplikacji opisana w data statement |
| `advertiser_id` | stabilny identyfikator reklamodawcy (strony) | tak | klaster w analizie; pseudonimizacja, jeśli wymagana |
| `platform` | platforma emisji | tak | |
| `delivery_start`, `delivery_stop` | początek i koniec emisji (koniec pusty = reklama aktywna lub brak danych; znaczenie opisuje data statement) | tak, jeśli źródło je udostępnia | czas życia (P28); brak = D6 |
| `retrieval_date` | data pobrania rekordu | tak | stan źródła w tym dniu; konieczna do oceny cenzurowania prawostronnego |
| `countries_delivered` | kraje dostarczenia | tak | zakres próby (P01) |
| `ad_text`, `headline`, `link_caption` | tekst reklamy | tak | wejście dla poziomu L1 |
| `language` | język tekstu (metoda detekcji opisana) | tak | D8 |
| `cta_label` | etykieta przycisku wezwania do działania | jeśli dostępna | |
| `dest_url` lub `dest_domain` | adres docelowy | warunkowa | łańcuch dowodu scamu (D4); P05 |
| `reach_*` | zasięg (liczba całkowita lub przedział) | warunkowa | tylko jeśli lead uzna zasięg za część „skali" (P27); P06 |
| `frame_source` | kryterium lub zapytanie, przez które reklama trafiła do ramki | warunkowa | niezależność ramki od annotatora ocenianego (D9, P29) |
| `creative_available` | czy kreacja (obraz/wideo) jest legalnie dostępna | tak | D1 |
| `creative_path` | ścieżka do pliku kreacji | warunkowa | tylko jeśli legalnie wolno |
| `source_removed_flag` | czy źródło oznacza reklamę jako usuniętą/naruszającą zasady | jeśli dostępne | dowód zewnętrzny, nie wynik; R03 |
| `source_name`, `source_version` | skąd i w jakiej wersji | tak | odtwarzalność |

Dostępność poszczególnych pól (według oficjalnej dokumentacji, nie scraperów): {{P06: pola zasięgu, czasu emisji i targetowania dostępne dla reklam komercyjnych | zależy od: oficjalna dokumentacja źródła | domyślnie: nieznane}}.

## 3. Macierz legalności: szkielet

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** Cała macierz.

Jeden wiersz = jedno źródło. Bez wypełnionej macierzy nie rozpoczynamy pracy na danych.

| Źródło | Kto udostępnia | Podstawa (regulamin, licencja, umowa) | Wymagania dostępu (tożsamość, wniosek, umowa uczelni) | Pola dostępne | Kreacje? | Retencja | Co wolno zapisać i publikować | Dane osobowe? | Ocena |
|---|---|---|---|---|---|---|---|---|---|
| {{P07: źródło 1 (np. oficjalne API biblioteki reklam) \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |
| {{P07: źródło 2 (np. Meta Content Library) \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |
| {{P18: źródło 3: Lista Ostrzeżeń CERT Polska i jej warunki użycia \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |

Pytania, na które macierz musi odpowiedzieć (lista pytań jest moja, odpowiedzi należą do inżyniera danych):

1. Czy oficjalne API biblioteki reklam zwraca reklamy komercyjne dostarczone w UE i które pola (tekst, daty, adres docelowy, zasięg)? Dokumentacja firm trzecich sugeruje, że reklamy inne niż polityczne są dostępne tylko, jeśli były dostarczone do UE lub Wielkiej Brytanii, i tylko przez ograniczony czas; **to wymaga potwierdzenia w oficjalnej dokumentacji**.
2. Czy regulamin pozwala na zapis i dalsze przetwarzanie kreacji (obraz/wideo)? (D1)
3. Czy uczelnia może złożyć wniosek o Meta Content Library i w jakim terminie? (P20) Według dokumentacji dostęp odbywa się przez ICPSR, wymaga umowy o korzystaniu z danych między ICPSR a instytucją, zabrania eksportu danych z platformy badawczej i uploadu danych do niej; dostępność reklamów w Content Library nie jest przeze mnie potwierdzona.
4. Czy wolno użyć Listy Ostrzeżeń CERT Polska do zestawienia z domenami z reklam i na jakich warunkach? (P18)
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
5. Dostępność pól czasu emisji i adresu docelowego (P05, P06), dostępność kreacji (P04); udział reklam bez daty końca emisji i rozkład czasu emisji reklam zakończonych (jako opis, bez korekty cenzurowania; P28, D6).
6. Czy jest data statement i wpis w macierzy legalności; **jeśli nie, pipeline zatrzymuje pracę i zgłasza to**.

Wyniki audytu są wpisywane do rejestru placeholderów (00) z odwołaniem do uruchomienia (hash danych w dzienniku).

---

# 04. Plan instrumentu pomiarowego

Instrument, czyli **annotator oceniany (O)**, koduje zmienne codebooka (02) na dużej liczbie reklam. Klasyfikuje reklamy do populacji badanej (wzmianka lub wizerunek osoby publicznej, scam) i do warstw (typ scamu, kategoria osoby). **Skala i czas życia reklam pochodzą z metadanych**, nie od annotatora ocenianego, więc jego zadanie jest wąskie i walidowalne. Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”
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
| D. Multimodalny LLM (VLM) dla obrazu i tekstu | L2 | Jedyny wariant do `media_type`, `media_synthetic_suspected` | **Brak równorzędnej walidacji w literaturze dla tego zadania**; zbiory pokrewne to chińskie media społecznościowe i inne zadania [chasm2026; adsprofiles2025], przeczytaj je w całości przed użyciem jako wzorca; ryzyko dla `media_synthetic_suspected` (wykrywanie deepfake'ów jest trudne) | tylko po D1 (legalny dostęp do kreacji) |
| E. Annotacja wyłącznie przez annotatorów referencyjnych na próbie + estymacja korygowana | L1/L2 | Najlepsza wiarygodność | Mała próba, szerokie CI | wariant zapasowy, gdy B/C/D nie osiągną zgodności (D5) |

## 3. Drzewo decyzji

1. **D1: czy kreacje są legalnie dostępne?**
   - **Nie** (scenariusz domyślny, dopóki nie ma dowodu): wyłącznie L1; warianty A, B lub C, zawsze z wariantem A jako punktem odniesienia. Konstrukt zawęża się do *wzmianki o celebrycie* (02, zasada 6).
   - **Tak:** dodatkowo L2; wariant D dla `media_type`, a `celeb_face_visible` koduje wyłącznie annotator referencyjny (annotator oceniany nie ocenia tożsamości osób na obrazie).
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

Cel: wykazać (albo wykazać brak), że annotator oceniany klasyfikuje reklamy do populacji badanej (wzmianka lub wizerunek osoby publicznej, scam) z błędem, który znamy i który uwzględniamy przy szacowaniu skali oraz przy interpretacji czasu życia reklam. Miara sukcesu to wiarygodny wniosek, nie wysokie F1 (zasady kursu). Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”
Mierzymy jakość annotatora ocenianego (O), a nie cechy reklam. Dla każdej zmiennej priorytetowej (`celeb_mention`, `scam_type`) osobna wartość jest klasą, np. `celeb_mention = explicit_name`. Annotatorzy referencyjni kodują próbę reklam, a ich uzgodnione etykiety tworzą gold standard; reklama, której gold standard przypisuje daną wartość, jest *pozytywem* tej klasy. Annotator oceniany koduje te same reklamy, a recall to odsetek pozytywów, które też oznaczył. Dla skali liczą się oba kierunki błędu: fałszywe pozytywy zawyżają liczbę reklam w klasie (precision), a pominięte pozytywy ją zaniżają (recall). Klasą o największym znaczeniu jest przynależność do populacji badanej, czyli łączne spełnienie kryteriów wzmianki (lub wizerunku, po D1) i scamu. Poniższe wartości mówią, ile pozytywów danej klasy musi mieć gold standard, żeby ten recall zmierzyć z założoną dokładnością.

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

1. **Warstwy** definiujemy wyłącznie z cech znanych przed annotacją: miesiąc, język, typ scamu z baseline'u, wynik baseline'u słownikowego (obecność nazwiska z listy osób publicznych), ewentualnie predykcja annotatora ocenianego. Powód: rzadką klasę (wzmianka lub wizerunek) trzeba nadpróbkować (losowanie proste dałoby zbyt mało pozytywów), a metody korekty błędu klasyfikatora wymagają próby ze znanymi prawdopodobieństwami [egami2025dsl].
2. **Limit na reklamodawcę** w komórce (warstwa x reklamodawca): wartość limitu jest parametrem; wybór: {{P24: limit reklam na reklamodawcę w komórce | zależy od: rozkład reklamodawców w danych | domyślnie: heurystyka własna, bez źródła; ustaw tak, aby żaden reklamodawca nie przekraczał 5% próby}}.
3. **Nadpróbkowanie warstw z rzadką klasą** i warstwa z predykcją negatywną (żeby oszacować recall, trzeba mieć etykiety także tam, gdzie annotator oceniany mówi „nie").
4. Seed, parametry i hash danych wejściowych zapisujemy w dzienniku uruchomień (`tools/run_log.py`).

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
5. **Wpływ na skalę i czas życia:** (a) skala: porównanie estymaty naiwnej (liczba reklam w klasie według O) z estymatą z korektą na gold standardzie (`tools/estimators.py`), z przedziałem po klastrach; (b) czas życia: porównanie rozkładu czasu emisji reklam zaklasyfikowanych poprawnie i błędnie oraz sprawdzenie, czy błąd różni się między reklamami krótko- i długotrwałymi. Obróbka cenzurowania i model czasu życia: > **[ANALITYK – DO WYPEŁNIENIA]**.
6. Wynik pierwszego testu: > **[PIPELINE – DO WYPEŁNIENIA]** {{P14: zgodność annotatora ocenianego z gold standardem | zależy od: pilotaż, P15 | domyślnie: brak}}. Decyzja: D5.

## 6. Korekta błędu pomiaru w analizie końcowej

Wniosek z literatury: predykcje modelu analizowane tak, jakby były obserwacjami bez błędu, dają obciążenie i nieprawidłowe przedziały ufności nawet przy dokładności powyżej 90%; metoda DSL łączy predykcje z mniejszą próbą etykiet eksperckich losowaną ze znanymi prawdopodobieństwami [egami2025dsl].

- **Co mamy:** `tools/estimators.py`, estymator różnicowy dla prostego parametru (częstość klasy; liczbę reklam w klasie, czyli skalę, dostajemy mnożąc przez liczebność ramki P02). Test na danych syntetycznych (300 powtórzeń): błąd naiwnej estymaty −0,029 (SE 0,0008), po korekcie −0,002 (SE 0,0017), czyli brak wykrywalnego obciążenia; estymator po korekcie ma jednak ok. dwukrotnie większe odchylenie standardowe niż naiwny (0,029 vs 0,014). To kompromis obciążenie–wariancja, o którym trzeba pisać w preprincie.
- **Czego nie mamy:** pełnego DSL dla regresji z kowariatami ani korekty dla modelu czasu życia. Będą potrzebne, jeśli pytanie badawcze (P26) obejmie związek czasu życia z cechami reklamy (np. typ scamu, wizerunek). To jest zadanie dla analityka po lekturze pracy [egami2025dsl]: > **[ANALITYK – DO WYPEŁNIENIA]**; status: do wdrożenia.
- Analiza wrażliwości: `prevalence_from_sens_spec` pozwala sprawdzić, jak zmieniałaby się częstość przy założonej czułości i swoistości z przedziału ufności walidacji. Używać z zakresem wartości.

## 7. Co jest przyjęte bez źródła (heurystyka własna)

1. Docelowa liczba 60 pozytywów na klasę raportowaną osobno.
2. Limit 5% próby na reklamodawcę.
3. Dwie rundy pilotażu po 30–50 reklam.

Każdą z tych wartości trzeba uzasadnić lub zmienić na podstawie danych (P09, P11, P13) i opisać w preprincie jako decyzję własną.

---

# 06. Rejestr ryzyk i ograniczeń

Ryzyka są wpisem do karty M1 (jawne ograniczenia i źródła błędu to kryterium oceny). Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” Znacznik na początku ryzyka wskazuje, kto je rozstrzyga lub potwierdza: **[PIPELINE]**, **[INŻ. DANYCH]**, **[LEAD]**; ryzyka danych i projektu zgłosił pipeline z własnej perspektywy, a ich opis i ocenę muszą potwierdzić wskazane role. Prawdopodobieństwo i wpływ to **ocena własna** (niski/średni/wysoki) do rewizji po danych; nie są oparte na pomiarze. „Wskaźnik z danych" mówi, co sprawdzić, gdy dane już są.

| ID | Ryzyko | Skutek dla wniosku | Praw. | Wpływ | Środek zaradczy | Wskaźnik z danych |
|---|---|---|---|---|---|---|
| R01 | **[INŻ. DANYCH]** **Biblioteka reklam jako zbiór cenzurowany**: widzimy to, co platforma zachowała i udostępniła; reklamy usunięte lub poza oknem retencji mogą znikać. Luki biblioteki opisano dla amerykańskich reklam politycznych [edelson2020; lepochat2022]; dla reklam komercyjnych w UE nie jest to ustalone | Obciążenie selekcją; wnioski o częstości tylko dla reklam widocznych | wysokie | wysoki | Jawnie ograniczyć wnioski do reklam widocznych w źródle w oknie dat; zapisywać datę pobrania; nie uogólniać na wszystkie reklamy | rozkład czasu między końcem emisji a pobraniem; udział reklam bez daty końca (P03) |
| R02 | **[INŻ. DANYCH / LEAD]** **Czas życia zniekształcony przez egzekwowanie**: platforma może szybciej usuwać reklamy z osobą publiczną (ma do tego dedykowany mechanizm porównania twarzy [meta2024celebbait]), więc czas życia zależy od polityki egzekwowania, a nie tylko od „trwałości” zjawiska | Błędna interpretacja czasu emisji | wysokie | wysoki | Opisać czas życia jako czas widoczności w źródle; zestawić z `platform_removal`; zastrzeżenie w karcie | rozkład czasu emisji reklam usuniętych i nieusuniętych |
| R03 | **[PIPELINE / INŻ. DANYCH]** **Etykieta scamu zależna od usunięcia przez platformę**: jeśli „scam" = usunięcie, to czas życia jest czasem do usunięcia (tautologia), a skala dotyczy tylko reklam wykrytych; dodatkowo reklamy z osobą publiczną są wykrywane osobnym mechanizmem | Czas życia i skala nie do zinterpretowania | wysokie | wysoki | Scam etykietować niezależnie od decyzji platformy: dowód zewnętrzny (domena docelowa, lista CERT) i `scam_type` annotatora referencyjnego (D4); analiza wrażliwości na definicję | zgodność między `scam_judgement`, listą CERT i `platform_removal` |
| R04 | **[INŻ. DANYCH]** **Brak adresu docelowego reklamy**: bez domeny nie ma łańcucha reklama, domena, lista CERT (P05) | Scam tylko z oceny annotatora i wskazania platformy | średnie | wysoki | D4; jawne zastrzeżenie; scam jako zmienna z poziomem pewności | odsetek rekordów z domeną |
| R05 | **[PIPELINE]** **Błąd pomiaru kryterium populacji** (L1 mierzy wzmiankę, nie wizerunek): reklamy z twarzą bez nazwiska są kodowane jako `none` i wypadają z populacji | Zaniżona skala; kierunek błędu czasu życia zależy od tego, które reklamy wypadają | wysokie (dopóki brak L2) | wysoki | Walidacja `celeb_mention` jako zmiennej priorytetowej; korekta błędu (05, sekcja 6); jawne ograniczenie konstruktu; decyzja leada o konstrukcie (P30) | recall `celeb_mention` w gold standardzie; analiza błędów wg typu reklamy |
| R06 | **[PIPELINE / INŻ. DANYCH]** **Koncentracja u kilku reklamodawców**: efektywna liczba obserwacji = liczba klastrów, nie reklam; przy niewielkiej liczbie klastrów standardowe błędy odporne na klastrowanie zaniżają niepewność [cameron2015] | Zawyżona pewność wniosków | wysokie | wysoki | Bootstrap po klastrach lub agregacja do reklamodawcy; limit w losowaniu; D7 | P11, P12 |
| R07 | **[LEAD]** **Zasięg (jeśli lead włączy go do „skali") zależy od budżetu i algorytmu dostarczania, nie tylko od kreacji** | Różnice zasięgu mogą wynikać z budżetu | wysokie | wysoki | Jawny opis zmiennych zakłócających; zasięg nie jest warunkiem pytania o skalę w liczbach reklam (P27) | dostępność budżetu (P06: dla reklam komercyjnych prawdopodobnie niedostępny) |
| R08 | **[PIPELINE]** **Błąd instrumentu zależny od cech powiązanych z wynikiem** | Obciążenie, którego globalna korekta nie usunie | średnie | wysoki | Analiza błędów wg warstw; próba z etykietami w każdej warstwie (05) | zgodność model–gold wg `scam_type`, języka, kategorii celebryty |
| R09 | **[INŻ. DANYCH / PIPELINE]** **Dane osobowe** (nazwiska osób publicznych; wizerunek). **Rozpoznawanie twarzy jest niezgodne z RODO w naszych warunkach, bo to dane biometryczne z art. 9 ust. 1 bez przesłanki z ust. 2 (04, zasada 4; [edpb2024clearview])**; Meta wstrzymała tę technologię w 2021 r. z powodu obaw społecznych i braku jasnych reguł, a obecnie stosuje ją z natychmiastowym usuwaniem danych twarzy [meta2024celebbait] | Naruszenie RODO/regulaminu, wyłączenie danych z użycia | średnie | wysoki | Bez automatycznego rozpoznawania twarzy; `celeb_id` tylko w pliku roboczym; raportowanie zagregowane po kategoriach; ocena prawna przez inżyniera danych (P07) | wynik oceny w macierzy legalności |
| R10 | **[INŻ. DANYCH]** **Regulamin i licencje**: warunki API/Content Library (zakaz eksportu, publikacji danych osobowych), warunki użycia listy CERT | Niemożność użycia lub publikacji danych | średnie | wysoki | Macierz legalności przed jakąkolwiek pracą na danych (03, P07, P18); wynik negatywny o dostępie jest pełnoprawny | wypełniona macierz |
| R11 | **[PIPELINE]** **Dryf definicji i konfiguracji**: zmiana promptu lub wersji modelu zmienia wynik [baumann2025] | Niepowtarzalność | średnie | średni | Zamrożenie codebooka i zbioru testowego; dziennik uruchomień; raport zakresu po konfiguracjach | flip rate między konfiguracjami (`prompt_robustness.py`) |
| R12 | **[PIPELINE]** **Rzadkie klasy**: za mało pozytywów w gold standardzie; paradoks kappa maskuje jakość kodowania [feinstein1990] | Szerokie CI; fałszywe odrzucenie zmiennej | wysokie | średni | Losowanie warstwowe; α z prevalence i zgodnością pozytywną/negatywną; klasy z małą liczbą pozytywów jako eksploracyjne (05) | P09 |
| R13 | **[PIPELINE]** **Język**: instrument i literatura głównie dla angielskiego; część reklam może być w innych językach | Niższa jakość dla polskiego | średnie | średni | Analiza błędów wg języka; D8 | P10 |
| R14 | **[LEAD]** **Nadinterpretacja**: opis skali i czasu życia może zostać odebrany jako wniosek o skuteczności lub przyczynach; ocena kursu wymaga rozróżnienia opisu od przyczynowości | Nadinterpretacja | średnie | średni | Język tezy (decyzja leada, P26); sekcja ograniczeń w preprincie | — |
| R15 | **[PIPELINE]** **Koszt, limity i czas** przetwarzania | Niemożność przetworzenia całości | średnie | średni | Kodowanie próby zamiast całości (wariant E) i estymacja korygowana | P16 |
| R16 | **[INŻ. DANYCH / LEAD]** **Niewykonalność pomiaru czasu życia**: dla reklam komercyjnych daty emisji (a ewentualnie zasięg) mogą być niedostępne (P06) | Brak zmiennej wynikowej | do ustalenia | wysoki | D6; wynik negatywny o pomiarze jest pełnoprawnym wynikiem (zasady kursu) | P06 |
| R17 | **[INŻ. DANYCH / LEAD]** **Cenzurowanie i obcięcie czasu życia**: reklamy wciąż aktywne (brak końca emisji) i reklamy rozpoczęte przed oknem źródła; retencja źródła obcina historię | Zaniżony lub zniekształcony czas życia | wysokie | wysoki | Jawna definicja czasu życia (P28); raportowanie udziału reklam bez końca; metody analizy przeżycia (analityk) | udział reklam bez daty końca (`audit_dataset.py`), rozkład `delivery_start` względem okna źródła |
| R18 | **[INŻ. DANYCH / LEAD]** **Skala jako liczba w ramce, nie w populacji**: jeśli ramka powstała z kryteriów związanych z osobami publicznymi lub scamem, liczby dotyczą tylko ramki | Zawyżona lub zaniżona skala | wysokie | wysoki | Opis ramki (P29, D9); skala raportowana względem ramki | opis ramki w data statement |

## Wnioski do karty M1

1. Najpoważniejsze zagrożenia dla pytania o skalę i czas życia to R02, R03, R17, R18 i R05. Wszystkie są strukturalne (wynikają z konstrukcji badania i danych), nie techniczne.
2. Część z nich nie jest usuwalna; jest jawnie opisywana jako ograniczenie, a sformułowanie wniosków (decyzja leada, P26) ma to odzwierciedlać.
3. Ryzyka R04, R10, R16 i R17 mogą zawęzić albo uniemożliwić badanie; plan zakłada rozstrzygnięcie ich przed zbieraniem danych (D4, D6, macierz legalności).

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
| `csirtknf2024` | CSIRT KNF (2025). *Raport Roczny CSIRT KNF 2024*. Komisja Nadzoru Finansowego. | Instytucjonalny pomiar reklam fałszywych inwestycji na Facebooku, zgłaszanie domen do CSIRT NASK i wpis na Listę Ostrzeżeń | Zweryfikowane jako publiczny raport; rok publikacji do sprawdzenia |
| `certlist` | CERT Polska. Lista Ostrzeżeń przed niebezpiecznymi stronami. cert.pl/lista-ostrzezen | Lista domen wprowadzających w błąd i wyłudzających dane; według miesięcznych podsumowań domeny są blokowane na 6 miesięcy | Opis potwierdzony w podsumowaniach CERT (licencja CC BY 4.0 dotyczy tych publikacji); **warunki użycia samej listy do sprawdzenia** |
| `radboud2025` | Kablan, L. (2025). *Misleading ad detection: Cryptocurrency scam ad classification on Facebook's ad library*. Praca licencjacka, Radboud University. | Przykład pipeline'u z Meta Ad Library i LLM; precision niskie przy rzadkich pozytywach; deduplikacja zmniejszyła zbiór z ok. 100 tys. do 25 671 reklam, z czego 2454 unikatowe | Zweryfikowane jako praca nierecenzowana; użyj tylko jako przykład poglądowy |
| `zeng2021` | Zeng, E., Wei, M., Gregersen, T., Kohno, T., Roesner, F. (2021). Polls, clickbait, and commemorative $2 bills: Problematic political advertising on news and media websites around the 2020 US elections. *ACM IMC*, 507–525. | Badanie reklam problematycznych metodą pomiarową | Dane bibliograficzne potwierdzone w spisach literatury innych prac; **treści (codebook) nie czytałem** |
| `chasm2026` | Chasm: Unveiling covert advertisements on Chinese social media. arXiv:2604.20511 | Zbiór do oceny multimodalnych LLM w wykrywaniu ukrytych reklam; metryki P, R, F1, AUC; zero-shot, uczenie w kontekście, fine-tuning | Preprint zweryfikowany; autorów i rok do uzupełnienia; **czytaj w całości, zanim użyjesz jako wzorca** |
| `adsprofiles2025` | When ads become profiles: Large-scale audit of algorithmic biases and LLM profiling risks. arXiv:2509.18874 | Multimodalny LLM stosowany do reklam z Facebooka (zadanie inne niż nasze) | Preprint zweryfikowany; autorów do uzupełnienia |
| `clark2026` | Clark, S., Lewandowsky, S. (2026). The continued influence of AI-generated deepfake videos despite transparency warnings. *Communications Psychology* 4. doi:10.1038/s44271-025-00381-9 | Perswazyjność deepfake'a nie znika po ostrzeżeniu (trzy eksperymenty, N = 175, 275, 223); autorzy zastrzegają, że wyjaśnienia związane z ramowaniem zadania nie są wykluczone; **dotyczy wideo i oceny winy, nie reklam**; nie jest używane w dokumentach pipelinu, do decyzji leada o przeglądzie literatury (P31) | Zweryfikowane |

## D. Wnioskowanie i dokumentacja danych

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `cameron2015` | Cameron, A. C., Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. *Journal of Human Resources* 50(2), 317–372. doi:10.3368/jhr.50.2.317 | Wnioskowanie przy danych klastrowych; przy niewielkiej liczbie klastrów standardowe błędy odporne na klastrowanie zaniżają niepewność i trzeba stosować korekty | Zweryfikowane |
| `gebru2021` | Gebru, T. i in. (2021). Datasheets for datasets. *Communications of the ACM* 64(12), 86–92. | Dokumentacja zbioru danych | Zweryfikowane |
| `bender2018` | Bender, E. M., Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *TACL* 6. | Data statement dla zbiorów językowych | Zweryfikowane |

## E. Źródła do uzupełnienia przez inżyniera danych

Oficjalna dokumentacja platform, na której opiera się feasibility (nie została przeze mnie zweryfikowana; opisy pól biblioteki reklam znam wyłącznie z dokumentacji firm trzecich): {{P07: adresy i wersje oficjalnej dokumentacji API biblioteki reklam i Meta Content Library, regulaminy | zależy od: inżynier danych | domyślnie: brak}}.

Dla Meta Content Library znana jest procedura wnioskowa (wniosek przez ICPSR, umowa o korzystaniu z danych między ICPSR a instytucją, zakaz eksportu i wgrywania danych do platformy badawczej, zakaz publikowania danych osobowych) według dokumentacji deweloperskiej Mety i komunikatu ICPSR; zakres pokrycia reklam nie został przeze mnie potwierdzony.

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

Kroki w kolejności. Każdy krok kończy się wpisem w rejestrze placeholderów (00) i, jeśli dotyczy, uruchomieniem zapisanym w dzienniku (`tools/run_log.py`). Punkty D1–D9 są zdefiniowane w 00. Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

## Krok 0. Bramka legalności (przed otwarciem danych)

- Jest macierz legalności i data statement od inżyniera danych? ({{P07: macierz legalności | zależy od: inżynier danych | domyślnie: brak}}, {{P08: data statement | zależy od: P07 | domyślnie: brak}})
- Jeśli nie: **stop**, pracujemy tylko na narzędziach i danych syntetycznych. Wynik negatywny o dostępie do danych jest pełnoprawnym wynikiem projektu.

## Krok 1. Audyt tabeli

`python tools/audit_dataset.py dane.csv` → wpisz do P01, P02, P03, P05, P06, P10, P11. Zapisz hash pliku wejściowego w dzienniku.

Reakcje:
- brakuje kolumn wymaganych → zwróć do inżyniera danych z listą (03, sekcja 2);
- nie ma dat początku i końca emisji → D6 = NIE (czas życia niemierzalny); zasięg jest potrzebny tylko, jeśli lead włączył go do definicji skali (P27);
- duży udział reklam bez daty końca → zgłoś do leada i analityka (cenzurowanie, P28, R17);
- adres docelowy niedostępny → D4 = NIE;
- kreacje niedostępne → D1 = NIE.

## Krok 2. Eksploracja do karty M1

1. Rozkład w czasie, po platformach, krajach i językach (P17, P10; statystyki opisowe dostarcza inżynier danych, pipeline może użyć `audit_dataset.py`).
2. Losowo wybrane 50–100 rekordów przejrzyj ręcznie; zapisz, co zaskoczyło (P17). To jest materiał do poprawy codebooka, nie do dowodzenia.
3. Szacunek prevalence wzmianki o osobie publicznej i scamu na tej próbie (P09). Przedział ufności Wilsona: `python tools/sample_size.py wilson --k ... --n ...`. Przy małej próbie przedział jest szeroki; zapisz go.
4. Koncentracja reklamodawców (P11), przybliżone ICC z danych (P12).
5. Decyzja D2: czy jest dość przypadków do planu z 05.

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

## Krok 7. Przekazanie analitykowi

Przekaż: tabelę z predykcjami i etykietami, wagami włączenia, klastrami; opis zmiennych; wyniki walidacji z CI; estymatę skali naiwną i skorygowaną; wyniki analizy błędów po warstwach i po czasie emisji (05, sekcja 5); zakres wrażliwości; ograniczenia. Analityk wdraża pełną korektę błędu pomiaru dla regresji lub modelu czasu życia [egami2025dsl] (w repozytorium jest tylko wersja uproszczona dla częstości; 05, sekcja 6).

## Lista kontrolna przed oddaniem raportu

- [ ] każdy wynik z liczbą ma odtwarzalne uruchomienie w dzienniku
- [ ] precision zawsze razem z prevalence
- [ ] CI przez bootstrap po klastrach
- [ ] zakres po konfiguracjach, nie jedna liczba
- [ ] ograniczenia z 06 przeniesione do preprintu
- [ ] użycie AI opisane (09)
