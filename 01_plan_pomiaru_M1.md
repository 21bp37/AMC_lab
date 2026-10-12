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
| T_L: próg mediany czasu życia | 2 dni kalendarzowe | H1: mediana L ≤ T_L |
| T_I: próg dziennej intensywności | 25 000 wyświetleń na dzień | H2: udział reklam z I ≥ T_I |
| p_min: wymagany udział | 50% | H2: udział reklam z I ≥ T_I jest większy niż p_min |

**Operacjonalizacja przyjęta przez pipeline** (do potwierdzenia przez leada i analityka):

- **L (czas życia)** = liczba dni kalendarzowych od pierwszego do ostatniego dnia emisji, **włącznie z oboma** (`delivery_stop − delivery_start + 1`); reklama wyświetlana jednego dnia ma L = 1. To ważne dla progu T_L = 2, bo zmiana konwencji o jeden dzień zmienia wniosek.
- **I (dzienna intensywność)** = skumulowane wyświetlenia (`reach_total`) / L. Liczba „aktywnych dni” jest przybliżona rozpiętością od pierwszej do ostatniej emisji (źródło nie ujawnia dni przerwy, jeśli były).
- **H1:** mediana L w populacji badanej ≤ T_L. **H2:** udział reklam populacji z I ≥ T_I jest większy niż p_min (równoważnie: mediana I ≥ T_I).
- Obie wielkości są liczone **na populacji badanej**, czyli na reklamach sklasyfikowanych jako deepfake scam (sekcja 4), z korektą błędu klasyfikacji (05, sekcja 6).

**Czego dane nie pozwolą ocenić (uczciwe zastrzeżenie dla karty M1).** Źródło daje **sumę wyświetleń za cały okres emisji**, a nie przebieg godzina po godzinie ani dzień po dniu. Dzienna intensywność jest więc wartością *średnią* (suma podzielona przez liczbę dni). Wysoka średnia intensywność przy krótkim życiu jest **zgodna z** taktyką *burst-and-burn*, ale jej nie dowodzi: ta taktyka dotyczy rozkładu w czasie (duży budżet na początku, potem wygaszenie), którego nie obserwujemy. Zdanie „co potwierdza stosowanie taktyki” w hipotezie jest interpretacją wykraczającą poza dane; w preprincie proponujemy sformułowanie „co jest zgodne z” (decyzja leada, R20). Dodatkowo krótkie życie może wynikać z szybkiego usuwania reklam przez platformę, a nie z decyzji reklamodawcy (R02).

> **[LEAD – DO WYPEŁNIENIA]** Reguła rozstrzygnięcia hipotez (np. co uznajemy za wsparcie H1 i H2: położenie przedziału ufności względem T_L, T_I i p_min): {{P32: reguła decyzyjna dla H1 i H2 (np. położenie przedziału ufności względem T_L, T_I i p_min) | zależy od: lead, analityk, P13 | domyślnie: brak}}
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
| Dowód zewnętrzny scamu (domena docelowa, Lista Ostrzeżeń CERT) | dane i lista | [INŻ. DANYCH] dostarcza, [PIPELINE] zestawia |
| Czas życia L (początek i koniec emisji) | metadane źródła (daty pierwszego i ostatniego wyświetlenia) | [INŻ. DANYCH] dostarcza; obróbka (cenzurowanie, przeżycie): [ANALITYK] |
| Skumulowane wyświetlenia → dzienna intensywność I | metadane źródła (liczba osób lub wyświetleń za okres) | [INŻ. DANYCH] dostarcza; I = suma / L liczy `tools/outcomes.py` |
| Mediana L, udział I ≥ T_I, przedziały ufności | liczone na populacji badanej z korektą błędu klasyfikacji | [PIPELINE] estymata prosta, [ANALITYK] modele |

Annotator oceniany nie mierzy ani czasu życia, ani intensywności. Mierzy **przynależność do klasy** (deepfake scam), a zadaniem pipelinu jest pokazać, jak błąd tej klasyfikacji wpływa na oba wyniki (sekcja 7).

## 3. Jednostka analizy i ramka

- **Jednostka:** unikatowa reklama w źródle (`ad_id`), z reklamodawcą jako klastrem; kreacje są deduplikowane (`creative_id`). Reklamy nie są niezależnymi obserwacjami: w raporcie branżowym 10 największych reklamodawców scamowych odpowiadało za 56,1% reklam scamowych [@gendigital2026]; dla naszych danych koncentrację policzy inżynier danych (P11).
- **Źródło (wpisane z ustaleń zespołu):** głównie **TikTok**, czyli Commercial Content Library i powiązane API (Commercial Content API). Według oficjalnych stron TikToka biblioteka zawiera kreacje, daty emisji, targetowanie i „liczbę osób, które zobaczyły reklamę”, obejmuje obecnie dane z Europy, a dane są dostępne do roku od ostatniego wyświetlenia reklamy; API jest otwarte dla publiczności i badaczy po wniosku przez konto deweloperskie [@tiktokcca; @tiktokcclnews2023]. Szczegóły pól i warunków potwierdza inżynier danych (P06, P07).
- **Ramka (zbiór kandydujący):** > **[INŻ. DANYCH / LEAD – DO WYPEŁNIENIA]** {{P29: jak zbudowano zbiór reklam kandydujących (kryteria, zapytania po słowach kluczowych lub reklamodawcach) | zależy od: źródło, P01 | domyślnie: brak}}. Okno dat i języki: {{P01: okno dat i języki | zależy od: macierz legalności (P07) | domyślnie: kraje UE (zakres źródła); okno i języki brak}}. Liczebność: {{P02: liczba reklam, kreacji, reklamodawców | zależy od: pobranie danych | domyślnie: nieznana}}.
- **Wymaganie pipelinu wobec ramki:** ramka nie może być zbudowana na wyniku annotatora ocenianego ani na kryterium „scam”; w przeciwnym razie wnioski dotyczą tylko ramki i nie uogólniają się na populację reklam (D9). Wyszukiwanie po słowach kluczowych wyznacza ramkę, więc słowa kluczowe i daty zapytań trzeba zapisać.
- Ramka jest **zbiorem cenzurowanym** (R01, R17): obserwujemy reklamy, które źródło zachowało i udostępniło, tylko do roku od ostatniego wyświetlenia.

