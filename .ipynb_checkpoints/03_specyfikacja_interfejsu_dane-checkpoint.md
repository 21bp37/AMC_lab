# 03. Specyfikacja interfejsu: pipeline i inżynier danych

Ten dokument mówi, **czego pipeline potrzebuje od inżyniera danych** i **co pipeline sprawdzi po otrzymaniu danych**. Treść merytoryczną dotyczącą źródeł, podstaw prawnych, ramki i data statementu uzupełnia inżynier danych; w miejscach, które do niego należą (oznaczone **[INŻ. DANYCH – DO WYPEŁNIENIA]**), są placeholdery i nie są wypełnione propozycją. Temat: „Jaka jest skala i czas życia reklam scamowych z wizerunkiem znanych osób?”; definicje skali i czasu życia należą do leada (P27, P28).

## 1. Zasada nadrzędna

Wszystkie dane pochodzą z legalnych źródeł, zgodnie z regulaminami stron i licencjami. **Nie używamy scrapowania ani narzędzi do masowego pobierania mediów ze stron**, nawet gdy są popularne w pracach badawczych, jeśli regulamin źródła tego nie dopuszcza. Pierwszym zadaniem inżyniera danych jest macierz legalności (sekcja 3); pipeline nie rusza danych, zanim ją zobaczy.

## 2. Wymagany schemat tabeli (jedna wiersz = jedna reklama w źródle)

Kolumny **wymagane** to minimum do wykonania planu pomiaru (01). Kolumny **warunkowe** zależą od tego, co źródło legalnie udostępnia (punkty D1, D4, D6). Nazwy kolumn można zmienić, ale mapowanie musi być opisane.

| Kolumna | Opis | Wymagana? | Uwagi |
|---|---|---|---|
| `ad_id` | stabilny identyfikator reklamy w źródle | tak | klucz główny |
| `creative_id` | identyfikator unikatowej kreacji po deduplikacji (ten sam tekst/obraz u tego samego reklamodawcy = jedna kreacja) | tak | metoda deduplikacji opisana w data statement |
| `advertiser_id` | stabilny identyfikator reklamodawcy (strony) | tak | klaster w analizie; pseudonimizacja, jeśli wymagana |
| `platform` | platforma emisji | tak | |
| `delivery_start`, `delivery_stop` | początek i koniec emisji (koniec pusty = reklama aktywna lub brak danych; znaczenie opisuje data statement) | tak, jeśli źródło je udostępnia | czas życia (P28); brak = D6 |
| `retrieval_date` | data pobrania rekordu | tak | stan źródła w tym dniu; konieczna do oceny cenzurowania prawostronnego |
| `countries_delivered` | kraje dostarczenia | tak | zakres próby (P01) |
| `ad_text`, `headline`, `link_caption` | tekst reklamy | tak | wejście dla poziomu L1 |
| `language` | język tekstu (metoda detekcji opisana) | tak | D8 |
| `cta_label` | etykieta przycisku wezwania do działania | jeśli dostępna | |
| `dest_url` lub `dest_domain` | adres docelowy | warunkowa | łańcuch dowodu scamu (D4); P05 |
| `reach_*` | zasięg (liczba całkowita lub przedział) | warunkowa | tylko jeśli lead uzna zasięg za część „skali" (P27); P06 |
| `frame_source` | kryterium lub zapytanie, przez które reklama trafiła do ramki | warunkowa | niezależność ramki od annotatora ocenianego (D9, P29) |
| `creative_available` | czy kreacja (obraz/wideo) jest legalnie dostępna | tak | D1 |
| `creative_path` | ścieżka do pliku kreacji | warunkowa | tylko jeśli legalnie wolno |
| `source_removed_flag` | czy źródło oznacza reklamę jako usuniętą/naruszającą zasady | jeśli dostępne | dowód zewnętrzny, nie wynik; R03 |
| `source_name`, `source_version` | skąd i w jakiej wersji | tak | odtwarzalność |

Dostępność poszczególnych pól (według oficjalnej dokumentacji, nie scraperów): {{P06: pola zasięgu, czasu emisji i targetowania dostępne dla reklam komercyjnych | zależy od: oficjalna dokumentacja źródła | domyślnie: nieznane}}.

## 3. Macierz legalności: szkielet

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** Cała macierz.

Jeden wiersz = jedno źródło. Bez wypełnionej macierzy nie rozpoczynamy pracy na danych.

