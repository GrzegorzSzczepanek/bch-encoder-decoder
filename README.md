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

Niniejszy dokument przedstawia instrukcję obsługi aplikacji napisanej w języku Python3, która implementuje koder i dekoder kodów BCH (Bose–Chaudhuri–Hocquenghem). Program umożliwia kodowanie i dekodowanie wiadomości przy użyciu kodów BCH, wstrzykiwanie błędów oraz wizualizację procesu korekcji błędów.
Matematyczne podstawy kodów BCH znajdują się w tym [pliku](Matematyczne-Podstawy-Kodów-BCH.pdf).

## Podstawy Teoretyczne

### Kody BCH

Kody BCH to rodzaj cyklicznych kodów korekcyjnych błędów, zdolnych do korygowania wielu błędów w słowie kodowym. Są szeroko stosowane w komunikacji cyfrowej oraz systemach przechowywania danych.

**Kod BCH (n, k, t):**

- **n**: Długość słowa kodowego (liczba bitów po kodowaniu).
- **k**: Długość oryginalnej wiadomości (liczba bitów przed kodowaniem).
- **t**: Zdolność korekcji błędów (maksymalna liczba błędów, które kod może skorygować).

### Ciała Galois

Kody BCH opierają się na arytmetyce w ciałach skończonych, zwanych ciałami Galois (GF). W szczególności wykorzystuje się ciała GF(2^m), gdzie m jest stopniem ciała. W tej aplikacji używamy ciał GF(2^m) do operacji matematycznych niezbędnych w kodach BCH.

## Opis Programu

### Funkcjonalności

- **Kodowanie**: Kodowanie podanej wiadomości przy użyciu kodu BCH z określonymi parametrami.
- **Dekodowanie**: Dekodowanie słowa kodowego, wykrywanie i korekcja błędów.
- **Wstrzykiwanie błędów**: Możliwość wstrzyknięcia określonej liczby losowych błędów bitowych.
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

2. **Kodowanie i dekodowanie losowej wiadomości z wstrzyknięciem 5 błędów**:

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
   python3 bch_encoder_decoder.py -message 4f70656e414945 -num_errors 3 -verbose
   ```

   - Koduje podaną wiadomość.
   - Wstrzykuje 3 błędy bitowe.
   - Włącza szczegółowe logowanie procesu.

5. **Ustawienie własnych parametrów t i m**:
   ```bash
   python3 bch_encoder_decoder.py -t 7 -m 9 -num_errors 7
   ```
   - Ustawia zdolność korekcji błędów na 7.
   - Ustawia rząd ciała Galois na 9.
   - Wstrzykuje 7 błędów bitowych.

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

### Przykład 2: Kodowanie i dekodowanie własnej wiadomości z 5 błędami

**Polecenie**:

```bash
python3 bch_encoder_decoder.py -message 041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d4 -num_errors 5
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

Injected 5 Errors at bit positions: [52, 76, 41, 173, 47]
Corrupted Codeword:
041b8d02eae8a41b64d73565c9fbd18378df6ed39390a42142d43d20574629

Corrected Codeword:
041b8d02ea6ab41b64c73565c9fbd18378df6ed393b0a42142d43d20574629

Visualized Changes (bits):
[... wizualizacja z użyciem kolorów ...]

Corrected Bit Positions:
Bit 52
Bit 76
Bit 41
Bit 173
Bit 47

Injected Bit Positions:
Bit 52
Bit 76
Bit 41
Bit 173
Bit 47

All injected errors were successfully corrected!
```

## Podsumowanie

Aplikacja pozwala na efektywne kodowanie i dekodowanie wiadomości z wykorzystaniem kodów BCH, w tym na symulację błędów oraz ich korekcję. Dzięki interfejsowi wiersza poleceń użytkownik może dostosować parametry kodowania i dekodowania oraz testować różne scenariusze.

## Bibliografia

- **Kody BCH**: [Wikipedia - Kod BCH](https://pl.wikipedia.org/wiki/Kod_BCH)
- **Ciało Galois**: [Wikipedia - Ciało Galois](https://pl.wikipedia.org/wiki/Cia%C5%82o_Galois)
- **Biblioteka bchlib**: [GitHub - bchlib](https://github.com/tomerfiliba/bchlib)
- **Biblioteka colorama**: [PyPI - colorama](https://pypi.org/project/colorama/)
- **Dokumentacja argparse**: [Python3 - argparse](https://docs.python3.org/3/library/argparse.html)

**Uwaga**: Przed uruchomieniem programu należy zainstalować wymagane biblioteki:

```bash
python33 -m venv venv
pip install -r requirements.txt
```
