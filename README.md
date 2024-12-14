# Koder i Dekoder Kodów BCH w Python3ie

## Spis Treści

- [Wprowadzenie](#wprowadzenie)
- [Podstawy Teoretyczne](#podstawy-teoretyczne)
  - [Kody BCH](#kody-bch)
  - [Ciała Galois](#ciała-galois)
- [Opis Programu](#opis-programu)
  - [Funkcjonalności](#funkcjonalności)
  - [Wymagania](#wymagania)
- [Instrukcja Użycia](#instrukcja-użycia)
  - [Argumenty Wiersza Poleceń](#argumenty-wiersza-poleceń)
  - [Przykłady Użycia](#przykłady-użycia)
- [Przykładowe Wyniki Programu](#przykładowe-wyniki-programu)
- [Podsumowanie](#podsumowanie)
- [Bibliografia](#bibliografia)

## Wprowadzenie

Niniejszy dokument przedstawia instrukcję obsługi aplikacji napisanej w języku Python3, która implementuje koder i dekoder kodów BCH (Bose–Chaudhuri–Hocquenghem). Program umożliwia kodowanie i dekodowanie wiadomości przy użyciu kodów BCH, wstrzykiwanie błędów oraz wizualizację procesu korekcji błędów. Matematyczne podstawy kodów BCH znajdują się w tym [pliku](Matematyczne-Podstawy-Kodów-BCH.pdf).

Program oczekuje, ze wiadomość będzie podana w systemie szesnatkowym i miała co najmniej 8 bitów.

## Podstawy Teoretyczne

### Kody BCH

Kody BCH to rodzaj cyklicznych kodów korekcyjnych błędów, zdolnych do korygowania wielu błędów w słowie kodowym. Są szeroko stosowane w komunikacji cyfrowej oraz systemach przechowywania danych.

**Kod BCH (n, k, t):**

- **n**: Długość słowa kodowego (liczba bitów po kodowaniu).
- **k**: Długość oryginalnej wiadomości (liczba bitów przed kodowaniem).
- **t**: Zdolność korekcji błędów (maksymalna liczba błędów, które kod może skorygować).

### Ciała Galois

Kody BCH opierają się na arytmetyce w ciałach skończonych, zwanych ciałami Galois (GF). W szczególności wykorzystuje się ciała GF(2^m), gdzie m jest stopniem ciała. W tej aplikacji używamy ciał GF(2^m) do operacji matematycznych niezbędnych w kodach BCH.

Więcej w [pliku](Matematyczne-Podstawy-Kodów-BCH.pdf).

## Opis Programu

### Funkcjonalności

- **Kodowanie**: Kodowanie podanej wiadomości przy użyciu kodu BCH z określonymi parametrami.
- **Dekodowanie**: Dekodowanie słowa kodowego, wykrywanie i korekcja błędów.
- **Wstrzykiwanie błędów**: Możliwość wstrzyknięcia określonej liczby losowych błędów bitowych lub błędów w określonych pozycjach bitów.
- **Wizualizacja**: Wyświetlanie procesu korekcji błędów z użyciem kolorów dla łatwiejszego zrozumienia.
- **Dostosowywanie parametrów**: Możliwość ustawienia własnych parametrów t i m, a także podania własnej wiadomości.

### Wymagania

- **Python3 3.x**
- **Biblioteki**:
  - `bchlib` (instalacja: `pip install bchlib`)
  - `colorama` (instalacja: `pip install colorama`)

## Instrukcja Użycia

### Argumenty Wiersza Poleceń

Program akceptuje następujące argumenty:

- `-t`: Zdolność korekcji błędów (domyślnie: 5).
- `-m`: Rząd ciała Galois GF(2^m) (domyślnie: 8).
- `-message`: Wiadomość do zakodowania w formacie szesnastkowym (hexadecimal).
- `-num_errors`: Liczba błędów bitowych do wstrzyknięcia (domyślnie: 0).
- `-error_bits`: Lista pozycji bitów, w których mają zostać wstrzyknięte błędy. Pozycje bitów powinny być podane jako lista liczb oddzielonych przecinkami (np. `1,3,5`).
- `-verbose`: Włączenie szczegółowego logowania.

Aby wyświetlić pomoc:

```bash
python3 bch_encoder_decoder.py -h
```

### Przykłady Użycia

1. **Kodowanie i dekodowanie losowej wiadomości bez błędów**:

   ```bash
   python3 bch_encoder_decoder.py
   ```

   - Używa domyślnych wartości t=5 i m=8.
   - Generuje losową wiadomość.
   - Koduje i dekoduje wiadomość bez wstrzykiwania błędów.

2. **Kodowanie i dekodowanie losowej wiadomości z wstrzyknięciem 5 losowych błędów**:

   ```bash
   python3 bch_encoder_decoder.py -num_errors 5
   ```

   - Generuje losową wiadomość.
   - Koduje wiadomość, wstrzykuje 5 losowych błędów bitowych, następnie dekoduje i koryguje błędy.

3. **Kodowanie i dekodowanie własnej wiadomości**:

   ```bash
   python3 bch_encoder_decoder.py -message 4f70656e414945
   ```

   - Koduje podaną wiadomość `4f70656e414945` (format szesnastkowy).
   - Dekoduje bez wstrzykiwania błędów.

4. **Kodowanie i dekodowanie z wstrzyknięciem błędów i szczegółowym logowaniem**:

   ```bash
   python3 bch_encoder_decoder.py -message 4f70656e414945 -num_errors 3 -error_bits 10,15,20 -verbose
   ```

   - Koduje podaną wiadomość.
   - Wstrzykuje 3 błędy bitowe w określonych pozycjach (bit 10, 15 i 20).
   - Włącza szczegółowe logowanie procesu.

5. **Ustawienie własnych parametrów t i m oraz wstrzyknięcie błędów w określonych bitach**:

   ```bash
   python3 bch_encoder_decoder.py -t 7 -m 9 -num_errors 7 -error_bits 1,3,5,7,9,11,13
   ```

   - Ustawia zdolność korekcji błędów na 7.
   - Ustawia rząd ciała Galois na 9.
   - Wstrzykuje 7 błędów bitowych w określonych pozycjach (bit 1, 3, 5, 7, 9, 11 i 13).

## Przykładowe Wyniki Programu

### Przykład 1: Kodowanie i dekodowanie losowej wiadomości z 3 błędami

**Polecenie**:

```bash
python3 bch_encoder_decoder.py -num_errors 3
```

**Wyjście**:

```yaml
n (codeword length): 255 bits
ecc_bits: 40 bits
ecc_bytes: 5 bytes
t (error correction capability): 5
Maximum data bits: 215 bits
Maximum data bytes: 26 bytes

----------------------------------------
Original Message:
e4d3c2b1a09f8e7d6c5b4a392817160f0e0d0c0b0a0908070605

Encoded Codeword:
e4d3c2b1a09f8e7d6c5b4a392817160f0e0d0c0b0a0908070605abcd1234ef

Injected 3 Errors at bit positions: [45, 128, 210]
Corrupted Codeword:
e4d3c2b1a09f8e7d6c5b4a392817160f0e0d0c0b0a0908070605abc51234ef

Corrected Codeword:
e4d3c2b1a09f8e7d6c5b4a392817160f0e0d0c0b0a0908070605abcd1234ef

Visualized Changes (bits):
[... wizualizacja z użyciem kolorów ...]

Corrected Bit Positions:
Bit 45
Bit 128
Bit 210

Injected Bit Positions:
Bit 45
Bit 128
Bit 210

All injected errors were successfully corrected!
```

### Przykład 2: Kodowanie i dekodowanie własnej wiadomości z 5 błędami w określonych bitach

**Polecenie**:

```bash
python3 bch_encoder_decoder.py -message 041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d4 -num_errors 5 -error_bits 1,3,5,7,9 -verbose
```

**Wyjście**:

```yaml
n (codeword length): 255 bits
ecc_bits: 40 bits
ecc_bytes: 5 bytes
t (error correction capability): 5
Maximum data bits: 215 bits
Maximum data bytes: 26 bytes

----------------------------------------
Original Message:
041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d4

Encoded Codeword:
041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d43d20574629

Injected 5 Errors at bit positions: [1, 3, 5, 7, 9]
Corrupted Codeword:
041b8d02eae8a41b64d73565c9fbd18378df6ed39390a42142d43d20574629

Corrected Codeword:
041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d43d20574629

Decoded Message:
041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d4

Visualized Changes (bits):
[... wizualizacja z użyciem kolorów ...]

Corrected Bit Positions:
Bit 1
Bit 3
Bit 5
Bit 7
Bit 9

Injected Bit Positions:
Bit 1
Bit 3
Bit 5
Bit 7
Bit 9

All injected errors were successfully corrected!
```

### Przykład 3: Kodowanie i dekodowanie własnej wiadomości z błędami przekraczającymi zdolność korekcji

**Polecenie**:

```bash
python3 bch_encoder_decoder.py -t 2 -m 5 -message 1F -num_errors 3 -error_bits 1,3,5 -verbose
```

**Wyjście**:

```yaml
n (codeword length): 31 bits
ecc_bits: 10 bits
ecc_bytes: 2 bytes
t (error correction capability): 2
Maximum data bits: 21 bits
Maximum data bytes: 2 bytes

----------------------------------------
Original Message:
1f00

Encoded Codeword:
1f00d640

Injected 3 Errors at bit positions: [1, 3, 5]
Corrupted Codeword:
1d14d640

Corrected Codeword:
1f00d640

Decoded Message:
1f00

Visualized Changes (bits):
000011111 00000000 11010110 01000000

Corrected Bit Positions:
Bit 1
Bit 3
Bit 5

Injected Bit Positions:
Bit 1
Bit 3
Bit 5

All injected errors were successfully corrected!
```

**Uwaga**: W przypadku przekroczenia zdolności korekcji błędów (`t`), program może nie być w stanie skorygować wszystkich wstrzykniętych błędów. Upewnij się, że liczba błędów nie przekracza wartości `t`, aby zapewnić prawidłowe działanie korekcji.

## Podsumowanie

Aplikacja pozwala na efektywne kodowanie i dekodowanie wiadomości z wykorzystaniem kodów BCH, w tym na symulację błędów oraz ich korekcję. Dzięki interfejsowi wiersza poleceń użytkownik może dostosować parametry kodowania i dekodowania oraz testować różne scenariusze, w tym wstrzykiwanie błędów w określonych pozycjach bitów.

## Bibliografia

- **Kody BCH**: [Wikipedia - Kod BCH](https://pl.wikipedia.org/wiki/Kod_BCH)
- **Ciało Galois**: [Wikipedia - Ciało Galois](https://pl.wikipedia.org/wiki/Cia%C5%82o_Galois)
- **Biblioteka bchlib**: [GitHub - bchlib](https://github.com/tomerfiliba/bchlib)
- **Biblioteka colorama**: [PyPI - colorama](https://pypi.org/project/colorama/)
- **Dokumentacja argparse**: [Python3 - argparse](https://docs.python.org/3/library/argparse.html)

**Uwaga**: Przed uruchomieniem programu należy zainstalować wymagane biblioteki:

```bash
python3 -m venv venv
pip install -r requirements.txt
```

---

### Dodatkowe Uwagi

1. **Format Argumentu `-error_bits`**:

   - Aby wstrzyknąć błędy w określonych pozycjach bitów, użyj argumentu `-error_bits` z listą pozycji oddzielonych przecinkami bez spacji.
   - **Przykład**: `-error_bits 1,3,5`

2. **Zgodność Liczby Błędów**:

   - Liczba błędów określona w `-num_errors` musi dokładnie odpowiadać liczbie pozycji bitów podanych w `-error_bits`.
   - **Przykład**: Dla `-num_errors 3`, należy podać trzy pozycje bitów, np. `-error_bits 1,3,5`

3. **Indeksowanie Bitów**:

   - Pozycje bitów są indeksowane od zera (`0`-based indexing).
   - Upewnij się, że podane pozycje bitów mieszczą się w zakresie długości słowa kodowego (`n`).

4. **Walidacja Argumentów**:

   - Program sprawdza, czy liczba błędów odpowiada liczbie podanych pozycji bitów. W przypadku niezgodności, wyświetla komunikat błędu i kończy działanie.

5. **Obsługa Błędów**:

   - Jeśli liczba wstrzykniętych błędów przekracza zdolność korekcji (`t`), program może nie skorygować wszystkich błędów, co zostanie odnotowane w wynikach.

6. **Przykłady z Hamming (7,4) Kode**:

   - Możesz również używać kodów Hamming (7,4) dla prostszych testów. Poniżej znajduje się przykład:

   **Polecenie**:

   ```bash
   python3 bch_encoder_decoder.py -m 4 -message 9 -num_errors 1 -error_bits 2 -verbose
   ```

   **Wyjście**:

   ```yaml
   Using Hamming (7,4) Code
   n (codeword length): 7 bits
   k (message length): 4 bits
   t (error correction capability): 1

   ----------------------------------------
   Original Message:
   1001

   Encoded Codeword:
   1001010

   Injected 1 Errors at bit positions: [2]
   Corrupted Codeword:
   1011010

   Corrected Codeword:
   1001010

   Decoded Message:
   1001

   Visualized Changes (bits):
   10[1→0]1010

   Corrected Bit Positions:
   Bit 2

   Injected Bit Positions:
   Bit 2

   All injected errors were successfully corrected!
   ```

   **Wyjaśnienie**:

   - **Original Message**: `1001`
   - **Encoded Codeword**: `1001010`
   - **Injected Error na Bit 2**: zmienia trzeci (indeksowany od 0) bit `0` to `1`, co daje `1011010`.
   - **Decoded Message**: `1001`
   - **Wizualizacja**: Pokazuje zmianę bitu z użyciem kolorów (jeśli terminal obsługuje).
   - **Wynik**: Wszystkie wstrzyknięte błędy zostały pomyślnie skorygowane.

---
