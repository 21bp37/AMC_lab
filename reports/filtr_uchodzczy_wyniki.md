# Filtr uchodźczy RU/UK, wyniki diagnostyki (wersja słów 0.1)

Wygenerowane przez `python -m pipeline.telegram_refugee check`. Dotyczy postów UA+PL z pobranych plików; okno 4.03–31.12.2022 (303 dni). Opis działania: `FILTR_UCHODZCZY.md`.

## Pro-Russian

- Posty UA+PL: 80712; po filtrze uchodźczym: 9809 (12%), z 964 kanałów; 10 największych kanałów daje 13%; kopie tego samego tekstu: 33%.
- Udział postów z narracją anty-UA (słownik RU/UK v0.1): przed filtrem 18.3%, po filtrze 32.3%. Filtr nie używa słów ze słownika anty-UA, więc różnica nie wynika z tych samych słów, ale może odzwierciedlać to, że posty o uchodźcach częściej dotyczą świadczeń itp. albo styl kanałów (zob. FILTR_UCHODZCZY.md).

| szereg | mediana/dzień | dni z zerem | dni z ≥3 | średnio/tydzień | najwyższy dzień | werdykt |
|---|---|---|---|---|---|---|
| posty uchodźcze | 24 | 0% | 99% | 223 | 2022-06-02 (261) | dzienny szereg wystarczająco gęsty |
| uchodźcze i anty-UA | 6 | 4% | 81% | 72 | 2022-06-02 (217) | dzienny szereg wystarczająco gęsty |

## Pro-Ukrainian

- Posty UA+PL: 46363; po filtrze uchodźczym: 4720 (10%), z 528 kanałów; 10 największych kanałów daje 19%; kopie tego samego tekstu: 16%.
- Udział postów z narracją anty-UA (słownik RU/UK v0.1): przed filtrem 5.2%, po filtrze 14.9%. Filtr nie używa słów ze słownika anty-UA, więc różnica nie wynika z tych samych słów, ale może odzwierciedlać to, że posty o uchodźcach częściej dotyczą świadczeń itp. albo styl kanałów (zob. FILTR_UCHODZCZY.md).

| szereg | mediana/dzień | dni z zerem | dni z ≥3 | średnio/tydzień | najwyższy dzień | werdykt |
|---|---|---|---|---|---|---|
| posty uchodźcze | 10 | 0% | 97% | 107 | 2022-03-26 (129) | dzienny szereg wystarczająco gęsty |
| uchodźcze i anty-UA | 2 | 23% | 31% | 16 | 2022-06-02 (45) | za mało postów: szeregu nie da się sensownie zbudować (zawęzić projekt) |

## Które kategorie i rdzenie łapią posty (wszystkie strony)

| kategoria | postów |
|---|---|
| uchodzcy | 14287 |
| migranci | 2705 |
| ukraincy_w_polsce | 901 |

Najczęściej trafione fragmenty (do przeglądu: jeśli któryś dominuje i wygląda na szum, usuń go z listy):

| fragment | postów |
|---|---|
| беженц | 11690 |
| біженц | 1654 |
| мигрант | 1282 |
| миграци | 1192 |
| переселенц | 664 |
| беженк | 513 |
| украинцев в польш | 222 |
| міграці | 177 |
| украинцы в польш | 134 |
| временной защит | 101 |
| мігрант | 96 |
| гастарбайтер | 86 |
| вимушених переселен | 81 |
| украинцам в польш | 52 |
| українці в польщ | 49 |

Progi werdyktu są orientacyjne (mediana ≥5 postów dziennie i ≤30% dni z zerem dla testu dziennego; ≥20 tygodniowo dla tygodniowego). Gęstość to nie to samo co trafność: czy posty są o uchodźcach, sprawdza dopiero ręczny przegląd (`score`).
