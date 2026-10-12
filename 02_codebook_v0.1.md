# 02. Codebook v0.1

**Status:** wersja robocza przed pilotażem. Zmiany tylko przez dziennik zmian (`templates/codebook_changelog.md`) i podniesienie wersji. Lista dozwolonych wartości jest w `tools/schema.yaml` (źródło prawdy); po zmianie uruchom `python tools/checks.py consistency`.

**Dlaczego tak:** codebook jest jedną instrukcją dla wszystkich annotatorów (referencyjnych i ocenianego); ta sama wersja służy do annotacji referencyjnej i do promptu annotatora ocenianego, co jest wzorcem z prac porównujących LLM z annotatorami [@gilardi2023; @halterman2025].

**Temat:** Oszustwa z deepfake'ami. **Pytanie projektowe:** „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”. Codebook służy do zaklasyfikowania reklamy do populacji badanej (wzmianka lub wizerunek osoby publicznej, scam) i do podziału na warstwy. Skala i czas życia pochodzą z metadanych, nie z codebooka. Definicje skali, czasu życia i konstruktu „wizerunek” należą do leada (P27, P28, P30): {{P30: konstrukt wizerunku: wzmianka, twarz czy oba | zależy od: lead, D1 | domyślnie: brak}}.

**Rdzeń i zmienne dodatkowe.** Rdzeń: `celeb_mention`, `scam_type`, `scam_judgement`, `celeb_category` oraz (po D1) `celeb_face_visible`, `media_type`, `media_synthetic_suspected` (z pomocniczą `media_synthetic_cue`). Zmienne oznaczone „(dodatkowa)” są poza rdzeniem pytania: opcjonalne i eksploracyjne, kodowane tylko jeśli starczy czasu na pilotaż. Codebook przechodzi co najmniej dwie rundy pilotażu, zanim zostanie zamrożony (05).

**Przykłady poniżej są wymyślone** (fikcyjne osoby, fikcyjne marki) i służą wyłącznie do zilustrowania reguł. Zostaną zastąpione zanonimizowanymi przykładami z pilotażu: {{P23: przykłady z pilotażu do uzupełnienia | zależy od: pilotaż, P07 | domyślnie: przykłady fikcyjne}}.

## Nomenklatura

- **Annotator:** każdy podmiot (osoba lub narzędzie), który stosuje definicje z tego codebooka do pojedynczej reklamy i przypisuje wartości zmiennych. Nie ustala „prawdy”, tylko stosuje zasady.
- **Annotator referencyjny (R1, R2, …):** annotator, którego uzgodnione etykiety tworzą gold standard.
- **Annotator oceniany (O):** annotator, którego jakość sprawdzamy względem gold standardu (w 04 opisany jako wariant A–E).
- **Pilotaż:** próbne kodowanie małej próby reklam przed zamrożeniem codebooka; służy do poprawy definicji, a nie do uzyskania wyników badania.
- **Krippendorff α (alfa):** miara zgodności między kodującymi, skorygowana o zgodność przypadkową. Wartość 1 to pełna zgodność, 0 to zgodność na poziomie losowym. Przyjęte progi [@krippendorff2004]: α ≥ 0,80 zmienna wiarygodna; 0,667 ≤ α < 0,80 tylko wnioski wstępne; α < 0,667 zmiennej nie uznajemy za mierzalną. Dla rzadkich kategorii α może być niskie mimo dobrego kodowania, dlatego sprawdzamy też zgodność pozytywną i negatywną (05).
- **Cohen κ (kappa):** podobna miara dla dwóch kodujących; wymaga tych samych dwóch osób dla całej próby.
- **Gold standard:** próba reklam zakodowana ręcznie i uzgodniona (adjudykowana), względem której oceniamy instrument (05).
- **Zamrożenie codebooka:** po pilotażu wersja i jej hash są ustalone; zmiana wymaga nowej wersji i wpisu w dzienniku zmian.

Jeśli kodowanie wykonuje jedna osoba, α między kodującymi nie da się policzyć; stosujemy wtedy powtórne kodowanie tej samej próby po przerwie i opisujemy to jako ograniczenie (05).

## Zasady ogólne

