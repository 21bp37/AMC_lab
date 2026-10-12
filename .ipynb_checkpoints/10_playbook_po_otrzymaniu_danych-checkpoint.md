# 10. Playbook: co robić po otrzymaniu danych

Kroki w kolejności. Każdy krok kończy się wpisem w rejestrze placeholderów (00) i, jeśli dotyczy, uruchomieniem zapisanym w dzienniku (`tools/run_log.py`). Punkty D1–D9 są zdefiniowane w 00. Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”

## Krok 0. Bramka legalności (przed otwarciem danych)

- Jest macierz legalności i data statement od inżyniera danych? ({{P07: macierz legalności | zależy od: inżynier danych | domyślnie: brak}}, {{P08: data statement | zależy od: P07 | domyślnie: brak}})
- Jeśli nie: **stop**, pracujemy tylko na narzędziach i danych syntetycznych. Wynik negatywny o dostępie do danych jest pełnoprawnym wynikiem projektu.

## Krok 1. Audyt tabeli

`python tools/audit_dataset.py dane.csv` → wpisz do P01, P02, P03, P05, P06, P10, P11. Zapisz hash pliku wejściowego w dzienniku.

Reakcje:
- brakuje kolumn wymaganych → zwróć do inżyniera danych z listą (03, sekcja 2);
- nie ma dat początku i końca emisji → D6 = NIE (czas życia niemierzalny); zasięg jest potrzebny tylko, jeśli lead włączył go do definicji skali (P27);
- duży udział reklam bez daty końca → zgłoś do leada i analityka (cenzurowanie, P28, R17);
- adres docelowy niedostępny → D4 = NIE;
- kreacje niedostępne → D1 = NIE.

## Krok 2. Eksploracja do karty M1

1. Rozkład w czasie, po platformach, krajach i językach (P17, P10; statystyki opisowe dostarcza inżynier danych, pipeline może użyć `audit_dataset.py`).
2. Losowo wybrane 50–100 rekordów przejrzyj ręcznie; zapisz, co zaskoczyło (P17). To jest materiał do poprawy codebooka, nie do dowodzenia.
3. Szacunek prevalence wzmianki o osobie publicznej i scamu na tej próbie (P09). Przedział ufności Wilsona: `python tools/sample_size.py wilson --k ... --n ...`. Przy małej próbie przedział jest szeroki; zapisz go.
4. Koncentracja reklamodawców (P11), przybliżone ICC z danych (P12).
5. Decyzja D2: czy jest dość przypadków do planu z 05.

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

## Krok 7. Przekazanie analitykowi

Przekaż: tabelę z predykcjami i etykietami, wagami włączenia, klastrami; opis zmiennych; wyniki walidacji z CI; estymatę skali naiwną i skorygowaną; wyniki analizy błędów po warstwach i po czasie emisji (05, sekcja 5); zakres wrażliwości; ograniczenia. Analityk wdraża pełną korektę błędu pomiaru dla regresji lub modelu czasu życia [@egami2025dsl] (w repozytorium jest tylko wersja uproszczona dla częstości; 05, sekcja 6).

## Lista kontrolna przed oddaniem raportu

- [ ] każdy wynik z liczbą ma odtwarzalne uruchomienie w dzienniku
- [ ] precision zawsze razem z prevalence
- [ ] CI przez bootstrap po klastrach
- [ ] zakres po konfiguracjach, nie jedna liczba
- [ ] ograniczenia z 06 przeniesione do preprintu
- [ ] użycie AI opisane (09)
