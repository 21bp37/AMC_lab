# Filtr uchodźczy RU/UK (Telegram): opis działania i sprawdzanie

Wersja słów: **0.1** (szkic, `TELEGRAM_REFUGEE_VERSION` w `pipeline/config.py`). Kod: `pipeline/telegram_refugee.py`.

## 1. Po co

Obecny filtr Telegrama wybiera posty, które wspominają **Ukrainę i Polskę**. Takie posty to głównie wojna i geopolityka
(największy peak, 16.11.2022, to Przewodów), a nie uchodźcy. Hipoteza dotyczy uchodźców, więc szereg `X^RU_t` z samego filtra UA+PL
mierzy bardziej uwagę na wojnie niż na uchodźcach. Filtr uchodźczy dokłada **trzeci warunek**:

```
post  =  wspomina Ukrainę  ORAZ  wspomina Polskę  ORAZ  mówi o uchodźcach / migrantach / Ukraińcach w Polsce
```

Działa na już pobranych i przefiltrowanych plikach (`data/telegram/posts_2022_part_*.csv`), więc **nie trzeba pobierać 49 GB od nowa**.

## 2. Zasada projektowa: filtr mówi KTO, nie CO

Filtr rozpoznaje **temat (kto jest bohaterem posta)**, a nie **narrację (co się o nim mówi)**. Dlatego na liście nie ma słów ze słownika
anty-UA (świadczenia, przestępczość, „nahlebniki” itd.). Gdyby były, to w przefiltrowanych postach udział „anty-UA” rósłby mechanicznie,
bo post przechodziłby filtr właśnie przez słowo, które potem liczy się jako narracja anty-UA. Test `test_filter_does_not_contain_anti_lexicon_words`
pilnuje, żeby żaden rdzeń z listy nie trafiał w `TELEGRAM_ANTI_UA`.

## 3. Co jest na liście (`TELEGRAM_REFUGEE_TERMS`)

Rdzenie słów, bez końcówek, więc łapią wszystkie odmiany (w rosyjskim i ukraińskim słowa mocno się odmieniają). Wielkość liter nie ma znaczenia.

| kategoria | rdzenie | uwagi |
|---|---|---|
| `uchodzcy` | RU: `беженц`, `беженк`, `беженств`, `беженск`, `переселенц`, `вынужденн* переселен`, `временн* защит`, `просител* убежищ`; UK: `біженц`, `біженк`, `біженств`, `біженськ`, `вимушен* переселен`, `тимчасов* захист`, `шукач* притулку` | status uchodźcy, ochrona czasowa, wysiedleńcy |
| `migranci` | RU: `мигрант`, `миграци`, `гастарбайтер`; UK: `мігрант`, `міграці`, `заробітчан` | migranci, emigranci, pracownicy sezonowi („мигрант” zawiera się w „эмигрант”, „иммигрант”) |
| `ukraincy_w_polsce` | RU: `украин[цк]*` + najwyżej 1 słowo + `в/во польш`; UK: `україн[цк]*` + najwyżej 1 słowo + `в/у/до польщ` | „Ukraińcy w Polsce” jako jedno wyrażenie; wzorzec nie przekracza kropki ani nie łapie „Ukraińcy odbili atak, w Polsce…” |

Post przechodzi, jeśli pasuje **którakolwiek** kategoria.

**Celowo pominięte** (zbyt wiele szumu): `убежище` (to także schron), `допомога` (to także pomoc wojskowa), `украинцы` samo (dominuje w wiadomościach z frontu),
`выплаты`, `пособия` (to narracja, nie temat).

## 4. Znane źródła fałszywych trafień (do sprawdzenia w przeglądzie)

- **Kryzys na granicy polsko-białoruskiej:** migranci z Bliskiego Wschodu, post wspomina Ukrainę i Polskę przy okazji.
- **Wysiedleńcy wewnątrz Ukrainy** („переселенцы” z Donbasu) w poście, który wspomina też Polskę.
- **„миграци…”** w kontekście polityki migracyjnej UE, niezwiązanej z Ukraińcami.
- Lista pisana **bez znajomości języków** (tłumaczenia kluczowych słów, sprawdzone na kilku przykładach), więc jest szkicem do poprawy po przeglądzie.

## 5. Jak uruchomić i sprawdzić

Domyślne ścieżki jak w `eda_telegram`: `data/telegram/posts_2022_part_*.csv` i `data/telegram/leiden_clusters.csv`.

### Krok 1. Automatyczna diagnostyka (bez udziału człowieka)

```bash
python -m pipeline.telegram_refugee check --translator none
```

Zapisuje:
- `reports/filtr_uchodzczy_wyniki.md`: ile postów zostaje po filtrze, ile kanałów, udział kopii, mediana dzienna, odsetek dni z zerem,
  największy dzień (i czy to nadal Przewodów), najczęstsze trafione rdzenie, werdykt o gęstości szeregu;
- `data/processed/telegram_refugee_daily.csv`: szereg dzienny (`day, side, n_topic, n_refugee, n_refugee_anti`) do testu hipotezy
  (`pipeline.telegram.side_series(daily, side, col="n_refugee")`);
