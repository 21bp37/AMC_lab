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
| T_I | 25 000 wyświetleń na dzień | człon o intensywności: reklama ma „wysoką intensywność”, gdy I ≥ T_I |
| p_min | 50% | człon o intensywności: udział takich reklam jest większy niż p_min |

**Definicje wielkości mierzonych.**
- **Czas życia L** = liczba dni kalendarzowych od pierwszego do ostatniego dnia emisji, włącznie z oboma (`delivery_stop − delivery_start + 1`); reklama z jednego dnia ma L = 1. Konwencja „włącznie” wymaga potwierdzenia: {{P28: konwencja liczenia dni oraz traktowanie reklam wciąż aktywnych i rozpoczętych przed oknem źródła | zależy od: P06, P03 | domyślnie: brak}} **[LEAD / INŻ. DANYCH]**.
- **Dzienna intensywność I** = skumulowane wyświetlenia za okres emisji / L. Źródło podaje sumę za okres, więc I jest wartością średnią.
- **Hipoteza jest jedna** i ma dwie składowe, które sprawdzamy na tej samej populacji: (a) mediana L ≤ T_L, co jest równoważne temu, że co najmniej połowa reklam ma L ≤ T_L; (b) więcej niż połowa reklam ma I ≥ T_I. Obie składowe dotyczą udziału reklam w populacji badanej, co upraszcza dobór liczebności i wnioskowanie (sekcja 5).
- **Populacja badana:** reklamy spełniające jednocześnie kryterium scamu i podejrzenia deepfake'a (sekcja 5). Czy populacja jest zawężona do deepfake'ów z wizerunkiem osoby publicznej (jak w pytaniu projektowym), czy obejmuje wszystkie deepfake scamy: {{P30: zawężenie populacji do wizerunku osoby publicznej | zależy od: lead, D1 | domyślnie: brak}} **[LEAD]**.
- **Reguła rozstrzygnięcia hipotez** (co uznajemy za wsparcie hipotezy, w tym przypadku, gdy spełniona jest tylko jedna jej składowa; np. położenie przedziału ufności względem progów): {{P32: reguła decyzyjna dla hipotezy | zależy od: lead, analityk, P13 | domyślnie: brak}} **[LEAD / ANALITYK]**.

**Zastrzeżenie interpretacyjne.** Źródło nie udostępnia wartości godzinowych ani dziennych, tylko zsumowaną liczbę wyświetleń za okres. Wysoka średnia intensywność przy krótkim życiu jest zgodna z taktyką *burst-and-burn*, ale jej nie dowodzi, bo taktyka dotyczy rozkładu ruchu w czasie, którego nie obserwujemy. Krótkie życie reklamy może wynikać również z szybkiego usuwania jej przez platformę. Dlatego wniosek o taktyce formułujemy jako „zgodny z danymi”, a nie „potwierdzony”.

## 2. Źródła danych

| Źródło | Co daje | Dostęp i warunki | Stan |
|---|---|---|---|
| **TikTok Commercial Content Library i Commercial Content API** (główne) | kreacje reklam, daty emisji (publikacja, „last seen date”), liczba osób, które zobaczyły reklamę, targetowanie, metadane reklamy i reklamodawcy; dane z UE [tiktokcca; tiktokcclnews2023] | biblioteka publiczna; API dla publiczności i badaczy po wniosku (konto TikTok for Developers, deklarowana odpowiedź w 2 dni robocze); dane dostępne do roku od ostatniego wyświetlenia reklamy | znaczenie pól, prawo zapisu kreacji i warunki publikacji: {{P07: macierz legalności \| zależy od: lektura Developer Terms of Service \| domyślnie: brak}} **[INŻ. DANYCH]** |
| Źródło dodatkowe (opcjonalne) | zespół może włączyć inną bibliotekę reklam | do ustalenia | {{P07: źródło dodatkowe \| zależy od: zespół \| domyślnie: brak}} |

**Zasady:** dane pochodzą wyłącznie z legalnych źródeł, zgodnie z regulaminami; nie stosujemy scrapowania. Dane o reklamach nie trafiają do repozytorium; opis zbioru zawiera data statement: {{P08: data statement | zależy od: P07 | domyślnie: brak}} **[INŻ. DANYCH]**.

**Znane ograniczenie pól.** Strona API mówi o „liczbie osób, które zobaczyły reklamę”, a analiza zakłada impresje (wyświetlenia). To, czy pole oznacza wyświetlenia czy unikatowych odbiorców, czy jest liczbą czy przedziałem, i czy jest sumą za okres, ustala inżynier danych: {{P06: znaczenie pól czasu emisji i wyświetleń | zależy od: oficjalna dokumentacja źródła | domyślnie: nieznane}} **[INŻ. DANYCH]**.

## 3. Zakres próby

