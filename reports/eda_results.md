# Wyniki eksploracji X/Twitter (generowane)

Plik generuje `python -m pipeline.eda_twitter`; nie edytować ręcznie. Definicje miar, podstaw liczenia i testów: `reports/METODY.md` (numery sekcji w nawiasach §).

Parametry: okno 2022-03-04–2022-12-31, próg peaku z = 2.5, okno mediany 15 dni, separacja ±3 dni, leksykony v0.2.

## 1. Zbiór (§1)

| Miara | Wartość |
|---|---|
| wpisy (wiersze) | 55 035 |
| w tym oryginały / odpowiedzi / retweety | 6043 / 13773 / 35219 |
| konta (autorzy wierszy) | 18833 |
| unikalne treści (kaskady) w oknie | 20188 |
| wpisy przed 2022-03-04 (okres niekompletny) | 39 |
| mediana wpisów na dzień w oknie | 131 |
| retweety z uciętym tekstem („…”) | 93,3% |
| oryginały+odpowiedzi zawierające obie frazy doboru dosłownie | 53,4% |
| etykiety sentymentu z pewnością > 0,95 | 93,2% |
| udział 10 najczęściej retweetowanych kont we wszystkich retweetach (§2.5) | 22,6% |
| udział 1% najaktywniejszych kont we wszystkich wpisach (§2.5) | 16,8% |
| linki do rosyjskich mediów państwowych / do Telegrama | 3 / 9 |

## 2. Skład: ton × leksykon (§2.3–2.4)

Podstawa: unikalne treści w oknie. Odsetek w wierszu = udział tonu w danej grupie leksykonu.

| Grupa leksykonu | Udział treści | Negatywne | Neutralne | Pozytywne |
|---|---|---|---|---|
| tylko anty-UA | 12,7% | 68% | 29% | 3% |
| tylko pro-UA | 7,4% | 47% | 34% | 19% |
| oba leksykony | 1,1% | 71% | 23% | 6% |
| żaden leksykon | 78,9% | 54% | 39% | 7% |

| Miara (unikalne treści) | Wartość | To samo na wpisach z RT |
|---|---|---|
| ton negatywny | 55,6% | 41,5% |
| ton pozytywny | 7,2% | 6,9% |
| leksykon anty-UA (w tym „oba”) | 13,7% | 14,3% |
| leksykon pro-UA (w tym „oba”) | 8,4% | 6,3% |
| anty-UA **i** ton negatywny | 9,4% | 7,0% |
| pro-UA **i** ton pozytywny | 1,4% | 1,9% |
| P(anty-UA \| negatywne) | 16,9% | 17,0% |
| P(neutralne \| anty-UA) | 28,3% | 48,1% |
| P(negatywne \| pro-UA) | 50,3% | 31,3% |

## 3. Trendy w czasie (§3.1, §3.2)

Trend: korelacja rang Spearmana ρ między numerem tygodnia a udziałem (unikalne treści; liczba tygodni z ≥ 30 treściami: 44), p dwustronne.

| Udział treści | ρ | p |
|---|---|---|
| ton negatywny | 0,46 | 0,002 |
| ton pozytywny | -0,37 | 0,013 |
| anty-UA | 0,45 | 0,002 |
| pro-UA | -0,64 | < 0,001 |
| anty-UA i negatywne | 0,48 | < 0,001 |
| pro-UA i pozytywne | -0,37 | 0,013 |

Porównanie okresów: test z dla dwóch proporcji (pooled), unikalne treści, III–IV 2022 vs XI–XII 2022.

| Udział treści | III–IV | XI–XII | różnica (pp) | z | p |
|---|---|---|---|---|---|
| ton negatywny | 52,7% | 58,8% | +6,1 | 5,78 | < 0,001 |
| anty-UA | 11,0% | 14,0% | +3,0 | 4,33 | < 0,001 |
| anty-UA i negatywne | 7,3% | 10,0% | +2,7 | 4,57 | < 0,001 |
| pro-UA | 9,6% | 6,8% | -2,8 | -4,75 | < 0,001 |

## 4. Związki dzienne (§3.1)

Korelacja rang Spearmana po dniach okna (podstawa: wpisy z retweetami), p dwustronne.

| Para zmiennych (dziennie) | ρ | p |
|---|---|---|
| liczba wpisów vs udział negatywnych | -0,26 | < 0,001 |
| liczba wpisów vs udział anty-UA | -0,24 | < 0,001 |
| udział anty-UA vs udział pro-UA | 0,05 | 0,423 |
| udział negatywnych vs udział anty-UA | 0,06 | 0,305 |

## 5. Zaangażowanie oryginałów (§3.3)

Podstawa: tylko oryginały (bez retweetów i odpowiedzi); liczniki z chwili pobrania. Test U Manna–Whitneya, dwustronny.

| Porównanie | Mediana A | Mediana B | p |
|---|---|---|---|
| polubienia: pozytywne (A) vs negatywne (B) | 97 | 59 | 0,004 |
| polubienia: negatywne (A) vs neutralne (B) | 59 | 27 | < 0,001 |
| retweety: anty-UA (A) vs żaden leksykon (B) | 11 | 7 | 0,154 |

## 6. Peaki (§2.6)

Seria: liczba różnych treści dziennie. Liczba peaków przy z = 2 / 2,5 / 3: 12 / 8 / 7. Peaki tej serii pokrywają się z peakami serii wpisów z RT w 1 z 6 dni.

| Dzień | Wpisy | Udział top konta | Udział top kaskady | Negatywne | Wydarzenie (±3 dni) |
|---|---|---|---|---|---|
| 2022-05-15 | 1048 | 35% | 35% | 54% | Eurowizja (+1 d) |
| 2022-05-09 | 877 | 17% | 10% | 58% | ambasador Rosji (farba) (+0 d) |
| 2022-04-09 | 552 | 20% | 20% | 43% | – |
| 2022-05-22 | 367 | 22% | 22% | 15% | – |
| 2022-10-31 | 350 | 49% | 49% | 62% | – |
| 2022-11-16 | 291 | 14% | 14% | 51% | Przewodów (+1 d) |
| 2022-04-17 | 289 | 27% | 25% | 11% | – |
| 2022-07-12 | 155 | 9% | 3% | 48% | – |

## 7. Moc testów (§4.4)

Test główny (korelacja dziennych przyrostów log(1+x), opóźnienia 0–7 dni, jednostronnie, 303 dni, 199 permutacji, 100 powtórzeń symulacji, prawdziwe opóźnienie 2 dni):

| Prawdziwa korelacja ρ | Odsetek wyników z p < 0,05 |
|---|---|
| 0 (brak efektu; powinno być ≈ 5%) | 5% |
| 0,2 | 52% |
| 0,3 | 88% |

Analiza uzupełniająca (dopasowanie peaków, 8 peaków, opóźnienie 3 dni): moc 46% przy 50% peaków z poprzednikiem na Telegramie, 80% przy 80%.