- `annotation_work/filtr_przeglad.xlsx` i `.csv`: 80 postów do przeglądu ręcznego (patrz krok 2b).

**Jak czytać werdykt gęstości** (progi orientacyjne, do zmiany w `density_verdict`):
- mediana ≥ 5 postów dziennie i ≤ 30% dni z zerem → test dzienny ma sens;
- mniej, ale ≥ 20 postów tygodniowo → tylko test tygodniowy;
- mniej → szeregu nie da się sensownie zbudować; wtedy zgodnie z kartą M1 zawężamy projekt do dynamiki narracji w X.

Sprawdzamy dwa szeregi: **wszystkie posty uchodźcze** (słabsza wersja hipotezy) oraz **uchodźcze z narracją anty-UA** (pełna hipoteza).

Automat **nie** powie, czy posty są naprawdę o uchodźcach. Do tego potrzebny jest człowiek.

### Krok 2. Ręczne sprawdzenie trafności (potrzebne, ok. 80 postów)

Są dwie drogi, wystarczy jedna.

**2a. Zalecana: jedna anotacja do dwóch celów** (pro/anty oraz filtr uchodźczy). Etykieta `nie_dotyczy` znaczy „post nie jest o Ukraińcach / uchodźcach
w Polsce”, czyli to jest odpowiedź „nie” na pytanie o uchodźców; `anty`, `pro`, `neutralne` to odpowiedź „tak”. Próba z Telegramu zawiera posty
przepuszczone i odrzucone przez filtr, więc z tych samych etykiet liczy się precyzję i czułość filtra:

```bash
python -m pipeline.annotation_sample --coders A B --translator google
# koderzy wypełniają kolumnę „etykieta” w annotation_work/anotacja_A.xlsx i anotacja_B.xlsx
python -m pipeline.annotation_check --annotations annotation_work/anotacja_A.xlsx annotation_work/anotacja_B.xlsx
```
W raporcie `annotation_work/wyniki_anotacji.md` jest sekcja **3b. Filtr uchodźczy** (precyzja, odsetek pominiętych, czułość, z przedziałami),
a błędy filtra w `annotation_work/bledy_filtra.csv` (FP = przepuszczony, ale poza tematem; FN = odrzucony, ale o uchodźcach).

**2b. Alternatywa: osobny, szybki przegląd** (jedna osoba, ok. 20–30 minut), jeśli nie robicie jeszcze pełnej anotacji:

```bash
python -m pipeline.telegram_refugee check --translator google    # tworzy annotation_work/filtr_przeglad.xlsx
# w kolumnie o_uchodzcach wpisz: tak / nie / niejasne   (instrukcja na drugim arkuszu)
python -m pipeline.telegram_refugee score
```
Wynik: `reports/filtr_uchodzczy_przeglad.md` (precyzja, odsetek pominiętych wśród odrzuconych, szacowana czułość) i
`annotation_work/filtr_uchodzczy_bledy.csv`.

## 6. Jak czytać wyniki i co robić dalej

| wynik | co zrobić |
|---|---|
| precyzja < 0,7 | zawęź rdzenie dające fałszywe trafienia (tabela „fragmenty stojące za FP” w raporcie), podnieś `TELEGRAM_REFUGEE_VERSION`, powtórz na **nowej** próbie |
| czułość < 0,5 | dopisz rdzenie z tekstów typu FN (po rosyjsku i ukraińsku, z odmianami), podnieś wersję, powtórz na nowej próbie |
| oba w normie, szereg gęsty | używamy `n_refugee` (wolumen) i `n_refugee_anti` (narracja) w teście hipotezy |
| oba w normie, szereg za rzadki | test tygodniowy albo zawężenie projektu do X (karta M1, sekcja „Wprost”) |

Przy ~20 postach na komórkę przedziały ufności są szerokie, więc wynik to sygnał, nie dowód. Czułość jest szacowana z rzadkich trafień w puli odrzuconych
i jest szacunkiem zgrubnym; wynik rozsądniej czytać razem z przykładami z `bledy_*.csv`.

**Zasada uczciwości:** listę poprawiamy na podstawie jednej próby, a ocenę powtarzamy na **nowej**, wylosowanej po zmianie. Zmiany zapisujemy w sekcji 8.

## 7. Ograniczenia

- Lista powstała bez znajomości rosyjskiego i ukraińskiego (tłumaczenia słów i przegląd po tłumaczeniu maszynowym), więc może pomijać slang i regionalne warianty.
- Filtr działa na postach, które już przeszły warunek „Ukraina i Polska”; posty o uchodźcach bez wzmianki o Polsce nie wchodzą (świadoma decyzja, żeby szereg odpowiadał polskiemu kontekstowi).
- Strona kanału (pro-rosyjski / pro-ukraiński) pochodzi z klasteryzacji autorów zbioru i dotyczy kanału, nie posta.
- Tłumaczenie maszynowe w przeglądzie może zniekształcać sens; kolumna „tlumaczenie” (ok / słabe) pozwala to odnotować.

## 8. Historia zmian listy

| wersja | zmiana |
|---|---|
| 0.1 | pierwszy szkic: 3 kategorie (uchodźcy, migranci, „Ukraińcy w Polsce”); bez słów narracji |
