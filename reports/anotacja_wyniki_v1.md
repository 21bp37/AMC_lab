# Weryfikacja etykiet pro / anty

Treści w próbie: 100 (X 50, Telegram 50). Koderzy wzorca: A, B.
Braki etykiet: A: 0, B: 0.

> Filtr uchodźczy PRZELICZONY aktualnymi regułami (50 postów Telegrama), na tych samych etykietach. Wagi zostają z losowania (domena filtra jest podzbiorem warstw), ale to jest ocena na zbiorze, na którym poprawiano listę: zawyżona.

## 1. Zgodność koderów

κ Cohena: 0 = zgodność losowa, 1 = pełna. κ5 = pięć etykiet, κ3 = anty / pro / inne. Przedziały: 95%, bootstrap po treściach. Próba jest celowo wzbogacona w rzadkie klasy, więc κ dotyczy tej próby, nie populacji.

| zbiór | para | n | % zgodności | κ5 / alfa | κ3 |
|---|---|---|---|---|---|
| Wszystko | A-B | 100 | 73% | 0.61 [0.49; 0.73] | 0.60 [0.42; 0.75] |
| Wszystko | alfa (wszyscy) | 100 | – | 0.61 [0.49; 0.73] |  |
| X | A-B | 50 | 74% | 0.64 [0.47; 0.80] | 0.67 [0.47; 0.85] |
| X | alfa (wszyscy) | 50 | – | 0.64 [0.48; 0.81] |  |
| Telegram | A-B | 50 | 72% | 0.55 [0.38; 0.71] | 0.35 [-0.05; 0.67] |
| Telegram | alfa (wszyscy) | 50 | – | 0.55 [0.35; 0.72] |  |

Rozkład etykiet u koderów:

| etykieta | A | B |
|---|---|---|
| anty | 21 | 20 |
| pro | 7 | 7 |
| neutralne | 21 | 17 |
| nie_dotyczy | 44 | 51 |
| niejasne | 7 | 5 |

Tłumaczenia oznaczone jako „słabe” przez któregokolwiek kodera: 1.

## 2. Etykieta referencyjna

Ustalona dla 100 z 100 treści; do rozstrzygnięcia: 0 (plik do_rozstrzygniecia.csv: uzupełnij etykieta_final i uruchom ponownie z --resolved). Nierozstrzygnięte treści są pomijane w ocenie słownika.

Etykieta referencyjna w warstwach próby (liczby treści):

| platform | stratum | N w populacji | anty | pro | neutralne | nie_dotyczy | niejasne | n |
|---|---|---|---|---|---|---|---|---|
| Telegram | Pro-Russian|anti|bez | 6658 | 0 | 0 | 0 | 4 | 0 | 4 |
| Telegram | Pro-Russian|anti|uch | 2011 | 2 | 0 | 3 | 3 | 0 | 8 |
| Telegram | Pro-Russian|inne|bez | 36350 | 0 | 0 | 0 | 6 | 0 | 6 |
| Telegram | Pro-Russian|inne|uch | 4361 | 2 | 0 | 2 | 4 | 0 | 8 |
| Telegram | Pro-Ukrainian|anti|bez | 1343 | 0 | 0 | 0 | 4 | 0 | 4 |
| Telegram | Pro-Ukrainian|anti|uch | 560 | 0 | 1 | 3 | 3 | 0 | 7 |
| Telegram | Pro-Ukrainian|inne|bez | 30928 | 0 | 0 | 1 | 5 | 0 | 6 |
| Telegram | Pro-Ukrainian|inne|uch | 3288 | 0 | 0 | 4 | 3 | 0 | 7 |
| X | anti | 2553 | 8 | 1 | 3 | 3 | 0 | 15 |
| X | brak | 15732 | 3 | 2 | 2 | 8 | 2 | 17 |
| X | mieszane | 213 | 1 | 0 | 0 | 3 | 1 | 5 |
| X | pro | 1485 | 3 | 2 | 1 | 7 | 0 | 13 |

## 3. Jakość klasyfikatorów względem etykiety referencyjnej

Wagi = 1 / prawdopodobieństwo włączenia, więc precyzja, czułość i prevalence dotyczą populacji treści, z której losowaliśmy (unikalne treści X w oknie; unikalne teksty Telegrama po filtrze Ukraina+Polska). CI: bootstrap w obrębie warstw. Czułość opiera się na rzadkich trafieniach w warstwie „brak / inne”, więc jej przedział jest zwykle szeroki.

