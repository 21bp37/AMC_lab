# 04. Plan instrumentu pomiarowego

Instrument, czyli **annotator oceniany (O)**, koduje zmienne codebooka (02) na dużej liczbie reklam. Klasyfikuje reklamy do populacji badanej (wzmianka lub wizerunek osoby publicznej, scam) i do warstw (typ scamu, kategoria osoby). **Skala i czas życia reklam pochodzą z metadanych**, nie od annotatora ocenianego, więc jego zadanie jest wąskie i walidowalne. **Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”
## Nomenklatura

- **Annotator:** każdy podmiot (osoba lub narzędzie), który stosuje codebook do reklamy i przypisuje wartości zmiennych.
- **Annotator referencyjny (R):** tworzy gold standard. **Annotator oceniany (O):** to, co sprawdzamy (instrument); wariant A–E poniżej opisuje, czym jest O.- **Poziom L1 / L2:** L1 to zmienne mierzalne z tekstu i metadanych; L2 to zmienne wymagające obrazu lub wideo, dostępne tylko po decyzji D1.
- **Gold standard:** próba reklam zakodowana ręcznie i uzgodniona, względem której oceniamy instrument (05).
- **Prevalence:** udział reklam z daną cechą w próbie lub populacji. Precision zależy od prevalence, więc bez niej nie da się jej interpretować.
- **CI (przedział ufności):** zakres prawdopodobnych wartości wielkości w populacji; szeroki przy małej próbie. W ocenie instrumentu liczymy go bootstrapem po klastrach (reklamodawcach), bo reklamy tego samego reklamodawcy nie są niezależne.
- **Flip rate:** odsetek reklam, którym zmiana promptu lub konfiguracji modelu zmienia etykietę; miara wrażliwości instrumentu.

## 1. Zasady

1. Annotator oceniany jest **hipotezą do sprawdzenia**, a nie założeniem. Literatura o LLM jako annotatorach dotyczy głównie **tekstu i angielskiego**: Gilardi i in. (tweety i artykuły, n = 6183 łącznie) [@gilardi2023], Ziems i in. (benchmarki tekstowe, angielskie; według streszczenia wtórnego κ w zakresie 0,40–0,65 w 8 z 17 zadań klasyfikacji, a LLM zwykle nie zastępują w pełni annotacji ludzkiej) [@ziems2024]. Dla reklam z obrazem i polskim tekstem nie mamy równorzędnego wsparcia, więc zgodność trzeba zmierzyć u siebie (05).
2. Ten sam codebook dla wszystkich annotatorów, wersjonowany i zamrożony przed oceną [@gilardi2023; @halterman2025].
3. Każde uruchomienie jest zapisane w dzienniku (`tools/run_log.py`): model, wersja, parametry, seed, hash promptu, hash danych, hash codebooka. Powód: wyniki modeli z API zmieniają się w czasie, a konfiguracja wpływa na wnioski [@baumann2025].
4. **Bez rozpoznawania twarzy.** Identyfikacja celebryty opiera się na tekście; na poziomie L2 wizualnym ocenia wyłącznie annotator referencyjny (02, `celeb_face_visible`), bez ustalania tożsamości po twarzy. Powód prawny: automatyczne rozpoznawanie osoby po twarzy to przetwarzanie danych biometrycznych w celu jednoznacznej identyfikacji, czyli szczególnej kategorii danych, której przetwarzanie **jest zakazane na podstawie art. 9 ust. 1 RODO**, chyba że zachodzi jeden z wyjątków z art. 9 ust. 2 (np. wyraźna zgoda, cele naukowe z podstawą w prawie i zabezpieczeniami); sama fotografia nie jest daną biometryczną, dopóki nie jest przetwarzana specjalnym środkiem technicznym umożliwiającym jednoznaczną identyfikację (motyw 51). Organ holenderski uznał w 2024 r. przetwarzanie danych biometrycznych przez Clearview AI za naruszenie art. 9 ust. 1 i nałożył karę 30,5 mln EUR [@edpb2024clearview; @rodo2016motyw51]. **Nie znaleźliśmy w tym projekcie przesłanki z art. 9 ust. 2, która pozwalałaby na takie rozpoznawanie** (ocena własna, nie opinia prawna; potwierdzić z IOD uczelni, P07), więc **nie stosujemy żadnego narzędzia (w tym VLM) do ustalania tożsamości osoby na podstawie twarzy**, ani w kodzie, ani w promptach. Prompty VLM nie mogą zawierać pytań o to, kim jest osoba na obrazie; zob. też 06, R09.
5. **Bez scrapowania.** Annotator oceniany działa na tabeli dostarczonej przez inżyniera danych z legalnego źródła (03). Nie pobieramy mediów ze stron reklam, jeśli regulamin źródła tego nie dopuszcza ({{P04: legalność pobierania kreacji | zależy od: regulamin źródła | domyślnie: nie pobieramy}}).

## 2. Macierz alternatyw

Ocena jakościowa do wypełnienia po pilotażu; kolumny „ryzyka" to ustalenia już teraz.

