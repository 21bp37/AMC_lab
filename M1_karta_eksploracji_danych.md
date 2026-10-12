# M1. Karta eksploracji danych

**Temat:** Oszustwa z deepfake'ami.
**Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

Oznaczenia: `{{Pnn: ...}}` to miejsce do uzupełnienia po otrzymaniu danych lub po decyzji wskazanej osoby; w nawiasach kwadratowych podano właściciela: **[LEAD]**, **[INŻ. DANYCH]**, **[PIPELINE]**, **[ANALITYK]**. Odwołania w nawiasach kwadratowych, np. [tiktokcca], odpowiadają pozycjom w sekcji „Źródła” na końcu.

## 1. Pytanie badawcze i hipoteza

**Pytanie badawcze.** Jaka jest mediana czasu życia reklam typu deepfake scam i jak kształtuje się ich dzienna intensywność wyświetleń (stosunek skumulowanych impresji do liczby aktywnych dni)?

**Hipoteza.** Mediana czasu życia reklam typu deepfake scam nie przekracza 2 dni kalendarzowych, lecz mimo tak krótkiej obecności charakteryzują się one skrajnie wysoką dzienną intensywnością wyświetleń (ponad 50% z nich osiąga szacunkowo 25 tys. impresji na dzień aktywności), co jest zgodne z taktyką agresywnego budżetu startowego (*burst-and-burn*).

**Parametry.** Wartości liczbowe mogą się jeszcze zmienić, dlatego są parametrami analizy:

| Parametr | Wartość | Znaczenie |
|---|---|---|
| T_L | 2 dni kalendarzowe | człon o czasie życia: mediana L ≤ T_L |
| T_I | 25 000 na dzień (jednostka: impresje w hipotezie; dostępna miara to unikalni użytkownicy, zob. P33) | człon o intensywności: reklama ma „wysoką intensywność”, gdy I ≥ T_I |
| p_min | 50% | człon o intensywności: udział takich reklam jest większy niż p_min |

**Definicje wielkości mierzonych.**
- **Czas życia L** = liczba dni kalendarzowych od pierwszego do ostatniego dnia emisji, włącznie z oboma (`delivery_stop − delivery_start + 1`); reklama z jednego dnia ma L = 1. Konwencja „włącznie” wymaga potwierdzenia: {{P28: konwencja liczenia dni oraz traktowanie reklam wciąż aktywnych i rozpoczętych przed oknem źródła | zależy od: P06, P03 | domyślnie: brak}} **[LEAD / INŻ. DANYCH]**.
- **Dzienna intensywność I** = zasięg za okres emisji / L. Z próbki pilotażowej wynika, że jedyna dostępna miara to **liczba unikalnych użytkowników, którzy zobaczyli reklamę (`unique_users_seen`), podana jako przedział** (np. „400K–500K”), a nie liczba wyświetleń (impresji). I jest więc średnią dzienną liczbą unikalnych użytkowników, liczoną dla dolnej i górnej granicy przedziału. Czy hipoteza i próg 25 tys. odnoszą się do tej miary: {{P33: miara intensywności (unikalni użytkownicy zamiast impresji) i obsługa przedziałów | zależy od: lead, P06 | domyślnie: brak}} **[LEAD]**.
- **Hipoteza jest jedna** i ma dwie składowe, które sprawdzamy na tej samej populacji: (a) mediana L ≤ T_L, co jest równoważne temu, że co najmniej połowa reklam ma L ≤ T_L; (b) więcej niż połowa reklam ma I ≥ T_I. Obie składowe dotyczą udziału reklam w populacji badanej, co upraszcza dobór liczebności i wnioskowanie (sekcja 5).
- **Populacja badana:** reklamy spełniające jednocześnie kryterium scamu i podejrzenia deepfake'a (sekcja 5). Czy populacja jest zawężona do deepfake'ów z wizerunkiem osoby publicznej (jak w pytaniu projektowym), czy obejmuje wszystkie deepfake scamy: {{P30: zawężenie populacji do wizerunku osoby publicznej | zależy od: lead, D1 | domyślnie: brak}} **[LEAD]**.
- **Reguła rozstrzygnięcia hipotez** (co uznajemy za wsparcie hipotezy, w tym przypadku, gdy spełniona jest tylko jedna jej składowa; np. położenie przedziału ufności względem progów): {{P32: reguła decyzyjna dla hipotezy | zależy od: lead, analityk, P13 | domyślnie: brak}} **[LEAD / ANALITYK]**.

