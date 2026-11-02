# 07. Bibliografia z adnotacjami i statusem weryfikacji

Oceniane jest poprawne cytowanie, więc każda pozycja ma status. **Zweryfikowane** oznacza: tytuł, autorzy i dane bibliograficzne potwierdzone w źródle w tej sesji (strona wydawcy, repozytorium preprintów lub spis literatury innej pracy), ale nie oznacza, że przeczytałem całą pracę. **Do sprawdzenia** oznacza: informacja z pamięci albo z drugorzędnego źródła; otwórz oryginał przed wpisaniem do preprintu. **Przeczytaj w całości** dotyczy prac, na których opiera się decyzja metodologiczna: znam z abstraktów i opisów, a nie z pełnego tekstu.

Klucze (`@klucz`) są używane w pozostałych dokumentach i w komentarzach narzędzi.

## A. Zgodność annotatorów i walidacja

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `krippendorff2004` | Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage. | Progi α: ≥ 0,800 dane wiarygodne, 0,667–0,800 tylko wnioski wstępne, < 0,667 odrzucić; autor zaleca dobierać próg do kosztu błędnych wniosków | Do sprawdzenia: progi potwierdzone w kilku źródłach wtórnych, nie w samej książce; sprawdź wydanie i numer strony |
| `feinstein1990` | Feinstein, A. R., Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. *J Clin Epidemiol* 43(6), 543–549. | Niska kappa przy wysokiej zgodności i niezrównoważonych brzegach | Zweryfikowane (dane z listy literatury w PMC) |
| `cicchetti1990` | Cicchetti, D. V., Feinstein, A. R. (1990). High agreement but low kappa: II. Resolving the paradoxes. *J Clin Epidemiol* 43(6), 551–558. | Zgodność pozytywna i negatywna jako uzupełnienie kappa | Zweryfikowane (j.w.) |
| `byrt1993` | Byrt, T., Bishop, J., Carlin, J. B. (1993). Bias, prevalence and kappa. *J Clin Epidemiol* 46(5), 423–429. | Indeksy prevalence i bias; zalecenie raportowania ich razem z kappa | Tytuł i autorzy zweryfikowani; czasopismo, tom i strony do sprawdzenia |
| `chen2009` | Chen, G. i in. (2009). Measuring agreement of administrative data with chart data using prevalence unadjusted and adjusted kappa. *BMC Med Res Methodol* 9, 5. doi:10.1186/1471-2288-9-5 | Raportuj kappa, prevalence, zgodność pozytywną i negatywną; PABAK nie mierzy tego samego co kappa przy niskiej prevalence | Tytuł, czasopismo i DOI zweryfikowane; lista autorów do sprawdzenia |
| `donner1987` | Donner, A., Eliasziw, M. (1987). Sample size requirements for reliability studies. *Stat Med* 6, 441–448. | Liczebność badania zgodności przez oczekiwaną szerokość przedziału | Zweryfikowane (spis literatury pakietu kappaSize) |
| `rotondi2012` | Rotondi, M. A., Donner, A. A confidence interval approach to sample size estimation for interobserver agreement studies with multiple raters and outcomes. *J Clin Epidemiol* | j.w. dla wielu annotatorów i kategorii | Tytuł zweryfikowany (pakiet kappaSize); rok, tom i strony do sprawdzenia |

