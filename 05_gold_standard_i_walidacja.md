# 05. Plan gold standardu i walidacji annotatora ocenianego

Cel: wykazać (albo wykazać brak), że annotator oceniany klasyfikuje reklamy do populacji badanej (reklamy typu deepfake scam: scam oraz podejrzenie deepfake'a) z błędem, który znamy i który uwzględniamy przy szacowaniu mediany czasu życia i udziału reklam o wysokiej dziennej intensywności wyświetleń. Miara sukcesu to wiarygodny wniosek, nie wysokie F1 (zasady kursu). **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” **Pytanie badawcze (01):** jaka jest mediana czasu życia reklam deepfake scam i ich dzienna intensywność wyświetleń.
Mierzymy jakość annotatora ocenianego (O), a nie cechy reklam. Dla każdej zmiennej priorytetowej (`scam_type`, `media_synthetic_suspected`) osobna wartość jest klasą, np. `media_synthetic_suspected = yes`. Annotatorzy referencyjni kodują próbę reklam, a ich uzgodnione etykiety tworzą gold standard; reklama, której gold standard przypisuje daną wartość, jest *pozytywem* tej klasy. Annotator oceniany koduje te same reklamy, a recall to odsetek pozytywów, które też oznaczył. Liczą się oba kierunki błędu: fałszywe pozytywy wprowadzają do populacji reklamy, które nią nie są (precision), a pominięte pozytywy wypychają z niej reklamy, które do niej należą (recall); oba zniekształcają medianę czasu życia i udział reklam o wysokiej intensywności, jeśli te reklamy różnią się czasem życia lub intensywnością od reszty. Klasą o największym znaczeniu jest przynależność do populacji badanej, czyli łączne spełnienie kryteriów scamu i podejrzenia deepfake'a (wymaga D1). Poniższe wartości mówią, ile pozytywów danej klasy musi mieć gold standard, żeby ten recall zmierzyć z założoną dokładnością.

Kolejność jest wiążąca: **pilotaż, korekta codebooka, zamrożenie codebooka, losowanie, annotacja, zamrożenie gold standardu, dopiero potem pierwsze uruchomienie annotatora ocenianego na zbiorze testowym.** Zbiór rozwijania promptu i zbiór testowy są rozłączne; po obejrzeniu wyników na zbiorze testowym prompt się nie zmienia (powód: strojenie na zbiorze oceniającym zawyża jakość; wzorzec zamrożonej instrukcji i oceny na danych niewidzianych przy budowie codebooka: [@halterman2025]).

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
- Reklamodawca jest klastrem. Ruch scamowy jest skoncentrowany: w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [@gendigital2026]; to wynik dla angielskich reklam w UE i Wielkiej Brytanii, więc dla naszych danych koncentrację trzeba policzyć ({{P11: liczba klastrów i udział 10 największych | zależy od: dane | domyślnie: nieznane}}).
- Ramka jest zbiorem cenzurowanym (06, R01): obserwujemy to, co biblioteka reklam zachowała i udostępniła. Luki w bibliotece reklam opisano dla amerykańskich reklam politycznych [@edelson2020; @lepochat2022]; przeniesienie na reklamy komercyjne w UE nie jest ustalone.

## 2. Projekt próby (dwufazowe losowanie warstwowe z limitem na reklamodawcę)

Implementacja: `tools/sampling.py`. Każdy rekord w próbie ma zapisane prawdopodobieństwo włączenia i wagę 1/p.

1. **Warstwy** definiujemy wyłącznie z cech znanych przed annotacją: miesiąc, język, typ scamu z baseline'u, wynik baseline'u słownikowego (np. słowa kluczowe scamu i obecność nazwiska z listy osób publicznych), ewentualnie predykcja annotatora ocenianego, a także długość emisji i wyświetlenia z metadanych **tylko jeśli** nie wprowadzi to zależności próby od wyniku (patrz uwaga niżej). Powód: rzadką klasę (deepfake scam) trzeba nadpróbkować (losowanie proste dałoby zbyt mało pozytywów), a metody korekty błędu klasyfikatora wymagają próby ze znanymi prawdopodobieństwami [@egami2025dsl].
2. **Limit na reklamodawcę** w komórce (warstwa x reklamodawca): wartość limitu jest parametrem; wybór: {{P24: limit reklam na reklamodawcę w komórce | zależy od: rozkład reklamodawców w danych | domyślnie: heurystyka własna, bez źródła; ustaw tak, aby żaden reklamodawca nie przekraczał 5% próby}}.
3. **Nadpróbkowanie warstw z rzadką klasą** i warstwa z predykcją negatywną (żeby oszacować recall, trzeba mieć etykiety także tam, gdzie annotator oceniany mówi „nie").
4. **Uwaga:** warstwowanie po czasie życia lub intensywności jest dozwolone, bo wagi 1/p je uwzględniają, ale zmienia efektywną liczebność; annotatorzy referencyjni nadal nie widzą wartości wyniku (kodowanie na ślepo).
5. Seed, parametry i hash danych wejściowych zapisujemy w dzienniku uruchomień (`tools/run_log.py`).

Test narzędzia na danych syntetycznych: estymator Horvitza-Thompsona z wagami odtwarza prawdziwą sumę (test `TestSampling`), a limit na reklamodawcę jest respektowany.

## 3. Liczebność

Nie ma w literaturze uniwersalnej liczby. Podejście, które obronimy: liczebność wynika z docelowej szerokości przedziału ufności, jak w planowaniu badań zgodności [@donner1987; @rotondi2012]. Poniższe wartości są policzone przez `tools/sample_size.py` i dotyczą przedziałów Wilsona przy założeniu niezależności obserwacji.

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

**Rola przedziału ufności w tym projekcie.** Estymacja przedziałowa zamiast punktowej pozwala: (a) ocenić, czy annotator oceniany jest wystarczająco zgodny z gold standardem (D5), uwzględniając niepewność próby; (b) zaplanować liczebność gold standardu z docelowego marginesu błędu; (c) oznaczyć klasy o zbyt szerokim przedziale jako eksploracyjne, bez wniosków wprost; (d) unikać nadinterpretacji różnic między grupami, gdy przedziały się w dużej mierze pokrywają; (e) jawnie pokazać niepewność w karcie M1, gdzie próba jest mała. Przedział Wilsona zachowuje się poprawnie przy małych próbach i dla odsetków (recall, precision, prevalence) bliskich 0 lub 1, w odróżnieniu od przedziału normalnego (Walda), który może wychodzić poza [0, 1] i ma niedostateczne pokrycie [@brown2001].

Przy recall ≈ 0,8: ±0,10 wymaga ok. 60 pozytywów, ±0,075 ok. 109, ±0,05 ok. 245.

**Wybór docelowy (heurystyka własna, nie z literatury):** celujemy w co najmniej 60 pozytywów w każdej klasie raportowanej osobno (połowa szerokości ok. ±0,10); klasy z mniejszą liczbą raportujemy jako eksploracyjne. Liczba pozytywów, nie łączne n, decyduje o precyzji. Wartość docelowa: {{P09: liczba pozytywów osiągalna w próbie | zależy od: prevalence, D2 | domyślnie: 60 na klasę}}.

**Uzasadnienie wyboru:** przy recall ≈ 0,8 przedział Wilsona o połowie szerokości ±0,10 wymaga ok. 60 pozytywów; zawężenie do ±0,075 wymaga ok. 109, a do ±0,05 ok. 245, więc koszt ręcznej annotacji rośnie szybciej niż zysk w precyzji. Wartość ±0,10 jest decyzją zespołu (pozwala odróżnić annotatora wykrywającego większość pozytywów od pomijającego połowę), a nie wartością z literatury; metoda wyboru liczebności z docelowej szerokości przedziału pochodzi z planowania badań zgodności [@donner1987; @rotondi2012]. Rachunek zakłada niezależne obserwacje i recall 0,8; przy klastrowaniu (deff > 1) i innym recallu margines będzie szerszy, dlatego wartość weryfikujemy na danych (P09, P12).

**Liczebność dla pytań H1 i H2 (populacja badana).** Obie hipotezy sprowadzają się do udziału w populacji: H1 (mediana L ≤ T_L) jest równoważna temu, że co najmniej 50% reklam ma L ≤ T_L, a H2 mówi, że więcej niż p_min = 50% reklam ma I ≥ T_I. Precyzja zależy więc od liczby reklam *w populacji badanej* (liczby pozytywów gold standardu), a nie od łącznej liczby reklam. Połowa szerokości 95% CI Wilsona dla udziału bliskiego 0,5 (wyliczenie: `tools/sample_size.py wilson`, obserwacje niezależne):

| liczba reklam w populacji | udział 0,5 | udział 0,7 |
|---|---|---|
| 30 | ±0,168 | ±0,156 |
| 60 | ±0,123 | ±0,113 |
| 100 | ±0,096 | ±0,088 |
| 150 | ±0,079 | ±0,073 |
| 250 | ±0,062 | ±0,056 |
| 400 | ±0,049 | ±0,045 |

Znaczenie: jeśli prawdziwy udział jest bliski progu 50% (np. 0,55), przedział o połowie szerokości ±0,10 nie rozstrzygnie hipotezy; potrzeba wtedy kilkuset reklam w populacji. Jeśli udział jest wyraźnie dalej od progu (np. 0,8), wystarcza kilkadziesiąt. Przy klastrowaniu połowa szerokości rośnie o czynnik √deff (wzór niżej). Mediana czasu życia mierzonego w pełnych dniach jest zmienną dyskretną, więc przedział mediany może być bardzo wąski lub zdegenerowany (np. samo „1–2 dni”); dlatego główny wniosek formułujemy przez udział reklam z L ≤ T_L.

**Korekta na klastrowanie.** Przedziały Wilsona zakładają niezależne obserwacje. Przy klastrach efektywna liczba obserwacji jest mniejsza o efekt projektu. Wzór deff = 1 + (m − 1)·ICC (Kish; **do sprawdzenia w źródle**): dla klastrów średniej wielkości 10 i ICC = 0,1 deff = 1,9, czyli 300 reklam odpowiada ok. 158 niezależnym; dla ICC = 0,3 deff = 3,7 i ok. 81. ICC z naszych danych: {{P12: ICC i deff | zależy od: dane | domyślnie: nieznane}}. Dlatego przedziały ufności liczymy bootstrapem po klastrach (`tools/evaluation.py`), co jest zgodne z zaleceniami dla danych grupowanych [@cameron2015].

## 4. Annotacja referencyjna

- Plan zakłada co najmniej 2 niezależnych annotatorów referencyjnych, kodowanie na ślepo (codebook, zasada 2), rozstrzyganie niezgodności przez trzecią osobę lub dyskusję z zapisem decyzji. Skład: > **[LEAD – DO WYPEŁNIENIA]** {{P21: annotatorzy referencyjni (ilu, którzy) | zależy od: lead | domyślnie: nieznany}}.
- **Jeden annotator referencyjny:** zgodności R–R nie da się wtedy policzyć. Stosujemy powtórne kodowanie tej samej próby przez R1 po przerwie i w innej kolejności, liczymy α między pierwszym a drugim przejściem i zapisujemy w ograniczeniach, że mierzy to stabilność jednej osoby, a nie jednoznaczność definicji. Progi α poniżej dotyczą zgodności między annotatorami; przy jednym annotatorze zmienne raportujemy jako wstępne.
- Miara główna: **Krippendorff α** (dowolna liczba annotatorów, braki dozwolone), uzupełniająco kappa Cohena i, dla zmiennych binarnych, prevalence index, bias index oraz zgodność pozytywna i negatywna [@cicchetti1990; @byrt1993; @chen2009]. Surowej zgodności procentowej nie raportujemy jako głównej miary.
- Progi: α ≥ 0,80 wiarygodne, 0,667–0,80 tylko wnioski wstępne, poniżej 0,667 odrzucić; autor zaleca dobierać próg do kosztu błędnych wniosków, więc to konwencja, a nie prawo [@krippendorff2004].
- **Uwaga: paradoks kappa.** Symulacja (`tools/sample_size.py alpha-sim`, dwóch annotatorów, każdy z trafnością 95%, błędy niezależne, czyli założenie optymistyczne) daje oczekiwane α ≈ 0,60 przy częstości zjawiska 0,1 i ok. 0,78 przy 0,3, **niezależnie od liczby jednostek**:

| n | częstość 0,1: oczekiwane α | połowa szer. 95% CI | częstość 0,3: oczekiwane α | połowa szer. 95% CI |
|---|---|---|---|---|
| 60 | 0,585 | ±0,306 | 0,771 | ±0,170 |
| 100 | 0,608 | ±0,228 | 0,781 | ±0,132 |
| 200 | 0,606 | ±0,160 | 0,784 | ±0,091 |
| 400 | 0,604 | ±0,112 | 0,779 | ±0,066 |

Znaczenie: dla rzadkiej zmiennej niskie α może wynikać z niezrównoważenia kategorii, a nie z niskiej jakości kodowania [@feinstein1990; @cicchetti1990]. Dlatego (a) raportujemy α razem z prevalence i zgodnością pozytywną/negatywną, (b) zgodność dla zmiennych rzadkich liczymy także na podpróbie wzbogaconej o pozytywy (z zaznaczeniem, że miara dotyczy tej podpróby), (c) nie usuwamy zmiennej tylko dlatego, że α < 0,80 przy bardzo rzadkiej kategorii; patrz D3 w `10_playbook`. Ostrzeżenie: PABAK nie mierzy tego samego co kappa przy niskiej prevalence [@chen2009], więc nie zastępuje α.
- Pilotaż: 30–50 reklam, dwie rundy (02, Procedura). Wyniki: {{P13: α per zmienna z CI | zależy od: pilotaż | domyślnie: brak}}. Przy 30–50 jednostkach przedziały są bardzo szerokie (tabela powyżej); pilotaż służy do poprawiania codebooka, nie do dowodzenia wiarygodności.

## 5. Ocena annotatora ocenianego

Narzędzia: `tools/evaluation.py` (macierz pomyłek, P/R/F1 z wagami 1/p, bootstrap klastrowy), `tools/prompt_robustness.py` (wrażliwość na prompt i powtórzenie).

1. **Annotator oceniany jako kolejny annotator.** Zgodność O–gold porównujemy ze zgodnością annotatorów referencyjnych między sobą (R–R; α, kappa). O nie jest oceniany surowszym kryterium niż R. Formalna procedura uzasadniania zastąpienia annotatora przez LLM na niewielkim podzbiorze istnieje w literaturze [@calderon2025]; zastosowanie do naszych zmiennych do ustalenia po lekturze pracy.
2. **Metryki per klasa:** precision, recall, F1, prevalence, każda z 95% CI z bootstrapu po klastrach. **Precision zawsze razem z prevalence w próbie**: przy rzadkiej klasie precision spada, nawet gdy recall jest dobry (przykład niskiego precision w pracy nierecenzowanej: [@radboud2025]).
3. **Wrażliwość na konfigurację:** to samo zadanie z kilkoma parafrazami promptu, z powtórzeniami i, jeśli możliwe, z więcej niż jednym modelem; raportujemy odsetek elementów, w których etykieta się zmienia, zakres kappa między konfiguracjami i zakres prevalence. Powód: replikacja 37 zadań adnotacji z 21 badań pokazała, że konfiguracja potrafi zmienić wniosek (ok. 31% hipotez z błędnym wnioskiem dla najlepszych modeli) [@baumann2025]. Wynik końcowy raportujemy jako zakres po konfiguracjach.
4. **Analiza błędów w warstwach:** wg języka, `scam_type`, kategorii osoby, typu kreacji, reklamodawcy (klastra) oraz **przedziału czasu emisji** (reklamy krótko- i długotrwałe). Sprawdzamy, czy błędy annotatora ocenianego zależą od cech powiązanych z wynikiem (czas życia); to krytyczne, bo błąd zależny od wyniku daje obciążenie, którego korekta globalna nie usunie (R08).
5. **Wpływ na wyniki:** (a) mediana L i udział reklam z I ≥ T_I: porównanie estymaty naiwnej (na reklamach wskazanych przez O) z estymatą z gold standardu (wagi 1/p; `tools/outcomes.py`), z przedziałem po klastrach; (b) porównanie rozkładów L i I u prawdziwych pozytywów, fałszywych pozytywów i fałszywych negatywów oraz sprawdzenie, czy błąd różni się między reklamami krótko- i długotrwałymi; (c) opcjonalnie liczebność populacji (częstość klasy × liczebność ramki; `tools/estimators.py`). Obróbka cenzurowania i model czasu życia: > **[ANALITYK – DO WYPEŁNIENIA]**.
6. **Zmienna deepfake (`media_synthetic_suspected`, `media_synthetic_cue`).** Jest kryterium populacji, więc jej błąd bezpośrednio wpływa na wyniki. Oceniamy ją osobno, jako zmienną porządkową o niskiej oczekiwanej wiarygodności: α/κ między annotatorami referencyjnymi (R–R) per wartość oraz odsetek `unsure`. Gold standardem jest tu zgodna ocena R, a nie prawda o syntezie materiału, więc zgodność z gold nie dowodzi, że kreacja jest deepfake'iem (06, R19). Jeśli α < 0,667, wyniki dla populacji definiowanej tą zmienną raportujemy jako wstępne i pokazujemy wrażliwość (tylko `yes`; `yes` ∪ `suspected`; `unsure` włączone lub wyłączone); przy bardzo niskiej zgodności populacja „deepfake scam” nie jest wiarygodnie mierzalna i to jest wynik.
7. Wynik pierwszego testu: > **[PIPELINE – DO WYPEŁNIENIA]** {{P14: zgodność annotatora ocenianego z gold standardem | zależy od: pilotaż, P15 | domyślnie: brak}}. Decyzja: D5.

## 6. Korekta błędu pomiaru w analizie końcowej

Wniosek z literatury: predykcje modelu analizowane tak, jakby były obserwacjami bez błędu, dają obciążenie i nieprawidłowe przedziały ufności nawet przy dokładności powyżej 90%; metoda DSL łączy predykcje z mniejszą próbą etykiet eksperckich losowaną ze znanymi prawdopodobieństwami [@egami2025dsl].

- **Co mamy dla mediany i udziałów:** `tools/outcomes.py` (L, I, ważona mediana, ważone udziały, pasmo dla reklam aktywnych, bootstrap po reklamodawcach). Estymata jest liczona na reklamach z gold standardu zaklasyfikowanych jako populacja badana, z wagami 1/p; jest nieobciążona co do doboru próby, ale nie wykorzystuje predykcji annotatora ocenianego na całej ramce, więc ma większą wariancję niż metoda łącząca oba (DSL).
- **Co mamy dla częstości klasy:** `tools/estimators.py`, estymator różnicowy dla prostego parametru (liczbę reklam w klasie dostajemy mnożąc częstość przez liczebność ramki P02). Test na danych syntetycznych (300 powtórzeń): błąd naiwnej estymaty −0,029 (SE 0,0008), po korekcie −0,002 (SE 0,0017), czyli brak wykrywalnego obciążenia; estymator po korekcie ma jednak ok. dwukrotnie większe odchylenie standardowe niż naiwny (0,029 vs 0,014). To kompromis obciążenie–wariancja, o którym trzeba pisać w preprincie.
- **Czego nie mamy:** pełnego DSL dla regresji z kowariatami ani korekty dla modelu czasu życia. Będą potrzebne, jeśli analiza obejmie związek czasu życia lub intensywności z cechami reklamy (np. typ scamu, obecność osoby publicznej) albo model przeżycia dla reklam aktywnych (Kaplan–Meier; w repozytorium jest tylko pasmo mediany). To jest zadanie dla analityka po lekturze pracy [@egami2025dsl]: > **[ANALITYK – DO WYPEŁNIENIA]**; status: do wdrożenia.
- Analiza wrażliwości: `prevalence_from_sens_spec` pozwala sprawdzić, jak zmieniałaby się częstość przy założonej czułości i swoistości z przedziału ufności walidacji. Używać z zakresem wartości.

## 7. Co jest przyjęte bez źródła (heurystyka własna)

1. Docelowa liczba 60 pozytywów na klasę raportowaną osobno.
2. Limit 5% próby na reklamodawcę.
3. Dwie rundy pilotażu po 30–50 reklam.

Każdą z tych wartości trzeba uzasadnić lub zmienić na podstawie danych (P09, P11, P13) i opisać w preprincie jako decyzję własną.