- **Jednostka analizy:** reklama w źródle (`ad_id`), po deduplikacji kreacji (`creative_id`); reklamodawca jest klastrem (reklamy jednego reklamodawcy nie są niezależne).
- **Zakres geograficzny:** UE (zakres danych źródła).
- **Okno dat i języki:** {{P01: okno dat i języki próby | zależy od: macierz legalności, dostępność | domyślnie: kraje UE (zakres źródła); okno i języki brak}} **[INŻ. DANYCH]**.
- **Ramka (zbiór reklam kandydujących):** sposób jej zbudowania (kryteria, zapytania po słowach kluczowych lub reklamodawcach) wyznacza, których reklam dotyczą wyniki: {{P29: budowa ramki | zależy od: źródło, P01 | domyślnie: brak}} **[INŻ. DANYCH / LEAD]**. Wymaganie: ramka nie może być zbudowana na wyniku annotatora ocenianego ani na kryterium „scam”.
- **Liczebność:** {{P02: liczba reklam, kreacji i reklamodawców po deduplikacji | zależy od: pobranie danych | domyślnie: nieznana}} **[INŻ. DANYCH]**.
- **Zbiór cenzurowany:** obserwujemy tylko reklamy, które źródło zachowało; reklamy wciąż aktywne w dniu pobrania mają nieznany koniec emisji. Data pobrania jest zmienną w zbiorze.

## 4. Wyniki wstępnej eksploracji

Eksploracja zostanie wykonana po otrzymaniu danych; poniższa tabela wskazuje, co i kto wpisuje. Narzędzia: `python tools/audit_dataset.py dane.csv` (statystyki opisowe i kontrola schematu) oraz `python tools/outcomes.py dane.csv` (wstępne rozkłady L i I bez korekty błędu klasyfikacji).

| Wynik | Gdzie | Właściciel |
|---|---|---|
| Rozkład reklam w czasie, wstępne rozkłady L i I, udział reklam bez daty końca | {{P17: rozkład reklam w czasie oraz wstępne rozkłady L i I \| zależy od: dane \| domyślnie: brak}} | [INŻ. DANYCH] |
| Rozkład języków i udział polskich reklam | {{P10: rozkład języków \| zależy od: dane \| domyślnie: brak}} | [INŻ. DANYCH] |
| Koncentracja reklamodawców: liczba klastrów, udział 10 największych | {{P11: liczba klastrów i udział 10 największych \| zależy od: dane \| domyślnie: brak}} | [INŻ. DANYCH] |
| Prevalence scamu i podejrzenia deepfake'a w ręcznie przejrzanej próbie 50–100 reklam, z przedziałem ufności | {{P09: prevalence \| zależy od: dane, pilotaż \| domyślnie: brak}} | [PIPELINE] |
| Notatki z ręcznego przeglądu (co zaskoczyło, co poprawić w codebooku) | {{P23: notatki i przykłady z pilotażu \| zależy od: dane \| domyślnie: brak}} | [PIPELINE] |

## 5. Plan pomiaru zjawiska

**Co mierzymy i skąd.**

| Wielkość | Skąd | Jak |
|---|---|---|
| Czas życia L, skumulowane wyświetlenia | metadane źródła | liczone z tabeli; annotatorzy ich nie widzą |
| Dzienna intensywność I | metadane źródła | I = wyświetlenia / L |
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
| Czy są daty początku i końca emisji oraz skumulowane wyświetlenia? | Strona API wymienia datę publikacji, „last seen date” i liczbę osób; znaczenie pól nieustalone | **[INŻ. DANYCH]**: P06; jeśli nie, D6 = NIE: pomiar czasu życia lub intensywności niemożliwy |
| Czy są dostępne kreacje (wideo) do wskazania deepfake'a? | Biblioteka zawiera kreacje; zakres w API i prawo przetwarzania nieustalone | **[INŻ. DANYCH]**: P04; jeśli nie, D1 = NIE: populacji „deepfake scam” nie da się zidentyfikować i lead zawęża pytanie (P30) |
| Czy w ramce jest dość reklam deepfake scam? | Nieznane; zależy od prevalence | **[PIPELINE]**: P09, D2 |
| Czy da się wiarygodnie kodować podejrzenie deepfake'a? | Brak równorzędnej walidacji w literaturze dla tego zadania; spodziewana niska zgodność | **[PIPELINE]**: pilotaż, P13, D3 |
| Czy da się skodować wystarczającą liczbę reklam w czasie kursu? | Ręczne kodowanie próby z estymacją korygowaną jest wariantem zapasowym | **[PIPELINE]**: koszt i limity {{P16: koszt i limity przetwarzania \| zależy od: P02, P15 \| domyślnie: nieznane}} |

**Wynik negatywny o wykonalności lub pomiarze jest pełnoprawnym wynikiem projektu** (zasady kursu): jeśli któryś warunek nie zostanie spełniony, rezultatem jest uzasadniony wniosek o tym, czego z danych publicznych nie da się zmierzyć, wraz z opisem danych, które byłyby potrzebne.

## 8. Otwarte decyzje i podział odpowiedzialności

| Właściciel | Odpowiada za | Otwarte miejsca |
|---|---|---|
| **[LEAD]** | pytanie, hipoteza, progi, reguła decyzyjna, skład annotatorów, stan wiedzy | P28 (z inż. danych), P30, P32, P21, P31 |
| **[INŻ. DANYCH]** | źródła, legalność, pola, ramka, statystyki opisowe | P01, P02, P04, P06, P07, P08, P10, P11, P17, P29 |
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
