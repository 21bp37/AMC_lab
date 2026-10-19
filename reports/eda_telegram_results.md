# Eksploracja Telegrama (opisowa; dane mogą być niepełne)

- Pliki postów uwzględnione: [1, 2, 3, 4, 5] (z 8)
- Posty po filtrze (UA+PL, 2022-03-04..2022-12-31): 113077, kanały: 2153
- Zakres dat: 2022-03-04 .. 2022-12-31; udział postów z kanałów bez etykiety: 12.0%
- Unikalne teksty (80 znaków): 77316

| strona | kanały | posty | mediana/dzień | dni bez postu | anty-UA | wyśw. (mediana) | przek. (mediana) | top-10 kanałów | powtórzenia |
|---|---|---|---|---|---|---|---|---|---|
| Pro-Russian | 971 | 58244 | 159 | 0% | 17.8% | 9522 | 16 | 16% | 34% |
| Pro-Ukrainian | 691 | 41310 | 110 | 0% | 4.9% | 11845 | 14 | 14% | 20% |
| unlabeled | 491 | 13523 | 34 | 0% | 11.8% | 386 | 1 | 31% | 18% |

## Trend udziału anty-UA (Spearman, tygodnie z n>=10, opisowo)
- Pro-Russian: rho=-0.22, p=0.157, tygodni=44
- Pro-Ukrainian: rho=-0.14, p=0.379, tygodni=44
- unlabeled: rho=-0.05, p=0.752, tygodni=44

## Peaki w szeregu prorosyjskim (z>2.5)

```
       day    n  top_channel_share  anti_share            event
2022-04-28  520           0.026923    0.128846                 
2022-06-17  299           0.023411    0.163880                 
2022-07-11  396           0.025253    0.285354                 
2022-11-16 2207           0.016765    0.053919 Przewodów (+1 d)
2022-11-30  432           0.020833    0.141204                 
2022-12-15  292           0.027397    0.133562                 
```
