#!/usr/bin/env python3

import bchlib
import random
import logging
import sys
import argparse

# For colored logging
try:
    from colorama import init, Fore, Style

    init(autoreset=True)
except ImportError:
    print("colorama module not found. Install it using 'pip install colorama'")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def hamming_7_4_encode(data_bits):
    d = data_bits
    c = [0] * 7
    c[3] = d[0]
    c[4] = d[1]
    c[5] = d[2]
    c[6] = d[3]
    c[0] = d[0] ^ d[1] ^ d[3]
    c[1] = d[0] ^ d[2] ^ d[3]
    c[2] = d[1] ^ d[2] ^ d[3]
    return c


def hamming_7_4_decode(codeword):
    r = codeword
    s = [0, 0, 0]
    s[0] = r[0] ^ r[3] ^ r[4] ^ r[6]
    s[1] = r[1] ^ r[3] ^ r[5] ^ r[6]
    s[2] = r[2] ^ r[4] ^ r[5] ^ r[6]
    syndrome = (s[0] << 2) | (s[1] << 1) | s[2]
    logging.debug(f"Syndrome: {syndrome} (binary: {''.join(map(str, s))})")
    if syndrome != 0:
        error_pos = syndrome - 1
        logging.debug(f"Correcting bit at position {error_pos}")
        r[error_pos] ^= 1
    data_bits = [r[3], r[4], r[5], r[6]]
    return data_bits, syndrome


def log_colored(message, color):
    logging.info(f"{color}{message}{Style.RESET_ALL}")


def bitflip(data, bit):
    if isinstance(data, bytearray):
        byte_index = bit // 8
        bit_index = bit % 8
        data[byte_index] ^= 1 << bit_index
    elif isinstance(data, list):
        data[bit] ^= 1
    else:
        raise TypeError("Unsupported data type for bitflip")


def encode_message(bch, data):
    ecc = bch.encode(data)
    return data + ecc


def inject_errors(data, num_errors=0, specific_bits=None):
    if specific_bits is not None:
        if not isinstance(specific_bits, list):
            raise TypeError("specific_bits should be a list of bit positions")
        error_positions = specific_bits
    else:
        if isinstance(data, bytearray):
            data_len_bits = len(data) * 8
        elif isinstance(data, list):
            data_len_bits = len(data)
        else:
            raise TypeError("Unsupported data type for inject_errors")
        if num_errors > data_len_bits:
            raise ValueError("Number of errors exceeds the number of bits in data")
        error_positions = random.sample(range(data_len_bits), num_errors)

    if isinstance(data, bytearray):
        data_with_errors = bytearray(data)
        for bit in error_positions:
            bitflip(data_with_errors, bit)
    elif isinstance(data, list):
        data_with_errors = data[:]
        for bit in error_positions:
            bitflip(data_with_errors, bit)
    else:
        raise TypeError("Unsupported data type for inject_errors")

    return data_with_errors, error_positions


def decode_and_correct(bch, corrupted_data):
    if isinstance(bch, CustomBCH):
        # For CustomBCH, the last ecc_bytes are the ECC
        data = corrupted_data[: -bch.ecc_bytes]
        recv_ecc = corrupted_data[-bch.ecc_bytes :]
        nerr = bch.decode(data, recv_ecc)
        if nerr >= 0:
            corrected_data, corrected_ecc = bch.correct(data, recv_ecc)
            return corrected_data + corrected_ecc, bch.errloc
        else:
            return None, None
    else:
        # For bchlib.BCH
        data = corrupted_data[: -bch.ecc_bytes]
        recv_ecc = corrupted_data[-bch.ecc_bytes :]
        nerr = bch.decode(data, recv_ecc)
        if nerr >= 0:
            corrected_data = bytearray(data)
            bch.correct(corrected_data, recv_ecc)
            return corrected_data + recv_ecc, bch.errloc
        else:
            return None, None