**Zastrzeżenie interpretacyjne.** Źródło nie udostępnia wartości godzinowych ani dziennych, tylko zsumowany zasięg (unikalni użytkownicy, w przedziale) za okres emisji. Wysoka średnia intensywność przy krótkim życiu jest zgodna z taktyką *burst-and-burn*, ale jej nie dowodzi, bo taktyka dotyczy rozkładu ruchu w czasie, którego nie obserwujemy. Krótkie życie reklamy może wynikać również z szybkiego usuwania jej przez platformę. Dlatego wniosek o taktyce formułujemy jako „zgodny z danymi”, a nie „potwierdzony”.

## 2. Źródła danych

| Źródło | Co daje | Dostęp i warunki | Stan |
|---|---|---|---|
| **TikTok Commercial Content Library i Commercial Content API** (główne) | kreacje reklam, daty emisji (publikacja, „last seen date”), liczba osób, które zobaczyły reklamę, targetowanie, metadane reklamy i reklamodawcy; dane z UE [tiktokcca; tiktokcclnews2023] | biblioteka publiczna; API dla publiczności i badaczy po wniosku (konto TikTok for Developers, deklarowana odpowiedź w 2 dni robocze); dane dostępne do roku od ostatniego wyświetlenia reklamy | znaczenie pól, prawo zapisu kreacji i warunki publikacji: {{P07: macierz legalności \| zależy od: lektura Developer Terms of Service \| domyślnie: brak}} **[INŻ. DANYCH]** |
| Źródło dodatkowe (opcjonalne) | zespół może włączyć inną bibliotekę reklam | do ustalenia | {{P07: źródło dodatkowe \| zależy od: zespół \| domyślnie: brak}} |

**Zasady:** dane pochodzą wyłącznie z legalnych źródeł, zgodnie z regulaminami; nie stosujemy scrapowania. Dane o reklamach nie trafiają do repozytorium; opis zbioru zawiera data statement: {{P08: data statement | zależy od: P07 | domyślnie: brak}} **[INŻ. DANYCH]**.

**Pola ustalone na próbce pilotażowej** (plik JSON z 44 reklamami TikToka; `python tools/load_tiktok_json.py`):

| Potrzebne do pytania | Co jest w źródle | Uwagi |
|---|---|---|
| Początek i koniec emisji | `first_shown_date`, `last_shown_date` (RRRRMMDD) | Wszystkie reklamy mają obie daty, także te ze statusem „active”; status nie oznacza, że reklama wciąż się wyświetla |
| Zasięg | `unique_users_seen` jako **przedział** (np. „1K–10K”, „1M–10M”), rozbicie po krajach, wieku i płci | To unikalni użytkownicy, nie wyświetlenia; 24 z 44 przedziałów ma rozpiętość co najmniej 5-krotną |
| Usunięcie przez platformę | `status` = „inactive” oraz „Removed from TikTok due to a violation of TikTok's terms” | 8 z 44 reklam; zmienna do analizy wrażliwości, nie definicja scamu |
| Kreacje | adresy wideo i obrazów (podpisane, wygasające linki) | Są dla reklam aktywnych (35 wideo, 20 obrazów); **dla 8 usuniętych brak jakichkolwiek mediów** |
| Reklamodawca | `business_id`, nazwa, „paid for by” | **Puste dla 8 usuniętych reklam** |
| Tekst reklamy, adres docelowy, język | brak (pole języka w targetowaniu puste dla 43 z 44) | Język i treść trzeba ustalać z kreacji |
| Targetowanie | kraje, grupy wieku i płci, liczba osiągalnych użytkowników | We wszystkich reklamach wszystkie grupy wieku i płci są włączone |

