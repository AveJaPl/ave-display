# Ave Text: krój do akapitów w parze z Ave Display

Data: 2026-11-07. Decyzje Filipa oznaczone **(Filip)**, reszta to decyzje projektowe Claude'a,
które można zmienić.

## Po co

Ave Display jest krojem wystawowym (same wersaliki, pochylenie 28°, trzon 34% wysokości litery)
i nie da się nim złożyć akapitu. Filip potrzebuje kroju do tekstu ciągłego, który
będzie pasował do nagłówków w Ave Display, tak żeby strony i aplikacje miały jedną rodzinę
krojów zamiast pary Ave Display + Geist. **(Filip)**

## Kierunek

Wybór z porównania sześciu krojów złożonych z nagłówkami Ave Display **(Filip)**:

- **kształty jak w Sairze**: kanciaste brzuszki (zaokrąglony prostokąt), to samo O co w Ave Display,
- **rytm, odstępy i kursywa jak w Exo 2**: techniczny charakter, luźne odstępy, kursywa z własnymi formami liter,
- **normalna szerokość**: Titillium Web było „zbyt wąskie”.

Saira i Exo 2 to wzorce proporcji, nie konturów. Ave Text jest rysowany od zera, bo Ave Display
ma zastrzeżone prawa i nie może opierać się na cudzych konturach (obie referencje są na OFL).

Z Ave Display przechodzi do Ave Text: kanciaste O z zaokrąglonymi narożnikami, wysokość
wersalików 700 j., metryki pionowe (950/-250) i ścięcie końcówek pod kątem pochylenia (28°).

**Wariant C (Filip, 2026-11-07)**, wybrany z trzech na prototypie: końcówki c, e, s, t, l, r, f, a, g, j
i cyfr cięte równolegle do trzonów Ave Display (`cut = tan 28°`) oraz większe narożniki prawy górny
i lewy dolny (`asym = 1.3`), jak w Ave Display. Filip widział niewielkie różnice między A (czysty) i C;
wybór jest odwracalny (dwa parametry w `style.py`), więc wracamy do niego po Bold i kursywie.

## Pomiary referencji (przeskalowane do wersalików 700 j.)

| | Saira 400 | Exo 2 400 | Saira 700 | Exo 2 700 |
|---|---|---|---|---|
| wysokość x | 519 | 494 | 519 | 501 |
| trzon n / H | 83 / 87 | 86 / 89 | 164 / 177 | 150 / 155 |
| kreska pozioma o | 70 | 73 | 124 | 109 |
| szerokość n (advance) | 609 | 589 | 601 | 610 |
| światła n / o | 88 / 66 | 78 / 56 | 63 / 45 | 60 / 41 |
| przestrzał o | 8 | 12 | 8 | 13 |
| spacja | 239 | 226 | 257 | 219 |
| kursywa | 12°, a jednopiętrowe | 8°, a jednopiętrowe, f z ogonkiem | | |

Skrypt pomiarowy: skaner poziomych i pionowych linii po konturach (fontTools), uruchamiany na instancjach
400/700 krojów zmiennych.

## Parametry startowe Ave Text

| parametr | Regular | Bold |
|---|---|---|
| UPM / wersaliki | 1000 / 700 | 1000 / 700 |
| wysokość x | 510 | 510 |
| wydłużenia górne / dolne | 740 / -210 | 740 / -210 |
| przestrzał (o, O, c…) | 10 | 10 |
| trzon małych / wielkich liter | 84 / 88 | 152 / 162 |
| kreska pozioma | ~72 (0,86 trzonu) | ~120 (0,78 trzonu) |
| światło n / o | 80 / 62 | 62 / 44 |
| spacja | 230 | 230 |
| metryki linii (typo/hhea/win) | 950 / -250, lineGap 0, USE_TYPO_METRICS | jw. |

Kursywa: **10°** (między Exo 2 a Sairą), pochylenie wokół połowy wysokości x, z formami alternatywnymi:
jednopiętrowe **a** i **f** z ogonkiem pod linią pisma. **l z ogonkiem** na dole w obu odmianach
(rozróżnia I, l i 1 w akapicie). Wartości są punktem startu, a ostateczne liczby ustala się na podglądach.

## Zakres

- **Style** (komplet do akapitów, „RIBBI”): Regular, Italic, Bold, Bold Italic, połączone w jedną rodzinę
  (nameID 1/2, fsSelection, macStyle), żeby `<strong>` i `<em>` wybierały właściwe pliki.
- **Znaki**: pełne strony kodowe Windows-1252 (Europa Zachodnia) i Windows-1250 (Europa Środkowa, w tym
  polskie znaki), czyli ASCII, Latin-1, Œ œ Š š Ž ž Č č Ř ř Ő ő Ű ű Ů ů itd., polska typografia („ ” ‚ ’ … — –),
  € ™ © ® § ¶ • † ‰ ‹ › « », znaki matematyczne z tych stron (± × ÷ ¬ µ ¹ ² ³ ¼ ½ ¾).
