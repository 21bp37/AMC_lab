# Wariant: wolumen tematu „o uchodźcach” (bramka v0.4), X vs Telegram

Mierzy wspólną uwagę do tematu, NIE negatywne treści ani narrację. Reguła: (a) p<0,05 dla RU, (b) test tygodniowy ten sam znak, (c) RU>UA (przedział różnicy bez 0). Kopie i dni wydarzeń sprawdzane w wariantach.

## Gęstość szeregów

| szereg | n | mediana/dzień | dni z zerem | peak | werdykt |
|---|---|---|---|---|---|
| x_about | 9901 | 27 | 0% | 2022-05-09 (189) | dzienny szereg wystarczająco gęsty |
| x_about_strict | 1287 | 3 | 8% | 2022-03-17 (33) | za rzadki na test dzienny; wystarczy test tygodniowy |
| tg_ru_about | 4788 | 11 | 1% | 2022-06-02 (152) | dzienny szereg wystarczająco gęsty |
| tg_ru_about_strict | 4485 | 10 | 1% | 2022-06-02 (152) | dzienny szereg wystarczająco gęsty |
| tg_ua_about | 2653 | 6 | 3% | 2022-03-25 (73) | dzienny szereg wystarczająco gęsty |
| tg_ua_about_strict | 2248 | 5 | 5% | 2022-03-26 (71) | dzienny szereg wystarczająco gęsty |

## Test hipotezy

| wariant | r RU (k) | p RU | r UA | p UA | tyg. ρ | RU−UA [95%] | a | b | c | H |
|---|---|---|---|---|---|---|---|---|---|---|
| główny: unikalne, bramka v0.4 | 0.05 (4) | 0.89 | 0.07 | 0.72 | -0.03 | -0.03 [-0.13; 0.11] | – | – | – | nie |
| z kopiami (nie tylko unikalne) | 0.07 (4) | 0.67 | 0.15 | 0.19 | 0.48 | -0.07 [-0.19; 0.09] | – | + | – | nie |
| bez filtra (cały temat UA+PL) | 0.09 (0) | 0.64 | 0.15 | 0.03 | 0.08 | -0.05 [-0.13; 0.05] | – | + | – | nie |
| udziały (o uchodźcach / temat) | 0.08 (0) | 0.71 | 0.08 | 0.58 | 0.03 | 0.00 [-0.13; 0.11] | – | + | – | nie |
| ścisła bramka (tylko rzeczownik uchodźczy) | 0.11 (5) | 0.29 | 0.18 | 0.03 | 0.09 | -0.07 [-0.18; 0.07] | – | + | – | nie |
| Telegram: filtr v0.3 | 0.07 (4) | 0.67 | 0.11 | 0.30 | -0.01 | -0.05 [-0.15; 0.11] | – | – | – | nie |
| bez 2.06.2022 | 0.07 (6) | 0.65 | 0.07 | 0.77 | 0.03 | 0.00 [-0.12; 0.14] | – | + | – | nie |
| bez dni wydarzeń ±1 | 0.05 (6) | 0.92 | 0.06 | 0.84 | -0.09 | -0.01 [-0.13; 0.13] | – | – | – | nie |

Interpretacja: korelacja nie dowodzi wpływu; wspólny bodziec (wydarzenia) jest głównym zagrożeniem, stąd wariant bez dni wydarzeń.