Te ustalenia pochodzą z jednej próbki; zakres pól w pełnym pobraniu i warunki zapisu danych potwierdza inżynier danych: {{P07: macierz legalności | zależy od: lektura Developer Terms of Service | domyślnie: brak}} **[INŻ. DANYCH]**.

## 3. Zakres próby

- **Jednostka analizy:** reklama w źródle (`ad_id`), po deduplikacji kreacji (`creative_id`); reklamodawca jest klastrem (reklamy jednego reklamodawcy nie są niezależne).
- **Zakres geograficzny:** UE (zakres danych źródła).
- **Okno dat:** w próbce pilotażowej pierwszy dzień emisji od 2025-09-30 do 2026-10-03, ostatni dzień od 2025-11-04 do 2026-10-11; dane pobrane 2026-10-12. Okno dla pełnego zbioru: {{P01: okno dat pełnego pobrania | zależy od: macierz legalności, dostępność | domyślnie: brak}} **[INŻ. DANYCH]**.
- **Języki:** źródło nie podaje języka reklamy; ustalamy go z kreacji (kodowanie). Reklamy z próbki są dostarczane niemal wyłącznie do Polski (36 z 44), pozostałe do kilkunastu krajów Europy z bardzo małym zasięgiem.
- **Ramka (zbiór reklam kandydujących):** sposób jej zbudowania (kryteria, zapytania po słowach kluczowych lub reklamodawcach) wyznacza, których reklam dotyczą wyniki: {{P29: budowa ramki | zależy od: źródło, P01 | domyślnie: brak}} **[INŻ. DANYCH / LEAD]**. Wymaganie: ramka nie może być zbudowana na wyniku annotatora ocenianego ani na kryterium „scam”.
- **Liczebność:** próbka pilotażowa to 44 reklamy (10 + 10 + 10 + 10 + 4 z zapytań: „inwestycja”, „zarobki”, „Orlen”, „KGHM”, „Brzoska”), 14 rozpoznawalnych reklamodawców i 8 reklam bez reklamodawcy. Liczebność pełnego zbioru i deduplikacja kreacji: {{P02: liczba reklam, kreacji i reklamodawców w pełnym zbiorze | zależy od: pełne pobranie | domyślnie: nieznana}} **[INŻ. DANYCH]**.
- **Zbiór cenzurowany:** obserwujemy tylko reklamy, które źródło zachowało; reklamy wciąż aktywne w dniu pobrania mają nieznany koniec emisji. Data pobrania jest zmienną w zbiorze.

## 4. Wyniki wstępnej eksploracji

Poniższe liczby pochodzą z **próbki pilotażowej: 44 reklamy z 5 zapytań po słowach kluczowych, pobrane 2026-10-12**. To jest cała ramka, **bez klasyfikacji**: nie wiadomo jeszcze, które reklamy są scamem ani deepfake'iem (prevalence: P09), więc liczby **nie testują hipotezy** i nie opisują populacji badanej. Wykonano je narzędziami `tools/load_tiktok_json.py`, `tools/audit_dataset.py` i `tools/outcomes.py`.