def visualize_changes(original, corrupted, corrected, injected_bits, corrected_bits):
    output = []
    if isinstance(original, bytearray):
        total_bits = len(original) * 8
        for bit in range(total_bits):
            byte_index = bit // 8
            bit_in_byte = 7 - (bit % 8)
            orig_bit = (original[byte_index] >> bit_in_byte) & 1
            corru_bit = (corrupted[byte_index] >> bit_in_byte) & 1
            corrected_bit = (corrected[byte_index] >> bit_in_byte) & 1

            if bit in injected_bits and bit in corrected_bits:
                output.append(
                    Fore.RED
                    + f"{orig_bit}"
                    + Fore.GREEN
                    + f"{corrected_bit}"
                    + Style.RESET_ALL
                )
            elif bit in injected_bits:
                output.append(Fore.RED + f"{corru_bit}" + Style.RESET_ALL)
            elif bit in corrected_bits:
                output.append(Fore.GREEN + f"{corrected_bit}" + Style.RESET_ALL)
            else:
                output.append(f"{orig_bit}")

            if bit % 8 == 7:
                output.append(" ")
    elif isinstance(original, list):
        total_bits = len(original)
        for bit in range(total_bits):
            orig_bit = original[bit]
            corru_bit = corrupted[bit]
            corrected_bit = corrected[bit]
            if bit in injected_bits and bit in corrected_bits:
                output.append(
                    Fore.RED
                    + f"{orig_bit}"
                    + Fore.GREEN
                    + f"{corrected_bit}"
                    + Style.RESET_ALL
                )
            elif bit in injected_bits:
                output.append(Fore.RED + f"{corru_bit}" + Style.RESET_ALL)
            elif bit in corrected_bits:
                output.append(Fore.GREEN + f"{corrected_bit}" + Style.RESET_ALL)
            else:
                output.append(f"{orig_bit}")
    else:
        raise TypeError("Unsupported data type for visualize_changes")

    return "".join(output)


