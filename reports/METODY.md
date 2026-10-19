# Metody eksploracji i pomiaru: definicje, metryki, testy

Dokument opisuje **co** liczymy, **na jakiej podstawie** i **jakim testem**, dla każdej liczby w karcie M1
(`M1_karta_eksploracji.tex`) i w wynikach (`eda_results.md`, generowanym). Parametry podane tutaj są wartościami
domyślnymi z kodu; ich źródło to `pipeline/config.py` i sygnatury funkcji w `pipeline/`. Numery § są używane
w `eda_results.md`.

Spis: §1 dane i jednostki · §2 miary · §3 testy eksploracyjne · §4 test hipotezy · §5 walidacja pomiaru ·
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

### 3.4 Telegram (eksploracja opisowa; `pipeline/eda_telegram.py`)

Bez testów hipotezy. Dane: posty z plików `post_texts_part_N.csv`, **przefiltrowane przy pobraniu** do 2022 r. i tematu
„Ukraina **i** Polska” (wyrażenia RU/UK w `config.TELEGRAM_UA` i `TELEGRAM_PL`: np. украин-/україн- oraz польш-/поляк-/варшав-).
Pliki są **niepełne** (raport podaje, które części uwzględniono) i nie stanowią próby losowej kanałów, bo każdy plik zawiera całe kanały.

| Miara | Definicja |
|---|---|
| **strona kanału** | z `leiden_clusters.csv`, kolumna `side`: *pro-Russian* (1 958 kanałów), *pro-Ukrainian* (1 116); kanały bez etykiety (z 4 687 jest ich 1 613) = `unlabeled`. Strony „neutralnej” w danych nie ma |
| **dzień** | doba w strefie Europe/Warsaw (czas posta z pliku jest w UTC) |
| **post z narracją anty-UA** | post tematyczny pasujący do szkicu `config.TELEGRAM_ANTI_UA` (v0.1, niezwalidowany; zawiera też hasła wojennej retoryki, np. „нацист”, „бандер”) |
| **dni bez postu** | odsetek dni okna (303), w których dana strona ma 0 postów tematycznych; pokazuje, czy szereg dzienny w ogóle da się zbudować |
| **top-10 kanałów** | udział 10 najaktywniejszych kanałów strony w jej postach (koncentracja) |
| **powtórzony tekst** | udział postów, których pierwsze 80 znaków (małe litery, znormalizowane spacje) wystąpiło już w innym poście strony (kopiowanie między kanałami) |
| **trend udziału anty-UA** | korelacja rang Spearmana między numerem tygodnia a tygodniowym udziałem postów anty-UA, tygodnie z ≥ 10 postami (tu próg jest niższy niż w X, bo to liczność postów, nie treści); opisowo |
| **peak** | ta sama definicja co §2.6, na dziennej liczbie postów prorosyjskich; `top_channel_share` to udział najaktywniejszego kanału w tym dniu |
| **zestawienie z X** (rys. 2C) | tygodniowe sumy postów prorosyjskich i treści anty-UA w X, każde skalowane do swojego maksimum; wyłącznie wizualne, bez korelacji i testu |

**Granica interpretacji.** Temat „Ukraina i Polska” obejmuje wojnę i geopolitykę (np. Przewodów), nie tylko uchodźców,
więc obecny szereg nie mierzy jeszcze zjawiska z hipotezy. Zawężenie do uchodźców (słowa typu беженц-, біженц-,
„украинцы в Польше”) to następny krok.

## 4. Test hipotezy (X vs Telegram; gotowy w kodzie, czeka na dane Telegrama)

**Hipoteza (H):** trendy w pojawianiu się negatywnych treści na temat ukraińskich uchodźców w polskich mediach
społecznościowych są skorelowane z podobnymi trendami w źródłach prorosyjskich.
**H₀:** po usunięciu wspólnego trendu całorocznego zmiany w obu źródłach nie są dodatnio skorelowane.

