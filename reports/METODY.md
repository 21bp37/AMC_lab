# Metody eksploracji i pomiaru: definicje, metryki, testy

Dokument opisuje **co** liczymy, **na jakiej podstawie** i **jakim testem**, dla każdej liczby w karcie M1
(`M1_karta_eksploracji.tex`) i w wynikach (`eda_results.md`, generowanym). Parametry podane tutaj są wartościami
domyślnymi z kodu; ich źródło to `pipeline/config.py` i sygnatury funkcji w `pipeline/`. Numery § są używane
w `eda_results.md`.

Spis: §1 dane i jednostki · §2 miary · §3 testy eksploracyjne · §4 testy hipotez H1/H2 · §5 walidacja pomiaru ·
§6 ograniczenia statystyczne · §7 słownik symboli i pojęć

---

## 1. Dane i jednostki analizy

| Pojęcie | Definicja | Gdzie w kodzie |
|---|---|---|
| **wpis (wiersz)** | jeden wiersz eksportu NodeXL: oryginał (`Tweet`), odpowiedź (`Replies to`) albo retweet (`Retweet`) | `load_twitter.normalize`, kolumna `type` |
| **treść (kaskada)** | jedna unikalna treść: oryginał lub odpowiedź liczone raz, a wszystkie retweety jednego wpisu łącznie jako jedna treść. Klucz: `autor źródłowy + pierwsze 80 znaków tekstu bez prefiksu „RT @…:”`, małymi literami | `cascade_key` |
| **autor źródłowy** | dla retweetu: konto z prefiksu „RT @konto:” (lub `Vertex 2`); dla pozostałych: autor wpisu | `source_author` |
| **dzień** | doba kalendarzowa w strefie Europe/Warsaw (czas z pliku jest w UTC). Wpis z 22:30 UTC 9.05 należy do 10.05 | `day` |
| **tydzień** | poniedziałek–niedziela (pandas `W-SUN`). W analizach tygodniowych pomijamy tygodnie z < 30 treściami | `eda_twitter.weekly_shares` |
| **okno analizy** | 2022-03-04 – 2022-12-31 (303 dni). 24.02–3.03 wyłączone, bo w zbiorze jest tam tylko 39 wpisów, przy medianie 131 dziennie | `config.EFFECTIVE_START`, `STUDY_END` |
| **wydarzenie** | ręczna lista dat (`config.EVENTS`); peak jest przypisany do wydarzenia, gdy dzieli je ≤ 3 dni | `series.peak_table` |

**Dwie podstawy liczenia.** *Wpisy* (z retweetami) mierzą, ile treści krążyło, czyli ekspozycję. *Treści* mierzą,
ile różnych rzeczy napisano. Udziały w czasie (trendy, skład) liczymy na **treściach**, bo jeden wiralowy wpis
z setkami retweetów przesuwa udział miesiąca o kilkanaście punktów. Wyjątek: korelacje dzienne (§3.1, drugi
wiersz tabeli) są liczone na wpisach. W tabelach zawsze podajemy, która podstawa jest użyta.

## 2. Miary

### 2.1 Sentyment (ton)
- Pochodzi z pliku: `Sentiment_Label` ∈ {negative, neutral, positive} oraz `Sentiment_Score` ∈ [0, 1], czyli
  prawdopodobieństwo, które model przypisał wybranej etykiecie.
- **Model nie jest opisany** (nazwa, wersja, dane treningowe, pole wejściowe). To decyzja D2 w `CLEANUP.md`.
- Ton mówi, czy *język* jest negatywny, ale **nie mówi, wobec kogo**: krytyka Rosji też jest „negative”.

### 2.2 Leksykony (wersja 0.2, eksploracyjna)
Leksykon to lista wyrażeń regularnych dopasowywanych do tekstu małymi literami (bez prefiksu RT).
Wpis „trafia” w leksykon, gdy pasuje choć jedno wyrażenie z dowolnej kategorii.