def run_test(bch, message, num_errors=0, specific_bits=None, use_hamming=False):
    logging.info(f"\n{'-'*40}\nOriginal Message:")
    if use_hamming:
        # Not used anymore, but we keep it as requested
        logging.info("".join(str(b) for b in message))
        codeword = hamming_7_4_encode(message)
        logging.info("\nEncoded Codeword:")
        logging.info("".join(str(b) for b in codeword))

        if num_errors > 0:
            corrupted_codeword, injected_bits = inject_errors(
                codeword, num_errors, specific_bits
            )
            log_colored(
                f"\nInjected {num_errors} Errors at bit positions: {injected_bits}",
                Fore.RED,
            )
            logging.info("Corrupted Codeword:")
            logging.info("".join(str(b) for b in corrupted_codeword))
        else:
            corrupted_codeword = codeword
            injected_bits = []

        corrected_data_bits, syndrome = hamming_7_4_decode(corrupted_codeword)
        corrected_codeword = corrupted_codeword
        logging.info("\nCorrected Codeword:")
        logging.info("".join(str(b) for b in corrected_codeword))
        logging.info("\nDecoded Message:")
        logging.info("".join(str(b) for b in corrected_data_bits))

        logging.info("\nVisualized Changes (bits):")
        corrected_bits = []
        if syndrome != 0:
            corrected_bits = [syndrome - 1]
        visualization = visualize_changes(
            codeword,
            corrupted_codeword,
            corrected_codeword,
            injected_bits,
            corrected_bits,
        )
        logging.info(visualization)

        if corrected_bits:
            log_colored("\nCorrected Bit Positions:", Fore.GREEN)
            for bit in corrected_bits:
                log_colored(f"Bit {bit}", Fore.GREEN)

        if injected_bits:
            log_colored("\nInjected Bit Positions:", Fore.RED)
            for bit in injected_bits:
                log_colored(f"Bit {bit}", Fore.RED)

        if set(injected_bits) == set(corrected_bits):
            log_colored(
                "\nAll injected errors were successfully corrected!", Fore.GREEN
            )
        else:
            log_colored("\nSome injected errors were not corrected!", Fore.RED)
    else:
        # BCH path
        if isinstance(bch, CustomBCH):
            logging.info(message.hex())
            codeword = encode_message(bch, message)
            logging.info("\nEncoded Codeword:")
            logging.info(codeword.hex())

            if num_errors > 0:
                corrupted_codeword, injected_bits = inject_errors(
                    codeword, num_errors, specific_bits
                )
                log_colored(
                    f"\nInjected {num_errors} Errors at bit positions: {injected_bits}",
                    Fore.RED,
                )
                logging.info("Corrupted Codeword:")
                logging.info(corrupted_codeword.hex())
            else:
                corrupted_codeword = codeword
                injected_bits = []

            corrected_codeword, corrected_bits = decode_and_correct(
                bch, corrupted_codeword
            )
            if corrected_codeword:
                logging.info("\nCorrected Codeword:")
                logging.info(corrected_codeword.hex())

                logging.info("\nVisualized Changes (bits):")
                visualization = visualize_changes(
                    codeword,
                    corrupted_codeword,
                    corrected_codeword,
                    injected_bits,
                    corrected_bits,
                )
                logging.info(visualization)

                if corrected_bits:
                    log_colored("\nCorrected Bit Positions:", Fore.GREEN)
                    for bit in corrected_bits:
                        log_colored(f"Bit {bit}", Fore.GREEN)

                if injected_bits:
                    log_colored("\nInjected Bit Positions:", Fore.RED)
                    for bit in injected_bits:
                        log_colored(f"Bit {bit}", Fore.RED)

                if set(injected_bits) == set(corrected_bits):
                    log_colored(
                        "\nAll injected errors were successfully corrected!", Fore.GREEN
                    )
                else:
                    log_colored("\nSome injected errors were not corrected!", Fore.RED)
            else:
                logging.error("Decoding failed. Unable to correct the errors.")
        else:
            logging.info(message.hex())
            codeword = encode_message(bch, message)
            logging.info("\nEncoded Codeword:")
            logging.info(codeword.hex())

            if num_errors > 0:
                corrupted_codeword, injected_bits = inject_errors(
                    codeword, num_errors, specific_bits
                )
                log_colored(
                    f"\nInjected {num_errors} Errors at bit positions: {injected_bits}",
                    Fore.RED,
                )
                logging.info("Corrupted Codeword:")
                logging.info(corrupted_codeword.hex())
            else:
                corrupted_codeword = codeword
                injected_bits = []

            corrected_codeword, corrected_bits = decode_and_correct(
                bch, corrupted_codeword
            )
            if corrected_codeword:
                logging.info("\nCorrected Codeword:")
                logging.info(corrected_codeword.hex())

                logging.info("\nVisualized Changes (bits):")
                visualization = visualize_changes(
                    codeword,
                    corrupted_codeword,
                    corrected_codeword,
                    injected_bits,
                    corrected_bits,
                )
                logging.info(visualization)

                if corrected_bits:
                    log_colored("\nCorrected Bit Positions:", Fore.GREEN)
                    for bit in corrected_bits:
                        log_colored(f"Bit {bit}", Fore.GREEN)

                if injected_bits:
                    log_colored("\nInjected Bit Positions:", Fore.RED)
                    for bit in injected_bits:
                        log_colored(f"Bit {bit}", Fore.RED)

                if set(injected_bits) == set(corrected_bits):
                    log_colored(
                        "\nAll injected errors were successfully corrected!", Fore.GREEN
                    )
                else:
                    log_colored("\nSome injected errors were not corrected!", Fore.RED)
            else:
                logging.error("Decoding failed. Unable to correct the errors.")