| Wynik | Wartość w próbce |
|---|---|
| Czas życia L (dni, włącznie) | mediana 10 (dolna mediana z `outcomes.py`; klasycznie 10,5), 95% CI 2–61; kwartyle 2 i 38; maksimum 367; L ≤ 2 ma 16 z 44 reklam (36%, 95% CI 18–73%): 3 reklamy z L = 1, 13 z L = 2, żadnej z L = 3 |
| Status | 36 „active”, 8 „inactive” (usunięte przez TikTok); wszystkie usunięte mają L = 1–2 dni i zasięg „1K–10K” (7 reklam) lub „10K–100K” (1 reklama) |
| Reklamy „active” a faktyczna emisja | tylko 9 z 36 ma ostatni dzień emisji w ciągu 7 dni przed pobraniem; 24 z 36 ma ostatni dzień starszy niż 30 dni, więc status „active” nie wskazuje reklam wciąż emitowanych |
| Zasięg (unikalni użytkownicy) | w przedziałach; mediana środków przedziałów 300 tys.; 12 reklam „1K–10K”, 10 reklam „1M–10M” |
| Dzienna intensywność I (unikalni użytkownicy na dzień) | udział reklam z I ≥ 25 tys.: 36% (dolne granice przedziałów), 41% (środki; 95% CI 9–69%), 43% (górne granice); dolna mediana I: 5,2 tys. (dolne granice), 6,7 tys. (środki), 10,0 tys. (górne granice) |
| Związek L i zasięgu | korelacja rangowa Spearmana 0,74: dłużej emitowane reklamy mają większy zasięg |
| Konwencja liczenia dni | mediana L wynosi 10,5 przy liczeniu włącznie i 9,5 bez dnia pierwszego (klasyczna mediana); liczba reklam z L ≤ 2 jest ta sama (16) w obu konwencjach, bo nie ma reklam z L = 3 |
| Reklamodawcy | 14 rozpoznawalnych (11 z jedną reklamą), 3 największych ma 25 z 44 reklam (57%), jeden ma 10; 8 reklam bez reklamodawcy (wszystkie usunięte) |
| Dostępność kreacji | 35 reklam z wideo, 20 z obrazem (19 z obydwoma), 8 bez żadnych mediów (wszystkie usunięte) |
| Zapytania a zawartość | wszystkie 10 reklam z zapytania „Orlen” pochodzi od reklamodawcy z nazwą zawierającą to słowo (prawdopodobnie reklamy oficjalne); 8 z 10 reklam z zapytania „KGHM” to reklamy usunięte; zapytania po nazwach mieszają reklamy legalne i podejrzane |

**Co z tego wynika dla projektu.**
1. Zasięg to unikalni użytkownicy w przedziałach, więc hipotezę o „impresjach” trzeba doprecyzować (P33); próg 25 tys. na dzień wypada wewnątrz przedziałów dla części reklam (wynik 36–43%).
2. Reklamy usunięte przez TikTok nie mają kreacji ani reklamodawcy, więc **nie da się ich zaklasyfikować jako deepfake ani przypisać do klastra**. To są prawdopodobnie najkrócej żyjące reklamy (wszystkie L ≤ 2), więc populacja możliwa do zakodowania z kreacji będzie obciążona w stronę reklam dłużej żyjących (06, R23).
3. Mediana czasu życia w ramce jest daleko od 2 dni, ale to cała ramka z dużym udziałem reklam legalnych; dopiero klasyfikacja populacji pokaże, czy hipoteza ma sens.
4. Próbka jest mała (44 reklamy, 14 reklamodawców), a trzech reklamodawców ma 57% reklam, więc przedziały po klastrach są szerokie (np. 95% CI mediany L w ramce: 2–61 dni).

Pozostałe wyniki wpisuje pipeline po pilotażu kodowania:

| Wynik | Gdzie | Właściciel |
|---|---|---|
| Prevalence scamu i podejrzenia deepfake'a w ręcznie przejrzanej próbie 50–100 reklam, z przedziałem ufności | {{P09: prevalence \| zależy od: dane, pilotaż \| domyślnie: brak}} | [PIPELINE] |
| Notatki z ręcznego przeglądu (co zaskoczyło, co poprawić w codebooku) | {{P23: notatki i przykłady z pilotażu \| zależy od: dane \| domyślnie: brak}} | [PIPELINE] |

