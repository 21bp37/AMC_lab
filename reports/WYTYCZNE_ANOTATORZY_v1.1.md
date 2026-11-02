# Wytyczne dla anotatorów – wersja 1.1 (tura 2)

**Zadanie:** dla każdego posta wybierz jedną etykietę opisującą postawę autora wobec **uchodźców/Ukraińców w Polsce**. Oceniasz tekst z kolumny `text_pl` (oryginał pomocniczo). Nie zgaduj intencji spoza tekstu.

## Etykiety
| Etykieta | Kiedy |
|---|---|
| `anty` | tekst przedstawia uchodźców/Ukraińców w Polsce negatywnie, wzywa do ograniczeń/wyjazdu, przypisuje im przywileje, przestępczość, nielojalność, pasożytnictwo |
| `pro` | tekst broni uchodźców, wyraża wsparcie/wdzięczność, krytykuje postawy antyuchodźcze |
| `neutralne` | o uchodźcach, ale informacyjnie, bez wyraźnej oceny lub z oceną zrównoważoną |
| `nie_dotyczy` | uchodźcy/Ukraińcy w Polsce nie są tematem (wojna, polityka, historia, wzmianka przelotna) |
| `niejasne` | nie da się ustalić postawy bez kontekstu (ucięty wątek, niejednoznaczna ironia) |

## Reguły
1. **Relacje o wydarzeniach** oceniaj po sposobie ujęcia (dobór słów, pytania sugerujące, dopiski), nie po samym zdarzeniu. Zdarzenie opisane sucho = `neutralne`; opisane z wydźwiękiem negatywnym/pozytywnym = `anty`/`pro`.
2. **Wzmianka przelotna** (Polska/Ukraińcy tylko jako tło) = `nie_dotyczy`.
3. **Krytyka państwa, rządu, armii, polityki wobec Ukrainy** (np. „Polacy zapłacą krwią za Ukrainę”, krytyka PiS, ranking krajów) bez oceny uchodźców = `nie_dotyczy`.
4. **Wojna na Ukrainie, Rosja, Wołyń/historia, kultura** bez wątku uchodźców w Polsce = `nie_dotyczy`, nawet jeśli ton jest proukraiński lub antyukraiński.
5. **Cytaty i polemika:** liczy się stanowisko autora posta. Cytując antyuchodźczą tezę, by ją wyśmiać lub obalić → `pro`; by ją poprzeć → `anty`.
6. **Ironia/sarkazm:** oceniaj sens zamierzony, jeśli jest czytelny; jeśli nie → `niejasne`.
7. **Głosy mieszane** (plusy i minusy bez przewagi) = `neutralne`.
8. **Krytyka Polski/Polaków z perspektywy proRosyjskiej** (np. „gościnność” w cudzysłowie, „junta”) bez oceny uchodźców = `nie_dotyczy`; z oceną uchodźców (np. „nie szukają pracy”, „wynoście się” zachęcająco przedstawione) = `anty`.
9. **Pytanie retoryczne zachęcające do zgody** („Zgadzacie się?”) pod relacją o wrogiej reakcji na uchodźców = `anty`.
10. **Wątpliwość:** `niejasne` tylko gdy po przeczytaniu dwóch interpretacji obie są równie prawdopodobne; nie używaj go zamiast `nie_dotyczy`.

## Praktyka
- Koduj samodzielnie, bez konsultacji z drugim koderem. Wątpliwości zapisz w kolumnie `komentarze` (krótko).
- Nie wyszukuj postów w sieci; nie używaj narzędzi AI do etykietowania.

## tl;dr
Etykietuj postawę autora wobec uchodźców w Polsce; jeśli ich w tekście praktycznie nie ma – `nie_dotyczy`; relacje oceniaj po ujęciu; `niejasne` to ostateczność.