class CustomBCH:
    def __init__(self, t, m=4):
        if m == 4 and t in [1, 2]:
            self.m = m
            self.t = t
            self.n = (1 << m) - 1  # n = 2^m -1 = 15
            if t == 1:
                self.k = 11
                self.generator = 0b10011  # x^4 + x + 1
            elif t == 2:
                self.k = 7
                self.generator = 0b110110111  # Example generator for t=2
            self.ecc_bits = self.n - self.k
            self.ecc_bytes = (self.ecc_bits + 7) // 8
            self.errloc = []
        else:
            raise NotImplementedError(
                f"Custom BCH with m={m}, t={t} not implemented yet."
            )

    def encode(self, data):
        # Ensure data length matches k bits
        data_bits = self._bytes_to_bits(data, self.k)
        if data_bits >= (1 << self.k):
            raise ValueError("Data too large to encode with given k.")

        # Shift data bits to make space for ECC
        codeword = data_bits << self.ecc_bits
        # Calculate ECC using polynomial division
        remainder = self._poly_mod(codeword, self.generator)
        # Append ECC to form the full codeword
        codeword |= remainder
        # Convert codeword to bytes
        codeword_bytes = self._bits_to_bytes(codeword, self.n)
        # Extract ECC from codeword
        ecc = codeword_bytes[-self.ecc_bytes :]
        return ecc

    def decode(self, data, recv_ecc):
        # Combine data and received ECC to form the full codeword
        codeword = bytearray(data + recv_ecc)
        codeword_bits = self._bytes_to_int(codeword, self.n)
        # Calculate syndrome
        syndrome = self._poly_mod(codeword_bits, self.generator)
        if syndrome == 0:
            self.errloc = []
            return 0  # No error
        else:
            # Attempt to locate and correct errors
            if self.t == 1:
                # Single error correction
                for bit_pos in range(self.n):
                    test_word = codeword_bits ^ (1 << bit_pos)
                    test_syndrome = self._poly_mod(test_word, self.generator)
                    if test_syndrome == 0:
                        self.errloc = [bit_pos]
                        return 1  # Single error corrected
                return -1  # Unable to correct
            elif self.t == 2:
                # Two error correction (simplistic approach)
                error_positions = []
                for bit_pos in range(self.n):
                    test_word = codeword_bits ^ (1 << bit_pos)
                    test_syndrome = self._poly_mod(test_word, self.generator)
                    if test_syndrome == 0:
                        error_positions.append(bit_pos)
                        if len(error_positions) == self.t:
                            break
                if len(error_positions) == self.t:
                    self.errloc = error_positions
                    return self.t  # Two errors corrected
                return -1  # Unable to correct

    def correct(self, data, ecc):
        if not self.errloc:
            return data, ecc  # No correction needed
        codeword = bytearray(data + ecc)
        for bit in self.errloc:
            byte_index = bit // 8
            bit_index = bit % 8
            codeword[byte_index] ^= 1 << (7 - bit_index)
        # Split corrected codeword back into data and ECC
        corrected_data = codeword[: len(data)]
        corrected_ecc = codeword[len(data) :]
        return corrected_data, corrected_ecc

    @staticmethod
    def _bytes_to_bits(data, length_bits):
        val = 0
        bits_needed = length_bits
        for byte in data:
            for b in range(8):
                if bits_needed == 0:
                    break
                bit_val = (byte >> (7 - b)) & 1
                val = (val << 1) | bit_val
                bits_needed -= 1
            if bits_needed == 0:
                break
        val = val << bits_needed  # Pad with zeros if necessary
        return val

    @staticmethod
    def _bits_to_bytes(bits_int, length_bits):
        byte_len = (length_bits + 7) // 8
        out = bytearray(byte_len)
        for i in range(byte_len):
            shift = 8 * (byte_len - 1 - i)
            chunk = (bits_int >> shift) & 0xFF
            out[i] = chunk
        return out

    @staticmethod
    def _bytes_to_int(data, length_bits):
        val = 0
        for byte in data:
            val = (val << 8) | byte
        val = val & ((1 << length_bits) - 1)
        return val

    @staticmethod
    def _poly_mod(dividend, generator):
        generator_degree = generator.bit_length() - 1
        while dividend.bit_length() >= generator.bit_length():
            shift = dividend.bit_length() - generator.bit_length()
            dividend ^= generator << shift
        return dividend

    def get_error_locations(self):
        return self.errloc