| Leksykon | Kategorie (klucze w `config.py`) |
|---|---|
| anty-UA (`ANTI_UA_NARRATIVES`) | `swiadczenia` (500+/800+, zasiłki, socjal, „za darmo”, podatnik), `praca_mieszkania`, `przestepczosc`, `banderyzm` (bandera, UPA, Wołyń, ukrainizacja), `roszczeniowosc` (w tym negacja wdzięczności), `zagrozenie_zdrowie` |
| pro-UA (`PRO_UA_NARRATIVES`) | `pomoc`, `solidarnosc`, `wdziecznosc` |

**Reguła negacji:** jeśli tekst pasuje do `NEGATED_GRATITUDE` („nie widać / brak / bez / zero wdzięczności”,
„niewdzięczni”), flaga pro-UA jest zerowana. Wpis liczy się wtedy jako anty-UA (`roszczeniowosc`).

### 2.3 Grupy leksykonu (`stance_lex`)
Każda treść trafia do dokładnie jednej grupy:

| Grupa | Warunek |
|---|---|
| `anti` (tylko anty-UA) | trafienie w anty-UA, brak w pro-UA |
| `pro` (tylko pro-UA) | trafienie w pro-UA, brak w anty-UA |
| `mieszane` (oba leksykony) | trafienie w oba |
| `brak` (żaden) | brak trafień; **nie oznacza „neutralna”**, tylko brak słów kluczowych |

### 2.4 Udziały i przecięcia
- **Udział** cechy = liczba treści z cechą / liczba wszystkich treści w danym okresie (dzień, tydzień, miesiąc, całe okno).
- **„Anty-UA i negatywne”** (`neg_anti`) = ton negatywny **oraz** trafienie w leksykon anty-UA. To przybliżenie
  „treści negatywnych wobec Ukraińców”.
- **„Pro-UA i pozytywne”** (`pos_pro`) = ton pozytywny **oraz** trafienie w leksykon pro-UA.
- **Prawdopodobieństwa warunkowe**, np. P(neutralne | anty-UA) = odsetek treści neutralnych wśród treści anty-UA.
- **pp** (punkt procentowy) = różnica dwóch odsetków, np. 11,0% → 14,0% to +3,0 pp.

### 2.5 Koncentracja
- **Udział 10 najczęściej retweetowanych kont** = suma retweetów 10 kont źródłowych z największą liczbą retweetów / wszystkie retweety.
- **Udział 1% najaktywniejszych kont** = wpisy 1% kont z największą liczbą wpisów / wszystkie wpisy.
- **Udział top konta / top kaskady w dniu** (tabela peaków) = wiersze dnia pochodzące od jednego najczęstszego
  konta źródłowego / jednej najczęstszej kaskady, podzielone przez wszystkie wiersze dnia.

### 2.6 Peak
Dla dziennej liczby $x_t$ (domyślnie: liczba **treści** w dniu $t$, seria `cascades`):

$$z_t = \frac{\log(1+x_t) - m_t}{1{,}4826 \cdot \mathrm{MAD}_t}$$

- $m_t$ to krocząca mediana $\log(1+x)$ w oknie 15 dni wycentrowanym na $t$ (co najmniej 7 obserwacji).
- $\mathrm{MAD}_t$ to krocząca mediana $|\log(1+x) - m|$ w tym samym oknie, czyli odporny odpowiednik odchylenia
  standardowego. Stała 1,4826 sprawia, że dla rozkładu normalnego MAD·1,4826 ≈ odchylenie standardowe.
- **Zabezpieczenie:** jeśli MAD = 0, zastępujemy je medianą MAD z całej serii. Mianownik nie spada poniżej połowy tej mediany.
- **Peak:** $z_t > 2{,}5$ (parametr `--z`), $t$ jest maksimum $x$ w oknie ±3 dni, a $x_t > 0$.
- **Czułość:** liczbę peaków raportujemy też dla $z$ = 2 i 3.
- Dlaczego logarytm: spłaszcza wielkie wartości, a $\log(1+x)$ działa także dla $x = 0$.
- Dlaczego lokalna mediana, a nie stały próg: peak to odchylenie od *bieżącego* tła. W ruchliwym marcu
  700 wpisów może nie być peakiem, a w spokojnym lipcu 150 już tak.