## 4. Definicje i dowód na scam

**Populacja badana („reklama typu deepfake scam”).** Reklama spełniająca jednocześnie dwa kryteria:
1. **scam** (poniżej),
2. **podejrzenie deepfake'a**: `media_synthetic_suspected` ∈ {`yes`, `suspected`} (02). Przy `yes` wymagana jest nazwana przesłanka (`media_synthetic_cue`). Analiza wrażliwości: tylko `yes`.

Deepfake nie jest tu ustalany, tylko **podejrzewany** na podstawie kreacji (R19). Pytanie „typu deepfake scam” w obecnym brzmieniu wymaga dostępu do kreacji (wideo): bez D1 populacji nie da się zidentyfikować (sekcja 8). Wizerunek osoby publicznej (`celeb_mention`, `celeb_face_visible`, `celeb_category`) jest warstwą opisową, chyba że lead zawęży populację (P30).

**Scam.** Dwie warstwy, rozdzielone celowo:
1. *Typ oferty* z treści reklamy (`scam_type`, kodowany przez annotatorów, łącznie z wartościami `not_scam` i `unclear`).
2. *Dowód zewnętrzny*: łańcuch reklama, domena docelowa, Lista Ostrzeżeń CERT Polska [@certlist]. Lista zawiera domeny wprowadzające w błąd i wyłudzające dane; według miesięcznych podsumowań CERT domeny są blokowane na 6 miesięcy, a jeśli nadal zawierają niebezpieczne treści, wpisuje się je ponownie. CSIRT KNF opisuje zgłaszanie do wpisu na tę listę domen z reklam fałszywych inwestycji publikowanych na Facebooku [@csirtknf2024]. Warunki: {{P18: warunki użycia Listy Ostrzeżeń | zależy od: inżynier danych | domyślnie: brak}}, {{P05: dostępność adresu docelowego | zależy od: pola źródła | domyślnie: nieznana}}, pokrycie: {{P19: odsetek domen z danych możliwych do zestawienia z listą | zależy od: P05, P18 | domyślnie: nieznane}}.
3. *Ocena annotatora referencyjnego* (`scam_judgement`) jest zmienną pomocniczą, nie dowodem.

**Dlaczego nie wystarczy usunięcie reklamy przez platformę jako definicja scamu.** Jeśli „scam” = „usunięta”, to **czas życia jest z definicji czasem do usunięcia**, więc pytanie o czas życia staje się tautologią, a hipoteza o krótkim życiu byłaby spełniona z konstrukcji (R02, R03). Dlatego scam etykietujemy niezależnie od decyzji platformy, a decyzję platformy (`platform_removal`) traktujemy jako zmienną do analizy wrażliwości. Jeśli nie ma adresu docelowego, łańcuch dowodu odpada (D4) i trzeba to zapisać jako jawne zastrzeżenie.

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
2. Gold standard: losowanie warstwowe z limitem na reklamodawcę i zapisem prawdopodobieństw włączenia; annotatorzy referencyjni ({{P21: skład | zależy od: lead | domyślnie: nieznany}}); Krippendorff α jako miara główna z progami 0,80 i 0,667 [@krippendorff2004].
3. Annotator oceniany jest oceniany względem gold standardu; precision zawsze z prevalence; CI przez bootstrap po klastrach [@cameron2015].
4. Wrażliwość na parafrazy promptu i wersję modelu raportowana jako zakres [@baumann2025].
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
| Czy jest legalne źródło reklam? | TikTok Commercial Content Library i API: publiczny dostęp, API po wniosku dla badaczy, dane z UE [@tiktokcca; @tiktokcclnews2023]; warunki dla zapisu i publikacji danych do sprawdzenia w regulaminie | [INŻ. DANYCH] | P07, P20 |
| Czy dostępne są daty początku i końca emisji? | Strona API wymienia datę publikacji i „last seen date”; **nie potwierdzono**, że to pierwszy i ostatni dzień wyświetlania i jak oznaczane są reklamy wciąż aktywne | [INŻ. DANYCH] | D6, P06, P28 |
| Czy dostępna jest liczba wyświetleń? | Strona API wymienia „liczbę osób, które zobaczyły reklamę”; **nie potwierdzono**, czy to wyświetlenia czy unikatowi odbiorcy, czy podawana jest wartość czy przedział i czy jest to suma za okres | [INŻ. DANYCH] | D6, P06 |
| Czy dostępne są kreacje (wideo), potrzebne do wskazania deepfake'a? | Biblioteka zawiera kreacje; **nie potwierdzono** zakresu w API ani prawa do zapisu i przetwarzania | [INŻ. DANYCH] | D1, P04 |
| Czy jest dość reklam deepfake scam do oszacowania mediany i udziału? | Nieznane; zależy od prevalence deepfake scamów w ramce | [PIPELINE] | D2, P09, P02 |
| Czy annotator oceniany zadziała? | Literatura dla tekstu, angielskiego; **brak równorzędnej walidacji dla reklam wideo i dla wykrywania deepfake'ów** [@gilardi2023; @ziems2024] | [PIPELINE] | D5, P14 |

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