| Wariant | Poziom | Zalety | Ograniczenia i ryzyka | Warunek użycia |
|---|---|---|---|---|
| A. Baseline słownikowy: lista osób publicznych + dopasowanie wzorców | L1 | Prosty, w pełni odtwarzalny, tani; konieczny jako punkt odniesienia | Nie wykryje wariantów pisowni, odmian, opisów (`implied`); zależy od jakości listy: {{P25: źródło i licencja listy osób publicznych \| zależy od: licencja \| domyślnie: brak}} | zawsze |
| B. LLM tekstowy z promptem z codebooka | L1 | Radzi sobie z opisami i odmianami; wzorzec jak w literaturze [@gilardi2023; @ziems2024] | Wrażliwość na prompt i wersję [@baumann2025]; koszt i limity: {{P16: koszt i limity \| zależy od: P02, P15 \| domyślnie: nieznane}}; polski mniej przebadany niż angielski | domyślny wariant dla L1 |
| C. Model otwarty uruchamiany lokalnie | L1/L2 | Pełna kontrola wersji, odtwarzalność, brak wysyłania danych na zewnątrz; ewentualnie jedyny wariant w środowisku bez eksportu | Zwykle słabszy; wymaga zasobów obliczeniowych; mniej wygodny | gdy środowisko danych wyklucza zewnętrzne API: {{P20: środowisko analizy \| zależy od: uczelnia \| domyślnie: nieznane}} |
| D. Multimodalny LLM (VLM) dla obrazu i tekstu | L2 | Jedyny wariant do `media_type`, `media_synthetic_suspected`, `media_synthetic_cue` | **Brak równorzędnej walidacji w literaturze dla tego zadania**; zbiory pokrewne to chińskie media społecznościowe i inne zadania [@chasm2026; @adsprofiles2025], przeczytaj je w całości przed użyciem jako wzorca; ryzyko dla `media_synthetic_suspected` (wykrywanie deepfake'ów jest trudne; wartość `suspected` to podejrzenie, R19) | tylko po D1 (legalny dostęp do kreacji) |
| E. Annotacja wyłącznie przez annotatorów referencyjnych na próbie + estymacja korygowana | L1/L2 | Najlepsza wiarygodność | Mała próba, szerokie CI | wariant zapasowy, gdy B/C/D nie osiągną zgodności (D5) |

## 3. Drzewo decyzji

1. **D1: czy kreacje są legalnie dostępne?**
   - **Nie** (scenariusz domyślny, dopóki nie ma dowodu): wyłącznie L1; warianty A, B lub C, zawsze z wariantem A jako punktem odniesienia. Konstrukt zawęża się do *wzmianki o celebrycie* (02, zasada 6).
   - **Tak:** dodatkowo L2; wariant D dla `media_type`, a `celeb_face_visible` koduje wyłącznie annotator referencyjny (annotator oceniany nie ocenia tożsamości osób na obrazie).
2. **Środowisko analizy** (P20): jeśli dane są dostępne wyłącznie w środowisku bez eksportu i bez wywołań zewnętrznych API, wariant C lub E.
3. **D5 po pilotażu:** jeśli zgodność annotatora ocenianego z gold standardem jest zbliżona do zgodności annotatorów referencyjnych między sobą (kryterium: 05, sekcja 5), użyj do całości z korektą błędu; w przeciwnym razie wariant E.

## 4. Prompt: reguły wersjonowania

- Prompty są plikami w repozytorium (`prompts/`), nazwa `prompt_<zmienna>_v<N>.txt`. Zmiana = nowy plik, nie nadpisanie.
- Treść promptu zawiera codebook dla zmiennej (definicje, wartości, przykłady, kontrprzykłady, reguły graniczne) bez dodawania własnych reguł, których nie ma w codebooku. Prompt nie jest drugim codebookiem.
- Dla każdej zmiennej: wartości dozwolone wymuszamy formatem wyjścia (np. JSON z listą wartości), odpowiedź spoza listy jest błędem i jest liczona.
- Parafrazy: dla każdego promptu przygotowujemy co najmniej 2 parafrazy do oceny wrażliwości (05, sekcja 5, punkt 3) [@baumann2025].
- Dobór promptu odbywa się na zbiorze rozwijania; zbiór testowy jest nietykalny do końca (05).

## 5. Dziennik uruchomień

Pola: czas UTC, kto, model i wersja, parametry, seed, plik i hash promptu, plik i hash danych wejściowych, plik i hash codebooka, wersja Pythona, uwagi. Komenda: `python tools/run_log.py ...` (opis w pliku). Dziennik jest też materiałem dowodowym przy obronie indywidualnej (09).

## 6. Wybór annotatora ocenianego: do wypełnienia po pilotażu

> **[PIPELINE – DO WYPEŁNIENIA po pilotażu]**

- Wybrany annotator oceniany (wariant) i uzasadnienie: {{P15: instrument (nazwa, wersja, parametry) | zależy od: D1, D5, P20 | domyślnie: wariant A + B}}
- Wynik pierwszego testu względem gold standardu: {{P14: P/R/F1 z CI, zgodność z annotatorami | zależy od: pilotaż | domyślnie: brak}}
- Koszt i czas przetworzenia całości: {{P16: koszt i limity | zależy od: P02, P15 | domyślnie: nieznane}}
