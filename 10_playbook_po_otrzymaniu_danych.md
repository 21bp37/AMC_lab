# 10. Playbook: co robić po otrzymaniu danych

Kroki w kolejności. Każdy krok kończy się wpisem w rejestrze placeholderów (00) i, jeśli dotyczy, uruchomieniem zapisanym w dzienniku (`tools/run_log.py`). Punkty D1–D9 są zdefiniowane w 00. **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?” **Pytanie badawcze (01):** mediana czasu życia reklam deepfake scam i ich dzienna intensywność wyświetleń (hipoteza: mediana ≤ 2 dni, ponad 50% reklam ≥ 25 tys. wyświetleń na dzień; progi są parametrami).

## Krok 0. Bramka legalności (przed otwarciem danych)

- Jest macierz legalności i data statement od inżyniera danych? ({{P07: macierz legalności | zależy od: inżynier danych | domyślnie: brak}}, {{P08: data statement | zależy od: P07 | domyślnie: brak}})
- Jeśli nie: **stop**, pracujemy tylko na narzędziach i danych syntetycznych. Wynik negatywny o dostępie do danych jest pełnoprawnym wynikiem projektu.

## Krok 1. Audyt tabeli

`python tools/audit_dataset.py dane.csv` → wpisz do P01, P02, P03, P05, P06, P10, P11. Zapisz hash pliku wejściowego w dzienniku.

Reakcje:
- brakuje kolumn wymaganych → zwróć do inżyniera danych z listą (03, sekcja 2);
- nie ma dat początku i końca emisji albo skumulowanych wyświetleń (`reach_total`) → D6 = NIE (czas życia lub dzienna intensywność niemierzalne);
- wyświetlenia podane jako przedziały → zapisz granice (`reach_min`, `reach_max`) i sprawdź, w ilu przypadkach próg T_I wypada w przedziale (R22);
- duży udział reklam bez daty końca → zgłoś do leada i analityka (cenzurowanie, P28, R17);
- adres docelowy niedostępny → D4 = NIE;
- kreacje (wideo) niedostępne → D1 = NIE: populacji „deepfake scam” nie da się zidentyfikować, zgłoś do leada (P30).

## Krok 2. Eksploracja do karty M1

1. Rozkład w czasie, po platformach, krajach i językach (P17, P10; statystyki opisowe dostarcza inżynier danych, pipeline może użyć `audit_dataset.py`).
2. Losowo wybrane 50–100 rekordów przejrzyj ręcznie; zapisz, co zaskoczyło (P17). To jest materiał do poprawy codebooka, nie do dowodzenia.
3. Szacunek prevalence scamu i podejrzenia deepfake'a na tej próbie (P09). Przedział ufności Wilsona: `python tools/sample_size.py wilson --k ... --n ...`. Przy małej próbie przedział jest szeroki; zapisz go.
4. Koncentracja reklamodawców (P11), przybliżone ICC z danych (P12).
5. Wstępne rozkłady L i I na całej ramce (opis, bez korekty): `python tools/outcomes.py dane.csv` (P17); sprawdź udział L = 1 i reklam aktywnych (R17, R21).
6. Decyzja D2: czy jest dość przypadków do planu z 05 (tabela liczebności dla H1 i H2).

## Krok 3. Pilotaż codebooka

1. Wylosuj 30–50 reklam (`tools/sampling.py`, bez limitu warstw; seed w dzienniku).
2. Dwóch annotatorów koduje niezależnie w `templates/annotation_sheet_template.csv`; walidacja: `python tools/checks.py sheet arkusz.csv`.
3. Zgodność: `python tools/agreement.py arkusz.csv --vars celeb_mention scam_type ...` → P13.
4. Spotkanie: omów niezgodności, popraw definicje, wpis w `templates/codebook_changelog.md`, wersja 0.2.
5. Pilotaż 2 na nowej próbie. D3: dla każdej zmiennej wg poniższej tabeli.

## Krok 4. Decyzje po pilotażu

| Wynik | Działanie | Podstawa |
|---|---|---|
| α ≥ 0,80 | zmienna wiarygodna, użyj w analizie | [@krippendorff2004] |
| 0,667 ≤ α < 0,80 | tylko wnioski wstępne; opisz jako takie | [@krippendorff2004] |
| α < 0,667, kategoria rzadka (prevalence < ok. 10–20% w próbie) | sprawdź zgodność pozytywną/negatywną i prevalence index; niskie α może wynikać z niezrównoważenia, a nie z jakości kodowania; nie usuwaj automatycznie | [@feinstein1990; @cicchetti1990; @chen2009]; symulacja w 05 |
| α < 0,667, kategorie zrównoważone, po drugiej rundzie | usuń zmienną z pomiaru; nie nazywaj jej mierzalną (wynik negatywny jest pełnoprawny) | zasady kursu; [@krippendorff2004] |

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

## Krok 7. Wyniki na populacji badanej

1. Populacja = gold standard sklasyfikowany jako deepfake scam (wagi 1/p): `python tools/outcomes.py gold.csv --class-col in_population --weight-col weight --cluster advertiser_id --thr-days 2 --thr-intensity 25000`. Progi to parametry od leada i mogą się zmienić.
2. Ten sam skrypt na reklamach wskazanych przez annotatora ocenianego (estymata naiwna) i porównanie z wynikiem z gold standardu (05, sekcja 5).
3. Wrażliwość: definicja populacji (tylko `yes`; `yes` ∪ `suspected`; `unsure` włączone lub wyłączone), konwencja liczenia dni, granice przedziałów wyświetleń.
4. Pasmo mediany L przy reklamach aktywnych: dolne (obserwowane do dnia pobrania) i górne (nieskończone) ograniczenie. Jeśli pasmo obejmuje próg T_L, hipoteza H1 nie jest rozstrzygnięta.
5. Wpis do rejestru (P32 czeka na regułę decyzyjną od leada i analityka).

## Krok 8. Przekazanie analitykowi

Przekaż: tabelę z predykcjami i etykietami, wagami włączenia, klastrami; opis zmiennych; wyniki walidacji z CI; medianę L i udział I ≥ T_I naiwne i z gold standardu; wyniki analizy błędów po warstwach, po czasie emisji i po intensywności (05, sekcja 5); zakres wrażliwości; ograniczenia. Analityk wdraża model przeżycia dla reklam aktywnych (Kaplan–Meier) i pełną korektę błędu pomiaru dla regresji [@egami2025dsl] (w repozytorium są tylko: wersja uproszczona dla częstości i `tools/outcomes.py` z pasmem mediany; 05, sekcja 6).

## Lista kontrolna przed oddaniem raportu

- [ ] każdy wynik z liczbą ma odtwarzalne uruchomienie w dzienniku
- [ ] precision zawsze razem z prevalence
- [ ] CI przez bootstrap po klastrach
- [ ] zakres po konfiguracjach, nie jedna liczba
- [ ] ograniczenia z 06 przeniesione do preprintu
- [ ] użycie AI opisane (09)