## 5. Plan pomiaru zjawiska

**Co mierzymy i skąd.**

| Wielkość | Skąd | Jak |
|---|---|---|
| Czas życia L, skumulowane wyświetlenia | metadane źródła | liczone z tabeli; annotatorzy ich nie widzą |
| Dzienna intensywność I | metadane źródła | I = zasięg (unikalni użytkownicy, przedział) / L |
| Przynależność do populacji (scam, podejrzenie deepfake'a) | kodowanie annotatorów na kreacjach i tekście | codebook; walidacja na gold standardzie |
| Warstwy: typ scamu, obecność osoby publicznej | kodowanie annotatorów | codebook |

**Populacja „deepfake scam”.** Reklama należy do populacji, gdy (1) jest scamem oraz (2) kodowanie wskazuje podejrzenie deepfake'a (`media_synthetic_suspected` = `yes` lub `suspected`, z nazwaną przesłanką: wadliwy obraz, niezgodność ruchu warg i głosu, nienaturalny głos lub oznaczenie jako treść wygenerowana). Deepfake jest tu **podejrzewany, nie ustalany**; analiza wrażliwości obejmuje definicje „tylko `yes`” i „`yes` lub `suspected`”. Rozpoznawania twarzy nie stosujemy (dane biometryczne z art. 9 ust. 1 RODO). Scam jest etykietowany **wyłącznie na podstawie oceny annotatorów** według jawnej reguły codebooka (`scam_judgement`, `scam_type`), **niezależnie od decyzji platformy**: gdyby scam oznaczał „usunięta przez platformę”, czas życia byłby z definicji czasem do usunięcia i hipoteza byłaby spełniona z konstrukcji. Nie używamy zewnętrznej listy scamów, więc etykieta nie ma niezależnego sprawdzianu.

**Instrument i walidacja.**
1. **Codebook** z pilotażem w dwóch rundach (30–50 reklam) i zamrożeniem. Zgodność annotatorów mierzymy współczynnikiem Krippendorffa α (≥ 0,80 wiarygodne, 0,667–0,80 tylko wnioski wstępne, poniżej odrzucić [krippendorff2004]), z prevalence i zgodnością pozytywną/negatywną. Wyniki pilotażu: {{P13: α per zmienna z przedziałem ufności | zależy od: pilotaż | domyślnie: brak}} **[PIPELINE]**.
2. **Gold standard:** losowanie dwufazowe warstwowe z limitem na reklamodawcę i zapisem prawdopodobieństw włączenia; kodowanie na ślepo przez annotatorów referencyjnych. Skład: {{P21: annotatorzy referencyjni (ilu, którzy) | zależy od: lead | domyślnie: nieznany}} **[LEAD]**.
3. **Annotator oceniany** (model lub inna metoda wybrana przez pipeline) jest oceniany względem gold standardu: precision razem z prevalence, recall, F1, przedziały ufności bootstrapem po reklamodawcach [cameron2015], wrażliwość na parafrazy promptu i wersję modelu raportowana jako zakres [baumann2025]. Wybrany annotator oceniany: {{P15: nazwa, wersja, parametry | zależy od: D1, D5, P20 | domyślnie: brak}} **[PIPELINE]**.
4. **Wyniki:** mediana L i udział reklam z I ≥ T_I liczone na populacji badanej z wagami 1/prawdopodobieństwo włączenia i przedziałami po klastrach. Błąd klasyfikacji populacji uwzględniamy według zasad korygowania predykcji modelu [egami2025dsl]; w repozytorium jest wersja uproszczona, a modele przeżycia dla reklam wciąż aktywnych i pełną korektę wdraża analityk: {{P12: ICC i deff; metoda dla czasu życia | zależy od: dane z etykietami | domyślnie: nie wdrożono}} **[ANALITYK]**.
5. **Reklamy wciąż aktywne:** podajemy pasmo mediany (reklamy aktywne jako obserwowane do dnia pobrania vs jako nieskończone); jeśli pasmo obejmuje T_L, składowa hipotezy o czasie życia jest nierozstrzygnięta.

**Analiza błędów.** (a) Macierz pomyłek dla klasy „deepfake scam” i jej składników. (b) Błąd w podziale na język, typ scamu, obecność osoby publicznej, typ kreacji, reklamodawcę i przedział czasu emisji. (c) Porównanie rozkładów L i I u prawdziwych pozytywów, fałszywych pozytywów i fałszywych negatywów: jeśli błędy zależą od czasu życia lub intensywności, korekta globalna nie wystarcza i wnioski opatrujemy zastrzeżeniem. (d) Wrażliwość na definicję populacji, konwencję liczenia dni i granice przedziałów wyświetleń.

**Liczebność (dla obu składowych hipotezy).** Precyzja zależy od liczby reklam w populacji badanej. Połowa szerokości 95% przedziału Wilsona dla udziału bliskiego 0,5: 60 reklam ±0,12, 100 reklam ±0,10, 250 reklam ±0,06, 400 reklam ±0,05 (przy niezależnych obserwacjach; klastrowanie poszerza przedział o czynnik √deff). Jeśli prawdziwy udział jest bliski progu 50%, potrzeba kilkuset reklam; jeśli wyraźnie dalej, wystarczy kilkadziesiąt. Docelowa liczba reklam w populacji (heurystyka własna: co najmniej 60): {{P09: liczba reklam w populacji osiągalna w próbie | zależy od: prevalence, D2 | domyślnie: 60}} **[PIPELINE]**.

## 6. Ograniczenia danych i źródła błędu

| Ograniczenie / źródło błędu | Skutek dla wniosków | Co robimy |
|---|---|---|
| **Dane zagregowane**: suma wyświetleń za okres, bez rozkładu godzinowego czy dziennego | Intensywność to średnia; nie da się potwierdzić taktyki *burst-and-burn* | Wniosek formułowany jako „zgodny z”; wykorzystamy rozbicie po dniach, jeśli źródło je zwraca |
| **Zależność L i I**: I = suma / L, więc dla L = 1 intensywność równa jest całej sumie | Krótkie reklamy mają mechanicznie wyższą i bardziej zmienną I; konwencja liczenia dni zmienia wniosek przy progu 2 dni | Jawna konwencja; raportujemy także skumulowane wyświetlenia; analiza wrażliwości |
| **Definicja pola wyświetleń**: osoby czy wyświetlenia, wartość czy przedział | Niepewna klasyfikacja względem progu 25 tys. | Ustalenie znaczenia pola; dla przedziałów udział policzony dla dolnej i górnej granicy |
| **Reklamy usunięte przez TikTok nie mają kreacji ani reklamodawcy** (8 z 44, wszystkie L ≤ 2) | Nie da się ich zaklasyfikować jako deepfake ani przypisać do klastra; populacja możliwa do zakodowania jest obciążona w stronę reklam dłużej żyjących, co może zawyżać medianę L | Jawne zastrzeżenie; analiza wrażliwości z założeniem skrajnym (usunięte reklamy dodane do populacji z ich L i zasięgiem); pytanie do inżyniera danych, czy kreacje usuniętych reklam da się uzyskać legalnie |
| **Zasięg to unikalni użytkownicy w przedziałach**, nie impresje | Intensywność jest niedoszacowana względem impresji (jeden użytkownik może zobaczyć reklamę wielokrotnie); przedział rozpiętości 10× zostawia udział z I ≥ 25 tys. nierozstrzygnięty (36–43% w ramce) | Obliczenia dla dolnej i górnej granicy przedziału; decyzja leada o mierze (P33) |
| **Status „active” nie oznacza emisji w toku** (24 z 36 reklam „active” miało ostatni dzień emisji ponad 30 dni przed pobraniem) | Nie da się odczytać cenzurowania ze statusu | Cenzurowanie definiowane przez datę ostatniej emisji względem daty pobrania (P28) |
| **Brak tekstu reklamy i adresu docelowego** w danych | Scam i język trzeba ustalać wyłącznie z kreacji (wideo, obraz) | Kodowanie z kreacji; dostępność kreacji jest warunkiem wykonalności |
| **Cenzurowanie**: reklamy wciąż aktywne; dane tylko do roku od ostatniego wyświetlenia; reklamy usunięte mogą znikać z biblioteki | Zniekształcony czas życia (mediana może być zawyżona lub zaniżona) | Pasmo mediany; data pobrania jako zmienna; wnioski ograniczone do reklam widocznych w źródle |
| **Egzekwowanie platformy**: czas życia zależy od tego, jak szybko platforma usuwa reklamy | Krótkie życie nie musi być decyzją reklamodawcy | Scam etykietowany niezależnie od usunięcia; `platform_removal` jako zmienna wrażliwości |
| **Deepfake tylko podejrzewany** i jest kryterium populacji | Populacja może zawierać reklamy bez syntezy i pomijać reklamy z syntezą | Przesłanka nazwana w kodowaniu; α i odsetek „niepewne”; wrażliwość na definicję populacji |
| **Brak niezależnego dowodu scamu**: etykieta pochodzi wyłącznie z oceny annotatorów | Część reklam uznanych za scam może być legalna lub odwrotnie; błąd etykiety nie jest mierzalny wprost | Jawna reguła w codebooku; dwie rundy pilotażu; α z prevalence; adjudykacja trzeciej osoby; wartość `unclear` zamiast zgadywania |
| **Mała liczba reklam w populacji** (rzadka klasa) | Szerokie przedziały ufności; paradoks kappa maskuje jakość kodowania | Losowanie z nadpróbkowaniem; klasy z małą liczbą pozytywów jako eksploracyjne |
| **Klastrowanie** reklamodawców (w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [gendigital2026]) | Zawyżona pewność wniosków | Bootstrap po reklamodawcach; limit reklam na reklamodawcę w losowaniu |
| **Ramka zależna od zapytań** | Wyniki dotyczą ramki, nie wszystkich reklam | Opis ramki w data statement; wyniki raportowane względem ramki |
| **Dane osobowe i regulamin**: wizerunek i nazwiska osób publicznych; warunki API | Niemożność użycia lub publikacji danych | Bez rozpoznawania twarzy; identyfikatory osób tylko w plikach roboczych; macierz legalności przed pracą na danych |
| **Wrażliwość instrumentu** na prompt i wersję | Niepowtarzalność | Zamrożenie codebooka i zbioru testowego; dziennik uruchomień; wyniki jako zakres |

Pełny rejestr z prawdopodobieństwem, wpływem i wskaźnikami z danych znajduje się w dokumencie 06.

## 7. Wykonalność w skali kursu

Temat jest wykonalny, jeśli spełnione są warunki sprawdzane przed pracą na danych i po eksploracji:

| Pytanie | Co wiemy | Rozstrzygnięcie |
|---|---|---|
| Czy jest legalne źródło? | Tak, TikTok Commercial Content Library / API [tiktokcca]; warunki zapisu i publikacji do sprawdzenia | **[INŻ. DANYCH]**: P07 |
| Czy są daty początku i końca emisji oraz zasięg? | **Tak, w próbce pilotażowej:** pierwszy i ostatni dzień emisji u wszystkich 44 reklam; zasięg jako przedział unikalnych użytkowników (nie impresje: P33); status usunięcia reklamy | **[INŻ. DANYCH]**: potwierdzenie na pełnym zbiorze i w dokumentacji; **[LEAD]**: P33; D6 = TAK dla czasu życia, dla intensywności po decyzji P33 |
| Czy są dostępne kreacje (wideo) do wskazania deepfake'a? | **Częściowo:** są dla reklam aktywnych (35 wideo z 36), **brak dla 8 reklam usuniętych przez TikTok**, które są najkrótsze; prawo do przetwarzania nieustalone | **[INŻ. DANYCH]**: P04, P07; usunięte reklamy wypadają z populacji (R23). Jeśli kreacji nie wolno przetwarzać, D1 = NIE: populacji „deepfake scam” nie da się zidentyfikować i lead zawęża pytanie (P30) |
| Czy w ramce jest dość reklam deepfake scam? | Nieznane; zależy od prevalence | **[PIPELINE]**: P09, D2 |
| Czy da się wiarygodnie kodować podejrzenie deepfake'a? | Brak równorzędnej walidacji w literaturze dla tego zadania; spodziewana niska zgodność | **[PIPELINE]**: pilotaż, P13, D3 |
| Czy da się skodować wystarczającą liczbę reklam w czasie kursu? | Ręczne kodowanie próby z estymacją korygowaną jest wariantem zapasowym | **[PIPELINE]**: koszt i limity {{P16: koszt i limity przetwarzania \| zależy od: P02, P15 \| domyślnie: nieznane}} |

**Wynik negatywny o wykonalności lub pomiarze jest pełnoprawnym wynikiem projektu** (zasady kursu): jeśli któryś warunek nie zostanie spełniony, rezultatem jest uzasadniony wniosek o tym, czego z danych publicznych nie da się zmierzyć, wraz z opisem danych, które byłyby potrzebne.

## 8. Otwarte decyzje i podział odpowiedzialności

| Właściciel | Odpowiada za | Otwarte miejsca |
|---|---|---|
| **[LEAD]** | pytanie, hipoteza, progi, miara intensywności, reguła decyzyjna, skład annotatorów, stan wiedzy | P28 (z inż. danych), P30, P32, P33, P21, P31 |
| **[INŻ. DANYCH]** | źródła, legalność, pola, ramka, statystyki opisowe | P01, P02, P04, P07, P08, P29 (pełne pobranie); P06, P10, P11, P17 wpisane z próbki pilotażowej do potwierdzenia na pełnym zbiorze |
| **[PIPELINE]** | codebook, gold standard, walidacja annotatora ocenianego, analiza błędów | P09, P13, P15, P16, P23 |
| **[ANALITYK]** | modele przeżycia, korekty końcowe, wnioskowanie | P12, P32 (z leadem) |

## 9. Stan wiedzy i uzasadnienie wartości badania

{{P31: stan wiedzy, luka badawcza, uzasadnienie wartości badania | zależy od: lead | domyślnie: brak}} **[LEAD]**

## Źródła

- TikTok for Developers. *Commercial Content API*. https://developers.tiktok.com/products/commercial-content-api [tiktokcca]
- TikTok Newsroom (2023). *TikTok's Research API and Commercial Content Library*. https://newsroom.tiktok.com/tiktoks-research-api-and-commercial-content-library [tiktokcclnews2023]
- Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage. [krippendorff2004]
- Cameron, A. C., Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. *Journal of Human Resources* 50(2), 317–372. [cameron2015]
- Egami, N., Hinck, M., Stewart, B. M., Wei, H. Using large language model annotations for the social sciences: A general framework of using predicted variables in downstream analyses. [egami2025dsl]
- Baumann, J. i in. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv:2509.08825. [baumann2025]
- Gen Digital, Gen Threat Labs. *The Scam Ad Machine*. Raport branżowy. [gendigital2026]

Statusy weryfikacji źródeł (które otwarto i potwierdzono, a które do sprawdzenia przed cytowaniem w preprincie) są w `07_bibliografia.md`.