- **Akcenty** w dwóch wersjach: dla małych liter i spłaszczone dla wielkich.
- **Cyfry**: proporcjonalne domyślnie, tabelaryczne przez `font-feature-settings: "tnum"` (ceny, tabele).
- **Kerning**: klasy (grupy kształtów) z wartościami liczonymi z profili glifów i sprawdzanymi na podglądach.
- **Hinting**: ttfautohint, bo krój będzie czytany w 14–18 px, także na Windowsie.
- **Pliki**: TTF i WOFF2 dla każdego stylu w `dist/`.

Poza zakresem: font zmienny, cyrylica i greka, kapitaliki, ligatury. Kod ma umożliwiać późniejsze
dołożenie grubości pośrednich (Medium, SemiBold) bez przepisywania glifów.

## Architektura kodu

- `src/ave_core/`: wspólne prymitywy przeniesione z Ave Display (Shape, polygon, rect, rounded, union)
  i wspólne kroki składania fontu (kontury TrueType, zapis TTF/WOFF2). **Ave Display po refaktorze musi
  budować się do bajtu identycznie**, co sprawdzamy sumą kontrolną pliku TTF przed i po.
- `src/ave_text/`: `style.py` (parametry stylu jako obiekt, nie stałe modułowe, bo stylów jest kilka),
  `shapes.py` (prymitywy kroju tekstowego: pierścień, łuk n/h/m/u z przewężeniem, brzuszek przy trzonie,
  ukośna kreska o stałej grubości, końcówki), `glyphs/` (małe, wielkie, cyfry, interpunkcja, symbole,
  akcenty), `spacing.py`, `kerning.py`, `builder.py` (rodzina, style, nazwy, hinting).
- Każdy glif to funkcja `(style) -> Shape`, rysowana w pionie. Kursywa = pochylenie + formy alternatywne.
  Litery z akcentami składane z bazy i znaku diakrytycznego (spłaszczone kontury, bez komponentów).
- `build.py` buduje obie rodziny (`--family display|text|all`).

## Weryfikacja

Testy automatyczne (`scripts/verify.py` rozszerzone o Ave Text):

- pokrycie zestawu znaków, brak pustych glifów, kierunek konturów, brak nakładających się konturów,
- metryki pionowe obejmują wszystkie glify, spójność metryk między stylami,
- łączenie stylów w rodzinę (nazwy, fsSelection, macStyle, usWeightClass, italicAngle),
- grubości trzonów n i H zgodne z parametrami stylu,
- cyfry tabelaryczne mają równą szerokość, kerning nie zbliża glifów poniżej progu,
- WOFF2 zgodny z TTF.

Testy wzrokowe (podglądy PNG z Chrome bez okna):

- akapity po polsku w 14/16/18/24 px obok Ave Display, na ciemnym i jasnym tle,
- ciągi kontrolne odstępów (nnonnoo, HHOHHO) i kerningu (To, Ty, Va, „A”, r., f,),
- porównanie z Sairą i Exo 2 w tym samym rozmiarze (tylko lokalnie, jako odniesienie).

## Kamienie milowe i punkty kontrolne z Filipem

1. **Wspólny rdzeń**: wydzielenie `ave_core`, Ave Display bez zmian (suma kontrolna).
2. **Prototyp Regular**: a–z, wielkie litery potrzebne do zdań, kropka i przecinek; dwa lub trzy warianty
   charakteru (końcówki proste lub ścięte pod 28°, symetryczne lub asymetryczne zaokrąglenia).
   → **Filip wybiera wariant na akapicie obok nagłówków.**
3. **Pełny Regular**: wszystkie znaki, odstępy, kerning, testy. → pokaz.
4. **Bold**. → pokaz.
5. **Italic i Bold Italic**. → pokaz.
6. **Domknięcie**: hinting, metadane i licencja (jak w Ave Display: wszelkie prawa zastrzeżone),
   specimen całej rodziny, README, commit.

## Stan na koniec 2026-11-07

Kamienie milowe 1–6 zrealizowane: wspólny rdzeń `ave_core` (Ave Display bez zmian, suma kontrolna), pełny Regular,
Bold, Italic, Bold Italic (po 283 glify), kerning klasowy, cyfry tabelaryczne, hinting, testy `verify_text.py`,
`specimen-text.html`. Zmiany względem planu:

- **Bold**: trzon 152/162, kreski poziome 118/124, szerokość ×1,045. Zaokrąglenia za długie dla krótszych krawędzi
  maleją proporcjonalnie (`rounded(..., fit=True)` w `ave_core`, Ave Display tej opcji nie używa).
- **Kursywa**: f z ogonkiem ma własne światła (−24/−14); grubość ukośnych kresek liczona po pochyleniu
  (kontekst `slanted()` w `shapes.py`).
- **Kerning**: metoda pola z ograniczeniem głębokości + „stożek światła” (CONE 1,3), limit −160, kuratorowana
  lista par klas zamiast kerningu wszystkich par (litery z otwartym bokiem mają celowe odstępy).
- **Nawiasy** są łukami o dużym promieniu, nie zaokrąglonymi prostokątami (w 40–64 px te drugie czytały się jak klamry).

Do ewentualnego dopracowania: ð (eth) przypomina trochę đ; & w Bold jest gęste; LT jest ciasne (−160).