1. **Jednostka kodowania:** pojedyncza unikatowa kreacja (`creative_id`); kopie tej samej kreacji u tego samego reklamodawcy są deduplikowane przed losowaniem (03, 05).
2. **Kodowanie na ślepo:** annotator nie widzi zasięgu, czasu emisji, wyniku annotatora ocenianego ani dowodów zewnętrznych (lista CERT, usunięcie przez platformę). Powód: znajomość wyniku obciążałaby kodowanie kryteriów populacji.
3. **Kodujemy to, co widać w reklamie**, nie to, co annotator wie z zewnątrz. Wyjątek: rozpoznanie osoby po opisie (`implied`) wymaga jednoznaczności opisu, a nie wiedzy specjalnej.
4. **Kategoria `unsure` jest pełnoprawna.** Wybieraj ją zamiast zgadywać. Odsetek `unsure` jest raportowany; wysoki odsetek oznacza zbyt niejasną definicję.
5. **Dwa poziomy:**
   - **L1** (z tekstu i metadanych): wykonalny bez dostępu do kreacji.
   - **L2** (wizualne): kodowany wyłącznie po potwierdzeniu punktu decyzyjnego D1 (legalny dostęp do kreacji): {{P04: dostępność kreacji i podstawa prawna | zależy od: regulamin źródła | domyślnie: brak dostępu, L2 wyłączony}}.
6. **Ograniczenie konstruktu L1:** temat mówi o *wizerunku*, a poziom L1 mierzy tylko *wzmiankę* o osobie publicznej w tekście. Reklama z twarzą osoby publicznej i bez nazwiska w tekście zostanie na L1 zakodowana jako `none` i wypadnie z populacji, co zaniża skalę. To jest błąd pomiaru kryterium populacji (06, R05) i jest opisany jako ograniczenie, dopóki L2 nie jest dostępny.

## Zmienne poziomu L1

### `celeb_mention` (kryterium populacji)

Czy tekst reklamy (treść, nagłówek, podpis linku, nazwa strony reklamodawcy, widoczna domena) odnosi się do osoby publicznej.

| Wartość | Definicja | Przykład (fikcyjny) | Kontrprzykład |
|---|---|---|---|
| `explicit_name` | Nazwisko, imię i nazwisko lub powszechnie znany pseudonim osoby publicznej występuje w tekście, nagłówku, podpisie linku lub domenie | „Jan Przykładowski ujawnia metodę na 500 zł dziennie" | „Eksperci radzą" (brak osoby) |
| `implied` | Brak nazwiska, ale opis jednoznacznie wskazuje konkretną osobę publiczną | „Prezes największego banku w kraju zdradza..." (jednoznaczne w kontekście) | „Znany biznesmen" (niejednoznaczne; wybierz `unsure` lub `none`) |
| `none` | Brak odniesienia do osoby publicznej | reklama suplementu bez odwołania do osoby | — |
| `unsure` | Nie da się rozstrzygnąć | tekst wspomina „znaną prezenterkę" bez możliwości ustalenia, czy to konkretna osoba | — |

**Przypadki graniczne.** (a) Właściciel marki o tym samym nazwisku co celebryta: `none`, jeśli nic nie wskazuje na osobę publiczną. (b) Postać fikcyjna lub maskotka: `none`. (c) Osoba publiczna wymieniona neutralnie jako element newsa bez sugestii poparcia: `explicit_name`, a rodzaj użycia koduje `celeb_claim`. (d) Osoba zmarła: kodujemy jak żywą. (e) Wymienione kilka osób: `explicit_name`, w `celeb_id` pierwsza wymieniona, reszta w `notes`.

### `celeb_id`

Tekst wolny, znormalizowane nazwisko ("Imię Nazwisko") albo `unrecognized`. Wymagane, gdy `celeb_mention` ∈ {`explicit_name`, `implied`}; puste lub `na`, gdy `none`. **Dane osobowe:** to pole zawiera dane osób, więc jest przechowywane tylko w pliku roboczym i nie trafia do materiałów publicznych; raportujemy tylko `celeb_category` i zagregowane liczby: {{P07: podstawa prawna przetwarzania nazwisk osób publicznych | zależy od: ocena inżyniera danych | domyślnie: pole nieraportowane publicznie}}.

### `celeb_category`