| zbiór | klasa | klasyfikator | n | oznaczone | prawdziwe | precyzja | czułość | F1 | prevalence (wzorzec) |
|---|---|---|---|---|---|---|---|---|---|
| X | anty | słownik | 50 | 20 | 15 | 0.51 [0.28; 0.74] | 0.28 [0.12; 0.69] | 0.36 | 0.270 |
| X | pro | słownik | 50 | 18 | 5 | 0.13 [0.00; 0.33] | 0.12 [0.00; 1.00] | 0.13 | 0.103 |
| Telegram | anty | słownik | 50 | 23 | 4 | 0.07 [0.00; 0.16] | 0.39 [0.00; 1.00] | 0.12 | 0.020 |
| Telegram / Pro-Russian | anty | słownik | 26 | 12 | 4 | 0.09 [0.00; 0.21] | 0.39 [0.00; 1.00] | 0.15 | 0.025 |
| Telegram / Pro-Ukrainian | anty | słownik | 24 | 11 | 0 | 0.00 [0.00; 0.00] | – [–; –] | – | 0.000 |
| Telegram / po filtrze uchodźczym | anty | słownik | 21 | 11 | 4 | 0.30 [0.00; 0.60] | 0.39 [0.00; 1.00] | 0.34 | 0.219 |
| Telegram / Pro-Russian / po filtrze uchodźczym | anty | słownik | 13 | 7 | 4 | 0.42 [0.00; 0.82] | 0.39 [0.00; 1.00] | 0.40 | 0.301 |

## 3b. Filtr uchodźczy RU/UK (Telegram), ocena z tych samych etykiet

Post „o uchodźcach” = etykieta referencyjna anty / pro / neutralne; „nie_dotyczy” = poza tematem; „niejasne” liczymy na niekorzyść filtra (wśród przepuszczonych jak poza tematem, wśród odrzuconych jak możliwy brak). Wagi i bootstrap w warstwach jak wyżej.

| zbiór | oceniono (przep. / odrz.) | precyzja | pominięte wśród odrzuconych | czułość |
|---|---|---|---|---|
| razem | 21 / 29 | 0.66 [0.39; 0.96] | 0.08 [0.00; 0.23] | 0.47 [0.21; 1.00] |
| Pro-Russian | 13 / 13 | 0.54 [0.22; 0.95] | 0.00 [0.00; 0.00] | 1.00 [1.00; 1.00] |
| Pro-Ukrainian | 8 / 16 | 1.00 [1.00; 1.00] | 0.44 [0.00; 0.80] | 0.27 [0.08; 1.00] |

Słownik a etykieta referencyjna, X (liczby w próbie, bez wag):

| lex | anty | pro | neutralne | nie_dotyczy | niejasne |
|---|---|---|---|---|---|
| słownik: anty | 8 | 1 | 3 | 3 | 0 |
| słownik: brak | 3 | 2 | 2 | 8 | 2 |
| słownik: oba | 1 | 0 | 0 | 3 | 1 |
| słownik: pro | 3 | 2 | 1 | 7 | 0 |

Słownik a etykieta referencyjna, Telegram (liczby w próbie, bez wag):

| lex | anty | pro | neutralne | nie_dotyczy | niejasne |
|---|---|---|---|---|---|
| słownik: anty | 2 | 1 | 6 | 14 | 0 |
| słownik: brak | 2 | 0 | 7 | 18 | 0 |

Fałszywe trafienia i braki słownika: bledy_leksykonu.csv (60 wierszy). Słowa najczęściej stojące za fałszywymi trafieniami „anty”:

| zbiór | słowo | fałszywe | trafne |
|---|---|---|---|
| X | napad | 2 | 0 |
| X | upa | 2 | 1 |
| X | gwałt | 1 | 1 |
| X | bandero | 1 | 2 |
| X | szczepi | 1 | 1 |
| X | bezczeln | 1 | 1 |
| X | niewdzięcz | 1 | 0 |
| X | socjal | 1 | 2 |
| Telegram | нацист | 6 | 0 |
| Telegram | насил | 6 | 0 |
| Telegram | бесплатн | 4 | 2 |
| Telegram | бандер | 3 | 0 |
| Telegram | пособи | 3 | 1 |
| Telegram | укроп | 2 | 0 |
| Telegram | преступн | 2 | 0 |
| Telegram | хохл | 2 | 0 |

## 4. Wnioski według reguły z karty M1

Progi (do zmiany w wywołaniu): κ3 ≥ 0.4, precyzja ≥ 0.7. Przy ~100 treściach przedziały są szerokie, więc traktuj to jako sygnał, nie dowód.

- X: κ3 = 0.67 ≥ 0.4, zgodność koderów wystarczająca do porównań ze słownikiem.
- **Telegram: κ3 = 0.35 < 0.4.** Kategorie nie są jednoznaczne dla koderów: popraw instrukcję (przykłady przypadków granicznych), zakoduj nową próbę i dopiero wtedy oceniaj słownik.
- Filtr uchodźczy: precyzja 0.66 [0.39; 0.96] < 0.7: zawęź rdzenie dające fałszywe trafienia (typ FP w bledy_filtra.csv); czułość 0.47 [0.21; 1.00] < 0.5: dopisz brakujące rdzenie (typ FN w bledy_filtra.csv).
- **X: precyzja „anty” = 0.51 [0.28; 0.74] < 0.7:** przejrzyj bledy_leksykonu.csv, popraw słownik (v0.3 z wpisem w changelogu) i zwaliduj na NOWEJ próbie.
- **Telegram: precyzja „anty” = 0.07 [0.00; 0.16] < 0.7:** **nie interpretujemy narracji z Telegramu**, testujemy tylko wolumen tematu.
- **Telegram po filtrze uchodźczym: precyzja „anty” = 0.30 [0.00; 0.60] < 0.7:** **nie interpretujemy narracji z Telegramu**, testujemy tylko wolumen tematu.