def main():
    parser = argparse.ArgumentParser(
        description="BCH Encoder and Decoder with Error Injection"
    )
    parser.add_argument(
        "-t", type=int, default=5, help="Error correction capability (default: 5)"
    )
    parser.add_argument(
        "-m", type=int, default=8, help="Galois Field order (default: 8)"
    )
    parser.add_argument("-message", type=str, help="Message to encode in hexadecimal")
    parser.add_argument(
        "-num_errors",
        type=int,
        default=0,
        help="Number of bit errors to inject (default: 0)",
    )
    parser.add_argument(
        "-error_bits",
        type=str,
        help="Comma-separated list of bit positions to inject errors",
    )
    parser.add_argument("-verbose", action="store_true", help="Enable detailed logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.error_bits:
        try:
            specific_bits = [int(bit.strip()) for bit in args.error_bits.split(",")]
        except ValueError:
            print("Error: -error_bits must be a comma-separated list of integers.")
            sys.exit(1)
        if args.num_errors != len(specific_bits):
            print("Error: Number of bits in -error_bits must match -num_errors.")
            sys.exit(1)
    else:
        specific_bits = None

    if args.m < 5:
        # Using custom BCH
        if args.m == 4:
            if args.t in [1, 2]:
                try:
                    bch = CustomBCH(t=args.t, m=4)
                except NotImplementedError as e:
                    print(f"Error: {e}")
                    sys.exit(1)
                # BCH(15,11,1) or BCH(15,7,2)
                max_data_bits = bch.k
                max_data_bytes = (bch.k + 7) // 8
            else:
                print(f"Error: Unsupported t={args.t} for m=4.")
                sys.exit(1)
        else:
            print(f"Error: Custom BCH with m={args.m} not implemented.")
            sys.exit(1)

        # Print parameters for visibility
        print(f"Using Custom BCH Code")
        print(f"n (codeword length): {bch.n} bits")
        print(f"ecc_bits: {bch.ecc_bits} bits")
        print(f"ecc_bytes: {bch.ecc_bytes} bytes")
        print(f"t (error correction capability): {bch.t}")
        print(f"k (message length): {bch.k} bits")
        print(f"Maximum data bits: {max_data_bits} bits")
        print(f"Maximum data bytes: {max_data_bytes} bytes")

        # Prepare message
        if args.message:
            message = bytearray.fromhex(args.message)
            if len(message) > max_data_bytes:
                print(
                    f"Error: Message length exceeds maximum allowed ({max_data_bytes} bytes)"
                )
                sys.exit(1)
            elif len(message) < max_data_bytes:
                message += bytearray(max_data_bytes - len(message))
        else:
            message = bytearray(random.getrandbits(8) for _ in range(max_data_bytes))

        run_test(
            bch,
            message,
            num_errors=args.num_errors,
            specific_bits=specific_bits,
            use_hamming=False,
        )

    else:
        # Using bchlib
        try:
            bch = bchlib.BCH(args.t, m=args.m)
        except ValueError as e:
            print(f"Error initializing bchlib.BCH: {e}")
            sys.exit(1)
        max_data_bits = bch.n - bch.ecc_bits
        max_data_bytes = max_data_bits // 8

        print(f"n (codeword length): {bch.n} bits")
        print(f"ecc_bits: {bch.ecc_bits} bits")
        print(f"ecc_bytes: {bch.ecc_bytes} bytes")
        print(f"t (error correction capability): {bch.t}")
        print(f"Maximum data bits: {max_data_bits} bits")
        print(f"Maximum data bytes: {max_data_bytes} bytes")

        if args.message:
            try:
                message = bytearray.fromhex(args.message)
            except ValueError:
                print("Error: -message must be a valid hexadecimal string.")
                sys.exit(1)
            if len(message) > max_data_bytes:
                print(
                    f"Error: Message length exceeds maximum allowed ({max_data_bytes} bytes)"
                )
                sys.exit(1)
            elif len(message) < max_data_bytes:
                message += bytearray(max_data_bytes - len(message))
        else:
            message = bytearray(random.getrandbits(8) for _ in range(max_data_bytes))

        run_test(
            bch,
            message,
            num_errors=args.num_errors,
            specific_bits=specific_bits,
            use_hamming=False,
        )


if __name__ == "__main__":
    main()