| Wartość | Definicja |
|---|---|
| `politician` | polityk, urzędnik, osoba pełniąca funkcję publiczną |
| `business_finance` | przedsiębiorca, bankier, osoba ze świata finansów |
| `sport` | sportowiec, trener |
| `media_entertainment` | aktor, prezenter, artysta, dziennikarz |
| `influencer` | twórca internetowy znany głównie z platform |
| `other` | osoba publiczna spoza powyższych |
| `na` | gdy `celeb_mention` = `none` albo `unsure` |

Przypadek graniczny: osoba należąca do dwóch kategorii. Wybierz tę, w której osoba występuje w reklamie.

### `celeb_claim` (mechanizm; dodatkowa)

Co reklama każe zrozumieć o stosunku osoby do oferty.

| Wartość | Definicja | Przykład (fikcyjny) |
|---|---|---|
| `fabricated_quote` | Reklama przypisuje osobie cytat lub wypowiedź | „Jan Przykładowski: «To zmieniło moje życie»" |
| `fabricated_event` | Reklama opisuje zdarzenie z udziałem osoby (rzekomy wywiad, skandal, program TV) | „Po wizycie w studiu prezenter ujawnił..." |
| `product_recommendation` | Osoba rzekomo poleca lub używa produktu bez cytatu | „Ulubiony suplement Jana Przykładowskiego" |
| `none` | Osoba wymieniona, ale bez przypisanego stosunku do oferty | |
| `unsure` | Nie da się rozstrzygnąć | |

Gdy `celeb_mention` = `none`, zostaw puste. Reguła pierwszeństwa przy kilku mechanizmach: `fabricated_quote` > `fabricated_event` > `product_recommendation`.

### `fake_news_format` (dodatkowa)