## B. LLM jako annotator w naukach społecznych

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `gilardi2023` | Gilardi, F., Alizadeh, M., Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *PNAS* 120(30), e2305016120. doi:10.1073/pnas.2305016120 | Ten sam codebook dla ludzi i modelu; porównanie z referencją ludzką; **dotyczy tekstu** (tweety, artykuły), n = 6183 łącznie | Zweryfikowane; autorzy sami ostrzegają, że to za wcześnie na zastępowanie annotatorów |
| `ziems2024` | Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., Yang, D. (2024). Can large language models transform computational social science? *Computational Linguistics* 50(1), 237–291. | Realistyczne oczekiwania: LLM nie zastępują w pełni annotacji ludzkiej; κ w zakresie 0,40–0,65 w 8 z 17 zadań (wartość ze streszczenia wtórnego); **tylko zadania tekstowe, angielski** | Zweryfikowane; zakres κ do sprawdzenia w pełnym tekście |
| `halterman2025` | Halterman, A., Keith, K. A. Codebook LLMs: Evaluating LLMs as measurement tools for political science concepts. arXiv:2407.10747 (wersja czasopiśmiennicza: Cambridge University Press) | Ramy pomiaru: przygotuj codebook dla ludzi i modelu, przetestuj podstawowe zdolności, oceń dokładność zero-shot; pozostałe etapy ramy do przeczytania | Preprint zweryfikowany; czasopismo, rok i strony do sprawdzenia; **przeczytaj w całości** |
| `baumann2025` | Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., Hovy, D. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv:2509.08825 | Konfiguracja (prompt, model) zmienia wnioski; ok. 31% hipotez z błędnym wnioskiem dla najlepszych modeli; adnotacje ludzkie zmniejszają ryzyko fałszywie pozytywnych wyników | Preprint zweryfikowany; liczba 31% z abstraktu wersji 2; **przeczytaj w całości** |
| `egami2025dsl` | Egami, N., Hinck, M., Stewart, B. M., Wei, H. Using large language model annotations for the social sciences: A general framework of using predicted variables in downstream analyses. (nagroda Gosnell Prize 2025) | Predykcje modelu analizowane jak obserwacje bez błędu dają obciążenie i nieprawidłowe CI nawet przy dokładności > 90%; metoda DSL łączy predykcje z mniejszą próbą etykiet eksperckich losowaną ze znanymi prawdopodobieństwami | Istnienie, autorzy i teza potwierdzone (abstrakty seminariów, strona nagrody); **wersja wydawnicza, tytuł wersji konferencyjnej i rok do sprawdzenia**; przeczytaj w całości, bo od niej zależy plan analizy |
| `calderon2025` | Calderon, N., Reichart, R., Dror, R. (2025). The alternative annotator test for LLM-as-a-judge: How to statistically justify replacing human annotators with LLMs. *Proc. ACL 2025* (long), 2025.acl-long.782. doi:10.18653/v1/2025.acl-long.782 | Procedura statystyczna uzasadniająca zastąpienie annotatora przez LLM na niewielkim podzbiorze; obejmuje też zadania wizualno-językowe | Zweryfikowane; szczegóły testu (alt-test) do przeczytania |

## C. Temat: dezinformacja antyukraińska, Telegram, opóźnienia między platformami

Do uzupełnienia przez leada i analityka. Wymagane minimum: publikacja lub karta zbioru „Russian and Ukrainian War-related Telegram Channels Dataset” (cytowanie zgodne z licencją zbioru) oraz opis metody zbierania danych z X/Twittera (API v2 for Academic Research, NodeXL). Nie wpisywać pozycji, których nikt nie otworzył.

## D. Wnioskowanie i dokumentacja danych

| Klucz | Pozycja | Co wspiera w planie | Status |
|---|---|---|---|
| `cameron2015` | Cameron, A. C., Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. *Journal of Human Resources* 50(2), 317–372. doi:10.3368/jhr.50.2.317 | Wnioskowanie przy danych klastrowych; przy niewielkiej liczbie klastrów standardowe błędy odporne na klastrowanie zaniżają niepewność i trzeba stosować korekty | Zweryfikowane |
| `gebru2021` | Gebru, T. i in. (2021). Datasheets for datasets. *Communications of the ACM* 64(12), 86–92. | Dokumentacja zbioru danych | Zweryfikowane |
| `bender2018` | Bender, E. M., Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *TACL* 6. | Data statement dla zbiorów językowych | Zweryfikowane |