Kod: `series.robust_z`, `series.detect_peaks`.

## 3. Testy eksploracyjne (opis danych X)

Wszystkie testy są dwustronne, z biblioteki `scipy.stats`, chyba że napisano inaczej. Próg istotności: p < 0,05.

| § | Pytanie | Zmienne | Test | Podstawa | Kod |
|---|---|---|---|---|---|
| 3.1 | Czy udział cechy rośnie lub maleje w czasie? | numer tygodnia (1…n) vs tygodniowy udział cechy | **korelacja rang Spearmana** (`spearmanr`), statystyka ρ | treści, tygodnie z ≥ 30 treściami | `compute_stats` → `weekly_trend` |
| 3.1 | Czy dni z dużą liczbą wpisów różnią się tonem? | dzienna liczba wpisów vs dzienny udział cechy | **korelacja rang Spearmana** | wpisy, 303 dni | `daily_corr` |
| 3.2 | Czy udział różni się między początkiem a końcem roku? | odsetek w III–IV 2022 vs XI–XII 2022 | **test z dla dwóch proporcji**, wariant z łączną proporcją (pooled) | treści | `two_prop` → `early_vs_late` |
| 3.3 | Czy wpisy o danym tonie lub narracji zbierają więcej reakcji? | polubienia, retweety oryginałów w dwóch grupach | **test U Manna–Whitneya** (`mannwhitneyu`) | tylko oryginały | `engagement_originals` |

**Korelacja rang Spearmana (ρ).** Obie zmienne zamieniamy na rangi i liczymy korelację Pearsona rang. ρ ∈ [−1, 1]:
ρ > 0 oznacza, że obie rosną razem, ρ < 0, że jedna rośnie, gdy druga maleje. Wychwytuje każdą monotoniczną
zależność i jest odporna na wartości odstające. p testuje hipotezę zerową ρ = 0.

**Test z dla dwóch proporcji.** $\hat p_1 = x_1/n_1$ i $\hat p_2 = x_2/n_2$, a łączna proporcja to
$\hat p = (x_1+x_2)/(n_1+n_2)$. Statystyka:

$$z = \frac{\hat p_2 - \hat p_1}{\sqrt{\hat p(1-\hat p)(1/n_1 + 1/n_2)}}$$

p = 2·(1 − Φ(|z|)), gdzie Φ to dystrybuanta rozkładu normalnego. Hipoteza zerowa: oba odsetki są równe.

**Test U Manna–Whitneya.** Porównuje dwie niezależne grupy bez założenia normalności. Sprawdza, czy losowa
obserwacja z jednej grupy jest częściej większa niż z drugiej. Właściwy dla liczników reakcji, które mają skrajnie
skośny rozkład. Raportujemy mediany grup i p.

## 4. Testy hipotez H1/H2 (X vs Telegram; gotowe w kodzie, czekają na dane Telegrama)

Oznaczenia: $Y_t$ to dzienna seria w X (liczba treści o Ukraińcach w Polsce; dla H2 z narracją anty-UA).
$X^{RU}_t$, $X^{UA}_t$ to dzienna liczba postów z tematem w kanałach Telegrama prorosyjskich i proukraińskich
(kontrola). $k$ to opóźnienie w dniach; $k > 0$ oznacza, że Telegram wyprzedza X.