`yes`, jeśli reklama naśladuje artykuł prasowy, wiadomość lub wywiad (nagłówek w stylu serwisu informacyjnego, „źródło: ..."), `no`, jeśli to czytelna reklama produktu, `unsure` przy wątpliwości. Przypadek graniczny: reklama z ramką „artykuł sponsorowany" ale stylizacją newsa: `yes`.

### `scam_type`

Typ oferty wynikający z treści reklamy.

| Wartość | Definicja |
|---|---|
| `investment_crypto` | inwestycje, kryptowaluty, „platformy", obietnica zysku z kapitału |
| `health_supplements` | suplementy, „cudowne" kuracje, produkty zdrowotne z nierealnymi obietnicami |
| `giveaway_contest` | rzekome nagrody, konkursy, rozdawanie produktów |
| `benefits_subsidies` | rzekome dopłaty, świadczenia, odszkodowania |
| `shop_counterfeit` | sklep z nierealnie niskimi cenami, podróbki |
| `other` | inny rodzaj oferty |
| `not_scam` | oferta wygląda na legalną |
| `unclear` | nie da się ustalić typu oferty |

Zmienna oznacza *typ oferty*, a nie dowód oszustwa. `not_scam` i `unclear` pozwalają zakodować również reklamy, które okażą się legalne. Przypadek graniczny: oferta łącząca dwa typy (np. suplement z konkursem): typ głównej obietnicy w nagłówku.

### `scam_judgement`

Ocena annotatora, czy reklama wygląda na oszukańczą (`scam`, `not_scam`, `unclear`) na podstawie wyłącznie reklamy. **Nie zastępuje dowodu zewnętrznego.** Służy jako zmienna pomocnicza i do analizy zgodności między oceną annotatora referencyjnego a dowodem zewnętrznym (sprawdzian, czy łatwo odróżnić scam od legalnej reklamy).

### `urgency_cue` (dodatkowa)

`yes`, jeśli reklama stosuje presję czasu lub rzadkości („tylko dziś", „zostało 3 sztuki", odliczanie), `no`, jeśli nie, `unsure` przy wątpliwości.

### `guaranteed_return_claim` (dodatkowa)

`yes`, jeśli reklama obiecuje pewny zysk, brak ryzyka lub konkretną stopę zwrotu („gwarantowany zysk", „bez ryzyka", „2000 zł tygodniowo"), `no`, jeśli nie, `unsure` przy wątpliwości.

### `authority_cue` (dodatkowa)

Na czym reklama opiera wiarygodność.

| Wartość | Definicja |
|---|---|
| `celebrity` | wiarygodność oparta na osobie publicznej (jej opinii, doświadczeniu) |
| `institution_or_expert` | instytucja, rzekomy ekspert, „badania naukowe", lekarz |
| `none` | brak odwołania do autorytetu |
| `unsure` | nie da się rozstrzygnąć |

Reguła: jeśli występują oba, wybierz dominujący (wyróżniony w nagłówku lub pierwszy w tekście). Zmienna jest zależna od `celeb_mention` (przy `celeb_mention` = `none` wartość `celebrity` jest niedozwolona; to jest też kontrola jakości).

### `cta_type` (dodatkowa)

Wezwanie do działania: `learn_more`, `sign_up`, `buy`, `download`, `contact`, `other`, `none`. Jeśli jest kilka, wybierz główne (przycisk reklamy ma pierwszeństwo przed tekstem).

## Zmienne poziomu L2 (tylko po D1)

Kodowane wyłącznie wtedy, gdy kreacje są legalnie dostępne: {{P04: dostępność kreacji | zależy od: regulamin źródła | domyślnie: niedostępne}}.

### `media_type`

`image`, `video`, `carousel`, `text_only`, `unavailable` (kreacja nie jest dostępna mimo włączonego L2).

### `celeb_face_visible` (kryterium populacji L2)

`yes`, jeśli na kreacji widać twarz osoby, którą annotator referencyjny uznaje za osobę publiczną **bez** pomocy zewnętrznych narzędzi rozpoznawania twarzy i bez ustalania, kim jest; `no`; `unsure`; `na_no_media`. **Nie używamy automatycznego rozpoznawania twarzy** (identyfikacja po twarzy to przetwarzanie danych biometrycznych objęte zakazem z art. 9 ust. 1 RODO bez przesłanki z ust. 2; szczegóły w 04, zasada 4). Zmienną koduje wyłącznie annotator referencyjny (osoba); annotator oceniany jej nie koduje. Wartością rezerwową jest `unsure`.

### `media_synthetic_suspected`

Ocena annotatora referencyjnego, czy kreacja (obraz lub wideo) wygląda na wygenerowaną lub zmanipulowaną (deepfake, obraz wygenerowany, podmiana twarzy lub głosu). Zmienna oznacza **podejrzenie, nie ustalenie**: z samego materiału nie da się wiarygodnie stwierdzić, że jest deepfake'iem (06, R19), a wartość `yes` nie znaczy „dowiedziono deepfake'a”. Zmienna jest opisowa; nie służy do określania populacji badanej, dopóki lead nie rozstrzygnie P30.

| Wartość | Definicja |
|---|---|
| `yes` | co najmniej jedna wyraźna przesłanka, którą można wskazać w kreacji (zob. `media_synthetic_cue`), bez równie prawdopodobnego wyjaśnienia innego niż synteza |
| `suspected` | słaba lub niejednoznaczna przesłanka (np. wygładzona skóra, dziwny ruch warg w jednym ujęciu), możliwe też inne wyjaśnienie (filtr, kompresja, retusz, animacja) |
| `no` | kreacja wyświetlona dobrej jakości, bez przesłanek syntezy |
| `unsure` | nie da się ocenić: niska rozdzielczość, bardzo krótki kadr, brak dźwięku przy ocenie ruchu ust, kreacja uszkodzona |
| `na_no_media` | brak obrazu lub wideo (kreacja tylko tekstowa albo niedostępna) |

Zasady rozstrzygania:
1. Oceniamy to, co widać i słychać w kreacji. Nie szukamy źródła obrazu, nie używamy narzędzi do wykrywania deepfake'ów ani rozpoznawania twarzy, nie ustalamy, kim jest osoba na materiale (04, zasada 4).
2. `yes` wymaga przesłanki, którą annotator potrafi nazwać w `media_synthetic_cue`; samo „wygląda dziwnie” to najwyżej `suspected`.
3. Jeśli reklama zawiera tylko obraz statyczny, ocena dotyczy obrazu; brak możliwości oceny ruchu ust nie jest przesłanką za ani przeciw (wtedy `no` albo `unsure`, zależnie od jakości obrazu).
4. W razie wahania między `yes` a `suspected` wybierz `suspected`; między `suspected` a `no`, gdy nie umiesz nazwać żadnej przesłanki, wybierz `no`; gdy jakość uniemożliwia ocenę, wybierz `unsure`, nie `no`.
5. Karuzela: oceń wszystkie karty; wartość to najwyższy poziom podejrzenia spośród nich (kolejność `yes` > `suspected` > `no`), `unsure` tylko gdy żadna karta nie pozwala na ocenę.

Przypadki brzegowe:
- **Znana osoba z ewidentnie nierealnego kontekstu** (np. wypowiada się w sprawie inwestycji, której nigdy nie promowała): to treść fałszywego poparcia (`celeb_claim`), nie dowód syntezy obrazu; sama treść nie uzasadnia `yes`.
- **Retusz, filtr beauty, sztuka cyfrowa, ilustracja, animacja, grafika AI wyraźnie niefotograficzna**: kodujemy `no` dla deepfake'a w sensie wizerunku osoby; jeśli kreacja jest jawnie oznaczona jako wygenerowana, patrz `platform_label` poniżej.
- **Oznaczenie przez platformę lub reklamodawcę** („wygenerowano przez AI”): zapisz `platform_label` w `media_synthetic_cue`; wartość `media_synthetic_suspected` ustaw na `yes`, jeśli oznaczenie dotyczy osoby na materiale, w pozostałych przypadkach `no`. Brak oznaczenia nie jest przesłanką za `no`.
- **Montaż z archiwalnych nagrań** (zmiana głosu, przycięty wywiad) bez oznak syntezy: `suspected` tylko wtedy, gdy ruch warg lub głos wyraźnie nie pasują; inaczej `no`.
- **Podróbka, sobowtór, aktor**: z materiału nie da się odróżnić od syntezy; `no` albo `suspected`, zależnie od przesłanek. Nie ustalamy tożsamości.
- **Wideo bez dźwięku lub z wyciętą ścieżką**: ruch ust nie może być jedyną przesłanką; ocena na podstawie obrazu, a przy złej jakości `unsure`.

### `media_synthetic_cue`

Zmienna pomocnicza do `media_synthetic_suspected`: **główna przesłanka**, na której oparto ocenę (jeśli kilka, wybierz najsilniejszą). Pozwala sprawdzić, na czym annotator opiera podejrzenie, i analizować niezgodności między annotatorami.

| Wartość | Definicja |
|---|---|
| `visual_artifact` | artefakty obrazu: zniekształcone dłonie, zęby, uszy, okulary, krawędzie twarzy, niespójne światło lub cienie, mrugnięcie lub mimika nienaturalne |
| `lip_audio_mismatch` | ruch warg nie pasuje do wypowiadanego tekstu |
| `voice_unnatural` | głos metaliczny, monotonny lub niespójny z osobą i obrazem |
| `platform_label` | oznaczenie treści jako wygenerowanej lub zmanipulowanej (platforma lub reklamodawca) |
| `other` | inna przesłanka (opisz w `notes`) |
| `none` | brak przesłanki (przy `no`, `unsure`) |
| `na` | brak mediów (przy `na_no_media`) |

Reguły spójności (sprawdza `python tools/checks.py sheet`): przy `yes` i `suspected` wartość `none` i `na` jest niedozwolona; przy `no` i `na_no_media` przesłanka musi być `none` lub `na` (albo pusta).

## Pola z dowodami zewnętrznymi (nie kodowane przez annotatorów)

Wypełnia pipeline na podstawie danych i list publicznych, po zakończeniu kodowania kryteriów populacji: `dest_domain`, `domain_on_cert_list`, `cert_list_interval`, `platform_removal` (definicje w `tools/schema.yaml`). Dostępność zależy od P05, P18, P19.

## Procedura

1. Pilotaż 1 (30–50 reklam, każdy annotator referencyjny koduje samodzielnie), potem omówienie niezgodności, korekta definicji, wersja 0.2 z wpisem w dzienniku zmian.
2. Pilotaż 2 na nowej próbie; jeśli zmienna wciąż nie osiąga α ≥ 0,667, usuń ją z pomiaru (10, punkt D3).
3. Dopiero po zamrożeniu codebooka losowanie i annotacja zbioru gold standardu (05).
4. Każda zmiana po zamrożeniu = nowa wersja + powtórna ocena na próbie kontrolnej.
