# Eksploracja Telegrama (opisowa; dane mogą być niepełne)

- Pliki postów uwzględnione: [1, 2, 3, 4, 5, 6, 7, 8] (z 8)
- Posty po filtrze (UA+PL, 2022-03-04..2022-12-31): 143675, kanały: 2966
- Zakres dat: 2022-03-04 .. 2022-12-31; udział postów z kanałów bez etykiety: 11.6%
- Unikalne teksty (80 znaków): 93907

| strona | kanały | posty | mediana/dzień | dni bez postu | anty-UA | wyśw. (mediana) | przek. (mediana) | top-10 kanałów | powtórzenia |
|---|---|---|---|---|---|---|---|---|---|
| Pro-Russian | 1464 | 80712 | 224 | 0% | 18.3% | 6956 | 12 | 11% | 37% |
| Pro-Ukrainian | 834 | 46363 | 121 | 0% | 5.2% | 11251 | 14 | 13% | 20% |
| unlabeled | 668 | 16600 | 41 | 0% | 11.2% | 616 | 1 | 25% | 18% |

## Trend udziału anty-UA (Spearman, tygodnie z n>=10, opisowo)
- Pro-Russian: rho=-0.23, p=0.134, tygodni=44
- Pro-Ukrainian: rho=-0.13, p=0.387, tygodni=44
- unlabeled: rho=-0.06, p=0.718, tygodni=44

## Peaki w szeregu prorosyjskim (z>2.5)

```
       day    n  top_channel_share  anti_share            event
2022-04-28  731           0.019152    0.120383                 
2022-06-17  426           0.021127    0.152582                 
2022-07-11  538           0.018587    0.291822                 
2022-11-16 3005           0.012313    0.056905 Przewodów (+1 d)
2022-11-30  616           0.014610    0.126623                 
2022-12-15  409           0.019560    0.146699                 
```
