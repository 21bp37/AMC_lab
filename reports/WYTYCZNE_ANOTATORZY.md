# Wytyczne dla anotatorów

**TL;DR:** Dla każdego posta wpisz w kolumnie `etykieta` jedną z pięciu wartości, oceniając samą treść posta (nie autora, nie kanał) i nie konsultując się z drugim koderem. Liczy się wydźwięk wobec Ukraińców i uchodźców w Polsce, także gdy post tylko „relacjonuje wydarzenie”.

## 1. Co robisz

Plik zawiera posty z X (po polsku) i z Telegramu (po rosyjsku lub ukraińsku, z tłumaczeniem maszynowym w kolumnie `tekst_pl`). Dla każdego wiersza:

1. Przeczytaj `tekst_pl` (w razie wątpliwości co do sensu zajrzyj do `tekst_oryg`).
2. Wybierz z listy jedną etykietę w kolumnie `etykieta`.
3. Opcjonalnie: jeśli tłumaczenie jest zniekształcone, wpisz `słabe` w kolumnie `tlumaczenie` (inaczej `ok` lub puste).

Nie zmieniaj kolejności wierszy ani kolumny `id`. Nie rozmawiaj z drugim koderem o konkretnych postach, dopóki nie oddacie plików.

## 2. Etykiety

| etykieta | kiedy |
|---|---|
| `anty` | Post ma **wyraźnie negatywny wydźwięk** wobec Ukraińców lub uchodźców w Polsce: przedstawia ich jako problem, zagrożenie, obciążenie, roszczeniowych, przeciwstawia ich Polakom, uogólnia pojedyncze zdarzenia na całą grupę. |
| `pro` | Post **broni lub wspiera** Ukraińców / uchodźców w Polsce, apeluje o pomoc dla nich, przeciwstawia się wrogości wobec nich. |
| `neutralne` | Post jest **o Ukraińcach lub uchodźcach w Polsce**, ale bez oceny: sucha informacja, komunikat, relacja bez uogólnień i wartościujących słów. |
| `nie_dotyczy` | Post **nie jest o Ukraińcach ani uchodźcach jako ludziach w Polsce**: front, polityka, gospodarka, katastrofy itp., nawet jeśli pada w nim „Ukraina” i „Polska”. Dotyczy to także krytyki lub poparcia wyłącznie dla **państwa i armii ukraińskiej** (np. Zełenski), bez odniesienia do ludności w Polsce. |
| `niejasne` | Naprawdę nie da się rozstrzygnąć (urwany tekst, nieczytelne tłumaczenie, sarkazm, którego nie rozumiesz). Używaj rzadko. |

## 3. Posty, które „tylko przytaczają wydarzenia”

Sama forma relacji nie decyduje o etykiecie. Pytanie brzmi: **jaki obraz tej grupy wyniesie czytelnik?**

- Sucha relacja o Ukraińcach/uchodźcach w Polsce, bez oceny → `neutralne`.
- Relacja o wydarzeniu niezwiązanym z nimi → `nie_dotyczy`.
- Relacja z doborem faktów lub słów, który kreuje negatywny obraz grupy → `anty`.
- Relacja, która kreuje pozytywny obraz grupy lub wzywa do wsparcia → `pro`.

Przykłady (wymyślone, dla ilustracji):

| treść | etykieta |
|---|---|
| „Ukrainiec pobił Polaka w Krakowie, policja zatrzymała sprawcę.” (sucha relacja) | `neutralne` |
| „Kolejny napad ukraińskich uchodźców, rząd milczy.” | `anty` |
| „Uchodźcy dostaną 800+, a Polacy stoją w kolejkach.” | `anty` |
| „W Warszawie otwarto punkt pomocy dla uchodźców.” | `neutralne` |
| „Zbieramy ciepłe ubrania dla rodzin z Ukrainy, każda pomoc się liczy!” | `pro` |
| „Wybuch w Przewodowie, rakieta spadła na wieś.” | `nie_dotyczy` |
| „Zełenski znowu żąda więcej broni.” | `nie_dotyczy` |

## 4. Trudne przypadki

- **Cytat:** oceniaj stanowisko autora posta, nie cytowanej osoby. Jeśli autor cytuje, żeby skrytykować lub obalić, oceniaj to, co autor chce przekazać.
- **Ironia i sarkazm:** oceniaj zamierzony sens. Jeśli nie jesteś pewien, wybierz `niejasne`.
- **Mieszany post** (część pozytywna, część negatywna): wybierz ton dominujący. Jeśli nie ma dominującego, `neutralne`.
- **Wątpliwości, czy wydźwięk jest „wyraźny”:** wybierz `neutralne`. Etykieta `anty` lub `pro` ma oznaczać przypadki, które dwóch koderów rzeczywiście uzna za wrogie lub życzliwe.
- **Emoji, hashtagi, linki:** liczy się treść. Samego linku bez komentarza nie oceniaj po jego domniemanej zawartości.
- **Tłumaczenie maszynowe:** może zniekształcać sens, więc przy wątpliwościach zajrzyj do oryginału lub oznacz `słabe`.
- **Autor i kanał są nieistotne.** Nie zgaduj etykiety po tym, kto napisał. Ten sam post ma dostać tę samą etykietę niezależnie od źródła.

## 5. Czego nie robimy

- Nie oceniamy, czy post jest prawdziwy.
- Nie oceniamy własnych poglądów na temat uchodźców.
- Nie szukamy dodatkowych informacji o poście w internecie.
- Nie zostawiamy pustych komórek (jeśli nie wiesz, wpisz `niejasne`).

## 6. Po wypełnieniu

Zapisz plik pod tą samą nazwą (`anotacja_<kod>.xlsx`) i odeślij. Zgodność koderów liczy się potem poleceniem `python -m pipeline.annotation_check`; przypadki sporne wrócą do wspólnego rozstrzygnięcia.