Oznaczenia: $Y_t$ to dzienna liczba różnych treści w X o Ukraińcach w Polsce z narracją anty-UA.
$X^{RU}_t$, $X^{UA}_t$ to dzienna liczba postów o Ukraińcach w Polsce z narracją anty-UA w kanałach Telegrama
prorosyjskich i proukraińskich (kontrola). $\Delta x_t = \log(1+x_t) - \log(1+x_{t-1})$ to przyrost z dnia na dzień.
$k$ to opóźnienie w dniach; $k > 0$ oznacza, że Telegram jest wcześniej.

**Dlaczego przyrosty, a nie poziomy.** Oba szeregi mogą maleć w ciągu roku, bo słabnie zainteresowanie wojną. Korelacja
poziomów byłaby wtedy wysoka bez żadnego związku między źródłami (korelacja pozorna). Przyrosty mierzą, czy *zmiany*
idą w parze. Test `test_weekly_trend_corr_detects_and_ignores_common_trend` pokazuje to na danych syntetycznych:
dwa niezależne szeregi z tym samym trendem mają ρ poziomów > 0,8, a test przyrostów nie daje istotności.

| § | Test | Co mierzy | Szczegóły | Kod |
|---|---|---|---|---|
| 4.1 | **Test główny: korelacja krzyżowa przyrostów** z testem permutacyjnym | największy współczynnik Pearsona $r(k)$ między $\Delta X^{RU}_{t-k}$ a $\Delta Y_t$ dla $k = 0…7$ | p jednostronne (H: r > 0). Rozkład zerowy: 1000 kołowych przesunięć szeregu $\Delta X^{RU}$ o co najmniej 8 dni (cała seria przesunięta, koniec zawinięty na początek; niszczy związek z $Y$, zachowuje własną zmienność serii). Statystyka zerowa też jest maksimum po $k$, więc wybór najlepszego opóźnienia nie zawyża istotności. p = (1 + #{wynik zerowy ≥ obserwowany}) / (1 + 1000). Liczone osobno dla $X^{RU}$ i $X^{UA}$ | `leadlag.xcorr_test(x, y, max_lag=7, min_lag=0, positive=True)` |
| 4.2 | **Test tygodniowy** | korelacja rang Spearmana ρ między tygodniowymi przyrostami $\log(1 + \text{suma tygodnia})$ | p jednostronne z 2000 kołowych przesunięć przyrostów $X$. Raportujemy też ρ poziomów, tylko dla porównania (bez testu) | `leadlag.weekly_trend_corr` |
| 4.3 | **Różnica RU vs UA** (kontrola) | $\max_k r_{RU}(k) - \max_k r_{UA}(k)$, $k = 0…7$ | blokowy bootstrap dni: 2000 losowań ze zwracaniem bloków 7 kolejnych dni docelowych $t$ (wspólnie dla RU i UA); dla każdego $k$ para $(\Delta X_{t-k}, \Delta Y_t)$ pochodzi z oryginalnej serii, więc opóźnienia nie przechodzą przez granice bloków. 95% przedział percentylowy | `leadlag.control_difference` |
| 4.4 | **Symulacja mocy** testu 4.1 | odsetek wyników z p < 0,05 przy znanej prawdziwej korelacji | 100 par syntetycznych szeregów po 303 dni. Liczności z rozkładu Poissona (średnio 60 dziennie), log-poziomy z wspólnym składnikiem o korelacji ρ i opóźnieniu 2 dni. 199 permutacji na test. Wyniki w `eda_results.md` §7: ρ = 0 → ok. 5% (kalibracja), ρ = 0,2 → ok. 50%, ρ = 0,3 → ok. 90% | `leadlag.power_xcorr` |

**Uruchomienie całości:** `leadlag.test_hypothesis(x_ru, x_ua, y)`, gdzie `y = series.daily_series(...)["anti_contents"]`, a `x_ru`, `x_ua` = `telegram.side_series(daily, "Pro-Russian" / "Pro-Ukrainian", col="n_topic_anti")`. Zwraca wyniki 4.1–4.3 i spełnienie kryteriów (a)–(c).

**Reguła decyzyjna.** H wspieramy, gdy:
1. Test 4.1 dla $X^{RU}$ daje p < 0,05.
2. Test 4.2 i wariant na udziałach (zamiast liczb) dają korelację tego samego znaku.
3. Przedział z 4.3 dla $r_{RU} - r_{UA}$ leży powyżej 0.

H₀ utrzymujemy, gdy p ≥ 0,05. Przy mocy z 4.4 oznacza to brak korelacji rzędu 0,3 lub silniejszej, ale nie wyklucza
słabszej (ok. 0,2 lub mniej).

**Warianty (wrażliwość):** udziały zamiast liczb (odporne na ogólny wzrost zainteresowania tematem), suma wyświetleń
na Telegramie, szereg bez dni ±3 od wydarzeń z `config.EVENTS` (wspólny bodziec).

### Analizy uzupełniające (kierunek; opisowo, nie rozstrzygają H)

| Test | Co mierzy | Szczegóły | Kod |
|---|---|---|---|
| **Test przyczynowości Grangera** (test F, `statsmodels.grangercausalitytests`, statystyka `ssr_ftest`) | czy przeszłe $\Delta X$ poprawiają prognozę $\Delta Y$ ponad przeszłe $\Delta Y$ | oba kierunki ($X→Y$ i $Y→X$), opóźnienia 1–7; raportujemy najmniejsze p po opóźnieniach (wielokrotne porównanie, §6) | `leadlag.granger_min_p` |
| **Dopasowanie peaków** z testem permutacyjnym | odsetek peaków $Y$, przed którymi w oknie 0–7 dni wystąpił peak $X$ | rozkład zerowy z 1000 kołowych przesunięć dat peaków $X$; raport: mediana i IQR opóźnień. Moc przy 8 peakach: ok. 46–80% (`eda_results.md` §7) | `leadlag.peak_lag_test`, `leadlag.power_peak_lag` |
| **Ślad treści** | czy to samo twierdzenie pojawiło się najpierw na Telegramie | ręcznie, 5 największych peaków $Y$, tłumaczenie RU→PL | — |

## 5. Walidacja pomiaru narracji (plan)

| Miara | Definicja | Próg / użycie | Kod |
|---|---|---|---|
| **α Krippendorffa** | zgodność koderów skorygowana o zgodność przypadkową; 0 = losowa, 1 = pełna | opcjonalnie (standard w analizie treści: ≥ 0,667 wnioski wstępne, ≥ 0,800 wiarygodne); w projekcie wystarcza κ | `tools/agreement.py` |
| **κ Cohena** | zgodność dwóch koderów dla etykiet nominalnych, skorygowana o zgodność przypadkową | **główna miara zgodności w projekcie**; raportowana z odsetkiem zgodności; κ < 0,4 = próba za słaba do interpretacji udziałów | `tools/agreement.py` |
| **Precyzja P** | trafne wśród oznaczonych przez klasyfikator jako anty-UA (TP / (TP + FP)) | raport z przedziałem ufności | `tools/evaluation.py` |
| **Czułość R** (recall) | wyłapane wśród prawdziwych anty-UA (TP / (TP + FN)) | j.w. | `tools/evaluation.py` |
| **F1** | średnia harmoniczna P i R: 2PR / (P + R) | j.w. | `tools/evaluation.py` |
| **Przedział Wilsona** | 95% przedział ufności dla odsetka | przedziały dla próby 2×100 | `tools/sample_size.py` |
| **Bootstrap klastrowy** | losowanie ze zwracaniem całych kont/kanałów, nie pojedynczych wpisów | przedziały ufności P/R/F1 | `tools/evaluation.py` |
| **Estymator z próbą ekspercką** | udział z klasyfikatora korygowany o błąd zmierzony na próbie kodowanej ręcznie | końcowe udziały anty-UA | `tools/estimators.py` |

Próba walidacyjna (wersja dla zespołu bez eksperta od języków): po **100** losowych treści z X i z Telegramu (kanały prorosyjskie),
kodowane niezależnie przez dwie osoby. Posty z Telegramu kodujemy **po tłumaczeniu maszynowym** na polski (DeepL/Google
lub model językowy); to ograniczenie (tłumaczenie zniekształca ton i slang) podajemy razem z wynikami. Kategorie: anty-UA / pro-UA / inne.
Przy próbie 100 przedział ufności dla precyzji ma szerokość rzędu ±10 pp. **Reguła:** jeśli κ < 0,4 lub precyzja słownika na Telegramie jest niska,
nie interpretujemy udziałów narracji z Telegramu i testujemy tylko wolumen tematu (liczba postów o uchodźcach, bez oceny narracji), co jest słabszą wersją hipotezy.
Estymator z próbą ekspercką (`tools/estimators.py`) stosujemy tylko wtedy, gdy próba jest losowa i wystarczająco duża; w przeciwnym razie raportujemy surowe udziały z zastrzeżeniem.

## 6. Ograniczenia statystyczne

- **Wielokrotne porównania:** w eksploracji jest kilkanaście testów, więc pojedyncze p z zakresu 0,01–0,05 może
  być fałszywie istotne. Główne wyniki mają p < 0,001. Test hipotezy ma jeden test główny (4.1), a test 4.2 i warianty tylko potwierdzają kierunek wyniku, więc nie wymagają korekty. Przy analizach uzupełniających planujemy korektę Holma.
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
| $Y_t$ | dzienna seria z X: liczba treści o Ukraińcach w Polsce z narracją anty-UA |
| $X^{RU}_t$, $X^{UA}_t$ | dzienna seria z Telegrama (te same treści), kanały prorosyjskie i proukraińskie (kontrola) |
| $\log(1+x)$ | logarytm naturalny z $1+x$; spłaszcza duże wartości, działa dla $x = 0$ |
| $\Delta$ | przyrost z dnia na dzień: $\Delta x_t = \log(1+x_t) - \log(1+x_{t-1})$ |
| $m_t$ | 15-dniowa krocząca mediana $\log(1+x)$ wokół dnia $t$ |
| MAD | mediana bezwzględnych odchyleń od mediany |
| $z_t$ | odporny wynik standaryzowany dnia $t$ (§2.6); osobno $z$ to statystyka testu dwóch proporcji (§3.2) |
| $k$ | opóźnienie w dniach; $k > 0$: Telegram wcześniej niż X; test główny sprawdza $k = 0…7$ |
| $r$ | współczynnik korelacji Pearsona (liniowej), od −1 do 1 |
| ρ (rho) | współczynnik korelacji rang Spearmana, od −1 do 1 |
| p | p-value: prawdopodobieństwo wyniku co najmniej tak skrajnego, gdyby hipoteza zerowa (brak efektu) była prawdziwa |
| κ (kappa) | κ Cohena: zgodność dwóch koderów skorygowana o zgodność przypadkową (0 = losowa, 1 = pełna); nie mylić z α Krippendorffa ani z poziomem istotności |
| IQR | rozstęp międzykwartylowy: 75. percentyl − 25. percentyl |
| pp | punkt procentowy |
| mediana | wartość środkowa po posortowaniu |
| moc testu | prawdopodobieństwo wykrycia efektu, jeśli on istnieje |
| rozkład zerowy | rozkład statystyki przy braku efektu, tu uzyskany z permutacji |
| permutacja kołowa | przesunięcie całej serii lub dat peaków o tę samą liczbę dni z zawinięciem końca na początek |
| H, H₀ | hipoteza (korelacja trendów negatywnych treści w X i w źródłach prorosyjskich) i hipoteza zerowa (brak dodatniej korelacji przyrostów) |
| korelacja pozorna | korelacja wynikająca tylko ze wspólnego trendu lub wspólnej przyczyny, a nie ze związku między szeregami |
