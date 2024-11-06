# Koder i Dekoder Kodów BCH w Pythonie (Wersja CLI)

## Spis Treści

- [Wprowadzenie](#wprowadzenie)
- [Teoria](#teoria)
  - [Kody BCH](#kody-bch)
  - [Ciała Skończone (Ciała Galois)](#ciała-skończone-ciała-galois)
- [Przegląd Algorytmu](#przegląd-algorytmu)
  - [Proces Kodowania](#proces-kodowania)
  - [Proces Dekodowania](#proces-dekodowania)
- [Wyjaśnienie Kodu](#wyjaśnienie-kodu)
  - [Operacje na Wielomianach](#operacje-na-wielomianach)
  - [Arytmetyka w Ciele GF(16)](#arytmetyka-w-ciele-gf16)
  - [Obliczanie Syndromów](#obliczanie-syndromów)
  - [Wielomian Lokatora Błędów](#wielomian-lokatora-błędów)
  - [Korekcja Błędów](#korekcja-błędów)
- [Instrukcje Użycia](#instrukcje-użycia)
  - [Kodowanie Wiadomości](#kodowanie-wiadomości)
  - [Dekodowanie Słowa Kodowego](#dekodowanie-słowa-kodowego)
- [Przykład](#przykład)
- [Podsumowanie](#podsumowanie)
- [Bibliografia](#bibliografia)

---

## Wprowadzenie

Ten dokument dostarcza szczegółowego wyjaśnienia implementacji w Pythonie kodera i dekodera kodów BCH (15,7). Implementacja obejmuje:

- Operacje na wielomianach w GF(2).
- Arytmetykę w ciele skończonym GF(16).
- Obliczanie syndromów.
- Rozwiązywanie wielomianu lokatora błędów.
- Korekcję błędów przy użyciu metody Chiena.
- Interfejs wiersza poleceń przy użyciu `argparse`.

---

### Kody BCH

Kody BCH to klasa cyklicznych kodów korekcyjnych błędów, skonstruowanych przy użyciu ciał skończonych. Są zdolne do korekcji wielu losowych błędów i są szeroko stosowane w cyfrowej komunikacji i systemach przechowywania danych.

- **Kod BCH (n, k)**: Kod korekcyjny błędów, gdzie:
  - `n`: Długość słowa kodowego.
  - `k`: Długość oryginalnej wiadomości.
  - `n - k`: Liczba bitów parzystości dodanych do korekcji błędów.

Kod BCH (15,7) może korygować do 2 błędów w 15-bitowym słowie kodowym.

### Ciała Skończone (Ciała Galois)

- **GF(q)**: Ciało skończone z `q` elementami.
- **GF(2^m)**: Rozszerzone ciała zbudowane nad GF(2), używane w kodach BCH.
- **Wielomian Pierwotny**: Wielomian używany do konstrukcji ciała skończonego.

W tej implementacji używamy GF(16) (ponieważ \(2^4 = 16\)) do operacji arytmetycznych, z wielomianem pierwotnym \(x^4 + x + 1\) (reprezentacja binarna `0b10011`).

---

## Przegląd Algorytmu

### Proces Kodowania

1. **Przygotowanie Wiadomości**:
   - Oryginalna wiadomość jest reprezentowana jako ciąg binarny o długości `k` (7 bitów).

2. **Przesunięcie Wiadomości**:
   - Wiadomość jest przesuwana w lewo o `(n - k)` bitów (dodanie zer), aby zrobić miejsce na bity parzystości.

3. **Dzielenie Wielomianów**:
   - Przesunięta wiadomość jest dzielona przez wielomian generujący `g(x)` przy użyciu dzielenia wielomianów w GF(2).
   - Reszta z tego dzielenia to bity parzystości.

4. **Tworzenie Słowa Kodowego**:
   - Słowo kodowe powstaje przez dodanie reszty (bitów parzystości) do przesuniętej wiadomości.

### Proces Dekodowania

1. **Obliczanie Syndromów**:
   - Oblicz syndromy \( S_1, S_2, S_3, S_4 \) przy użyciu otrzymanego słowa kodowego.
   - Syndromy są obliczane przy użyciu arytmetyki w GF(16).

2. **Wykrywanie Błędów**:
   - Jeśli wszystkie syndromy są zerowe, nie ma błędów.
   - Jeśli nie, przejdź do korekcji błędów.

3. **Wielomian Lokatora Błędów**:
   - Rozwiąż współczynniki wielomianu lokatora błędów \( \sigma_1 \) i \( \sigma_2 \) przy użyciu syndromów.

4. **Metoda Chiena**:
   - Znajdź pozycje błędów przez ocenę wielomianu lokatora błędów dla wszystkich możliwych elementów ciała.

5. **Korekcja Błędów**:
   - Odwróć bity na zidentyfikowanych pozycjach błędów, aby skorygować słowo kodowe.

6. **Ekstrakcja Wiadomości**:
   - Wyodrębnij oryginalne bity wiadomości ze skorygowanego słowa kodowego.

---

## Wyjaśnienie Kodu

### Operacje na Wielomianach

#### Mnożenie Wielomianów (`poly_mul`)

- Mnoży dwa wielomiany w GF(2) przy użyciu przesunięć i operacji XOR.

#### Dzielenie Wielomianów (`poly_div`)

- Wykonuje dzielenie wielomianów metodą długiego dzielenia.
- Zwraca iloraz i resztę.

### Arytmetyka w Ciele GF(16)

#### Generowanie Tabel GF(16) (`gf16_generate_tables`)

- Generuje tabelę potęgowania (`exp_table`) i tabelę logarytmów (`log_table`) dla GF(16) przy użyciu wielomianu pierwotnego.

#### Dodawanie w GF(16) (`gf16_add`)

- Dodawanie jest wykonywane przy użyciu operacji bitowej XOR (`^`).

#### Mnożenie w GF(16) (`gf16_mul`)

- Mnożenie jest wykonywane przy użyciu tabel logarytmów i potęgowań:
  \[ \text{log}(a \times b) = (\text{log}(a) + \text{log}(b)) \mod 15 \]

#### Odwrotność Multiplikatywna w GF(16) (`gf16_inv`)

- Oblicza odwrotność elementu:
  \[ \text{log}(a^{-1}) = (15 - \text{log}(a)) \mod 15 \]

### Obliczanie Syndromów

- Syndromy są obliczane przy użyciu bitów otrzymanego słowa kodowego i tabeli potęgowań.
- Dla każdego syndromu \( S_i \):
  \[ S_i = \sum_{j=0}^{n-1} c_j \cdot \alpha^{i \cdot j} \]
  gdzie \( c_j \) to \( j \)-ty bit słowa kodowego, a \( \alpha \) to pierwotny element.

### Wielomian Lokatora Błędów

- Wielomian lokatora błędów \( \sigma(x) = x^2 + \sigma_1 x + \sigma_2 \) jest rozwiązywany przy użyciu syndromów.
- Obliczany jest wyznacznik \( D \), aby sprawdzić, czy układ równań jest rozwiązywalny.
- Jeśli \( D = 0 \), błędy nie mogą być skorygowane (więcej niż 2 błędy).

### Korekcja Błędów

#### Metoda Chiena (`chien_search`)

- Ocenia wielomian lokatora błędów dla wszystkich elementów odwrotnych ciała, aby znaleźć pozycje błędów.
- Dla każdej pozycji \( i \):
  \[ \sigma(\alpha^{-i}) = 0 \]
- Pozycje, gdzie wielomian przyjmuje wartość zero, wskazują na lokalizacje błędów.

#### Korekcja Słowa Kodowego

- Bity na pozycjach błędów są odwracane (korygowane) w słowie kodowym.

---

## Instrukcje Użycia

Upewnij się, że masz zainstalowany Python 3 na swoim systemie.

### Kodowanie Wiadomości

Aby zakodować 7-bitową wiadomość przy użyciu kodu BCH (15,7):

```sh
python bch_terminal_implementation.py encode -n 15 -k 7 -message <7-bitowa-wiadomość-binarnie>
```

#### Przykład
```sh
python bch_terminal_implementation.py encode -n 15 -k 7 -message 1010101
```

### Dekodowanie

Aby zdekodować 15-bitowe słowo kodowe i skorygować do 2 błędów:

```sh
python bch_terminal_implementation.py decode -n 15 -k 7 -codeword <15-bitowe-słowo-kodowe-binarnie>
```

#### Przykład
```sh
python bch_terminal_implementation.py decode -n 15 -k 7 -codeword 101010100011001
```

### Kodowanie

Polecenie:
```sh
python bch_terminal_implementation.py encode -n 15 -k 7 -message 1010101
```
Wynik:

```yaml
Starting encoding process...
Message integer: 85
Shifted message: 0b101010100000000
Generator polynomial: 0b111010001
Remainder after division: 0b11001
Encoded codeword: 101010100011001
```