# Dziennik zmian pomiaru (leksykon, klasyfikator, definicje szeregów)

Każda zmiana definicji zmiennej wynikowej (leksykon narracji, próg piku, model sentymentu/klasyfikator, filtr tematu) = wpis i nowa wersja.

| Wersja | Data | Kto | Co zmieniono | Dlaczego (dowód: przykłady, wynik walidacji) | Wpływ na wyniki |
|---|---|---|---|---|---|
| leksykon 0.1 | 2026-10-19 | pipeline | wersja eksploracyjna 6 narracji (`pipeline/config.py`); usunięto „wdzięczn*” (fałszywe trafienia w podziękowaniach) | eksploracja M1 | brak walidacji, tylko opis |
| leksykon 0.2 | 2026-10-19 | pipeline | + leksykon pro-UA (pomoc, solidarność, wdzięczność); negacja wdzięczności („nie widać wdzięczności”) liczy się jako anty-UA, nie pro-UA; + „podatnik” w narracji o świadczeniach | wiralowy wpis anty-UA (512 RT) był liczony jako pro-UA i zawyżał udział pro-UA w grudniu | udziały pro-UA w XII spadają; trendy liczone na unikalnych treściach |