| § | Test | Co mierzy | Szczegóły | Kod |
|---|---|---|---|---|
| 4.1 | **Dopasowanie peaków** z testem permutacyjnym | odsetek peaków $Y$, przed którymi w oknie 0–7 dni wystąpił peak $X$ | rozkład zerowy z 1000 **kołowych przesunięć** dat peaków $X$ (wszystkie przesuwamy o tę samą losową liczbę dni, z zawinięciem na początek okna; zachowuje liczbę i odstępy peaków). p = (1 + #{odsetek zerowy ≥ obserwowany}) / (1 + 1000). Raport: mediana i IQR dopasowanych opóźnień | `leadlag.peak_lag_test` |
| 4.2 | **Korelacja krzyżowa** z testem permutacyjnym | współczynnik Pearsona $r(k)$ między $\Delta X_{t-k}$ a $\Delta Y_t$, $k = -14…14$ | $\Delta$ = przyrost $\log(1+x)$ dzień do dnia; różnicowanie usuwa wspólny trend. Statystyka: max |r(k)|. Rozkład zerowy: 500 kołowych przesunięć **przyrostów** $X$ o co najmniej 15 dni (przesunięcie poziomów z trendem dawałoby test zbyt liberalny; sprawdzone testem kalibracji) | `leadlag.xcorr_test` |
| 4.3 | **Test przyczynowości Grangera** (test F, `statsmodels.grangercausalitytests`, statystyka `ssr_ftest`) | czy przeszłe $\Delta X$ poprawiają prognozę $\Delta Y$ ponad przeszłe $\Delta Y$ | oba kierunki ($X→Y$ i $Y→X$), opóźnienia 1–7; raportujemy najmniejsze p po opóźnieniach (uwaga: to wielokrotne porównanie, §6) | `leadlag.granger_min_p` |
| 4.4 | **Symulacja mocy** | szansa, że test 4.1 da p < 0,05, gdy efekt istnieje | 100 par syntetycznych szeregów (300 dni, Poisson, malejący trend). W $X$ jest tyle zdarzeń, ile peaków ma X (8). Każde zdarzenie z prawdopodobieństwem 0,5 lub 0,8 pojawia się w $Y$ po 3 ± 1 dniach. Amplituda zdarzenia: 4-krotność tła. W teście 199 permutacji | `leadlag.power_peak_lag` |

**Reguła decyzyjna H1** (wszystkie warunki):
1. Test 4.1 daje p < 0,05.
2. Maksimum $r(k)$ w 4.2 wypada przy $k \in [1, 7]$ i $r > 0$.
3. Granger $X^{RU}→Y$ ma p < 0,05, a $Y→X^{RU}$ nie.
4. Odsetek dopasowanych peaków dla $X^{RU}$ jest wyraźnie wyższy niż dla $X^{UA}$.

**Reguła decyzyjna H2:** H1 jest spełniona, a dodatkowo mediana dopasowanych opóźnień ∈ [1, 7] dni i IQR ≤ 2 dni
(IQR = 75. percentyl − 25. percentyl). Mediana dostanie bootstrapowy 95% przedział ufności (do dodania w `leadlag.py` po wczytaniu Telegrama). Gdy dopasowanych peaków
jest < 8, H2 raportujemy opisowo.

## 5. Walidacja pomiaru narracji (plan)

| Miara | Definicja | Próg / użycie | Kod |
|---|---|---|---|
| **α Krippendorffa** | zgodność dwóch koderów skorygowana o zgodność przypadkową; 0 = losowa, 1 = pełna | ≥ 0,667 wnioski wstępne, ≥ 0,800 dane wiarygodne | `tools/agreement.py` |
| **κ Cohena** | zgodność dwóch koderów dla etykiet nominalnych (uzupełnienie α) | raportowane z odsetkiem zgodności i zgodnością pozytywną/negatywną | `tools/agreement.py` |
| **Precyzja P** | trafne wśród oznaczonych przez klasyfikator jako anty-UA (TP / (TP + FP)) | raport z przedziałem ufności | `tools/evaluation.py` |
| **Czułość R** (recall) | wyłapane wśród prawdziwych anty-UA (TP / (TP + FN)) | j.w. | `tools/evaluation.py` |
| **F1** | średnia harmoniczna P i R: 2PR / (P + R) | j.w. | `tools/evaluation.py` |
| **Przedział Wilsona** | 95% przedział ufności dla odsetka | planowanie liczebności próby (2×300) | `tools/sample_size.py` |
| **Bootstrap klastrowy** | losowanie ze zwracaniem całych kont/kanałów, nie pojedynczych wpisów | przedziały ufności P/R/F1 | `tools/evaluation.py` |
| **Estymator z próbą ekspercką** | udział z klasyfikatora korygowany o błąd zmierzony na próbie kodowanej ręcznie | końcowe udziały anty-UA | `tools/estimators.py` |

Próba walidacyjna: 300 treści z X i 300 postów z Telegrama, warstwowane po grupie leksykonu i limitowane per
konto/kanał, kodowane niezależnie przez 2 osoby. Kategorie stanowiska: anty-UA / pro-UA / neutralne / nie dotyczy.

## 6. Ograniczenia statystyczne

- **Wielokrotne porównania:** w eksploracji jest kilkanaście testów, więc pojedyncze p z zakresu 0,01–0,05 może
  być fałszywie istotne. Główne wyniki mają p < 0,001. W analizie H1/H2 planujemy korektę Holma.
- **Autokorelacja:** kolejne dni i tygodnie są do siebie podobne, a testy z §3 zakładają niezależność. Rzeczywiste
  p są przez to wyższe niż podane, więc wyniki §3 są eksploracyjne. Testy z §4 są na to odporne, bo permutacje
  kołowe zachowują strukturę czasową.
- **Zależność obserwacji:** wpisy jednego konta nie są niezależne. Dlatego udziały liczymy na treściach,
  a w walidacji bootstrapujemy po kontach.
- **Liczniki reakcji** pochodzą z chwili pobrania danych, nie z dnia publikacji. Starsze wpisy miały więcej czasu
  na zebranie reakcji.

## 7. Słownik symboli i pojęć

| Symbol / pojęcie | Znaczenie |
|---|---|
| $t$ | dzień (doba w czasie warszawskim) |
| $x_t$ | dowolna dzienna liczba, np. liczba treści w dniu $t$ |
| $Y_t$ | dzienna seria z X (zmienna zależna) |
| $X^{RU}_t$, $X^{UA}_t$ | dzienna seria z Telegrama, kanały prorosyjskie i proukraińskie |
| $\log(1+x)$ | logarytm naturalny z $1+x$; spłaszcza duże wartości, działa dla $x = 0$ |
| $\Delta$ | przyrost z dnia na dzień: $\Delta x_t = \log(1+x_t) - \log(1+x_{t-1})$ |
| $m_t$ | 15-dniowa krocząca mediana $\log(1+x)$ wokół dnia $t$ |
| MAD | mediana bezwzględnych odchyleń od mediany |
| $z_t$ | odporny wynik standaryzowany dnia $t$ (§2.6); osobno $z$ to statystyka testu dwóch proporcji (§3.2) |
| $k$ | opóźnienie w dniach; $k > 0$: Telegram wyprzedza X |
| $r$ | współczynnik korelacji Pearsona (liniowej), od −1 do 1 |
| ρ (rho) | współczynnik korelacji rang Spearmana, od −1 do 1 |
| p | p-value: prawdopodobieństwo wyniku co najmniej tak skrajnego, gdyby hipoteza zerowa (brak efektu) była prawdziwa |
| α | tu: α Krippendorffa (zgodność koderów); nie mylić z poziomem istotności 0,05 |
| IQR | rozstęp międzykwartylowy: 75. percentyl − 25. percentyl |
| pp | punkt procentowy |
| mediana | wartość środkowa po posortowaniu |
| moc testu | prawdopodobieństwo wykrycia efektu, jeśli on istnieje |
| rozkład zerowy | rozkład statystyki przy braku efektu, tu uzyskany z permutacji |
| permutacja kołowa | przesunięcie całej serii lub dat peaków o tę samą liczbę dni z zawinięciem końca na początek |
| H1, H2 | hipotezy: kolejność (Telegram prorosyjski → X) i stałe opóźnienie (karta, sekcja 1) |