| Źródło | Kto udostępnia | Podstawa (regulamin, licencja, umowa) | Wymagania dostępu (tożsamość, wniosek, umowa uczelni) | Pola dostępne | Kreacje? | Retencja | Co wolno zapisać i publikować | Dane osobowe? | Ocena |
|---|---|---|---|---|---|---|---|---|---|
| {{P07: źródło 1 (np. oficjalne API biblioteki reklam) \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |
| {{P07: źródło 2 (np. Meta Content Library) \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |
| {{P18: źródło 3: Lista Ostrzeżeń CERT Polska i jej warunki użycia \| zależy od: inżynier danych \| domyślnie: brak}} | | | | | | | | | |

Pytania, na które macierz musi odpowiedzieć (lista pytań jest moja, odpowiedzi należą do inżyniera danych):

1. Czy oficjalne API biblioteki reklam zwraca reklamy komercyjne dostarczone w UE i które pola (tekst, daty, adres docelowy, zasięg)? Dokumentacja firm trzecich sugeruje, że reklamy inne niż polityczne są dostępne tylko, jeśli były dostarczone do UE lub Wielkiej Brytanii, i tylko przez ograniczony czas; **to wymaga potwierdzenia w oficjalnej dokumentacji**.
2. Czy regulamin pozwala na zapis i dalsze przetwarzanie kreacji (obraz/wideo)? (D1)
3. Czy uczelnia może złożyć wniosek o Meta Content Library i w jakim terminie? (P20) Według dokumentacji dostęp odbywa się przez ICPSR, wymaga umowy o korzystaniu z danych między ICPSR a instytucją, zabrania eksportu danych z platformy badawczej i uploadu danych do niej; dostępność reklamów w Content Library nie jest przeze mnie potwierdzona.
4. Czy wolno użyć Listy Ostrzeżeń CERT Polska do zestawienia z domenami z reklam i na jakich warunkach? (P18)
5. Czy nazwiska osób publicznych w tekście reklam są danymi osobowymi wymagającymi dodatkowej podstawy w kontekście RODO i jak ograniczyć ich przetwarzanie? (R09)
6. Jakie są ograniczenia retencji i do kiedy dane trzeba pobrać, aby nie zniknęły? (R01)
7. Które pola określają początek i koniec emisji, co oznacza pusty koniec emisji, i czy źródło zwraca reklamy już zakończone lub usunięte oraz na jak długo? (czas życia: P28, R01, R17)
8. Jak zbudowano zbiór reklam kandydujących (kryteria, zapytania, listy) i czy jest to opisane w data statement? (P29, D9)

## 4. Data statement

> **[INŻ. DANYCH – DO WYPEŁNIENIA]** Cały data statement.

Szkielet na podstawie praktyk dokumentacji danych [@bender2018; @gebru2021]. Link i wersja: {{P08: data statement | zależy od: P07 | domyślnie: brak}}. Minimalne pola: cel zbioru, źródło i sposób dostępu, okno dat, kraje i języki, metoda deduplikacji, znane luki i obciążenia, dane osobowe i sposób ich ograniczenia, licencja i warunki użycia, wersja i data pobrania.

## 5. Co pipeline sprawdzi po otrzymaniu danych

Narzędzie: `python tools/audit_dataset.py dane.csv` (opis w README). Sprawdzenia:

1. Zgodność schematu: kolumny wymagane, typy, klucze, duplikaty `ad_id` i `creative_id`.
2. Zakres dat, odsetek brakujących dat końca i pól warunkowych.
3. Liczba reklam, unikatowych kreacji, reklamodawców; koncentracja (udział 10 największych, indeks Herfindahla, efektywna liczba klastrów); wyniki trafiają do P02 i P11.
4. Rozkład języków i krajów (P10, D8), rozkład miesięcy.
5. Dostępność pól czasu emisji i adresu docelowego (P05, P06), dostępność kreacji (P04); udział reklam bez daty końca emisji i rozkład czasu emisji reklam zakończonych (jako opis, bez korekty cenzurowania; P28, D6).
6. Czy jest data statement i wpis w macierzy legalności; **jeśli nie, pipeline zatrzymuje pracę i zgłasza to**.

Wyniki audytu są wpisywane do rejestru placeholderów (00) z odwołaniem do uruchomienia (hash danych w dzienniku).
