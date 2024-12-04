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
logging.basicConfig(level=logging.INFO, format='%(message)s')

def hamming_7_4_encode(data_bits):
    """Encode 4 bits of data into 7 bits using Hamming (7,4) code."""
    d = data_bits  # Should be a list of 4 bits
    c = [0] * 7
    c[3] = d[0]
    c[4] = d[1]
    c[5] = d[2]
    c[6] = d[3]
    c[0] = d[0] ^ d[1] ^ d[3]  # c1
    c[1] = d[0] ^ d[2] ^ d[3]  # c2
    c[2] = d[1] ^ d[2] ^ d[3]  # c3
    return c

def hamming_7_4_decode(codeword):
    """Decode 7 bits codeword into 4 bits of data using Hamming (7,4) code."""
    r = codeword  # Should be a list of 7 bits
    s = [0, 0, 0]
    s[0] = r[0] ^ r[3] ^ r[4] ^ r[6]
    s[1] = r[1] ^ r[3] ^ r[5] ^ r[6]
    s[2] = r[2] ^ r[4] ^ r[5] ^ r[6]
    syndrome = (s[0] << 2) | (s[1] << 1) | s[2]
    if syndrome != 0:
        error_pos = syndrome - 1  # Positions are from 0 to 6
        r[error_pos] ^= 1  # Correct the error
    data_bits = [r[3], r[4], r[5], r[6]]
    return data_bits, syndrome

def log_colored(message, color):
    """Log messages with color."""
    logging.info(f"{color}{message}{Style.RESET_ALL}")

def bitflip(data, bit):
    """Flip a specific bit in data."""
    if isinstance(data, bytearray):
        byte_index = bit // 8
        bit_index = bit % 8
        data[byte_index] ^= 1 << bit_index
    elif isinstance(data, list):
        data[bit] ^= 1
    else:
        raise TypeError("Unsupported data type for bitflip")

def encode_message(bch, data):
    """Encode the data using BCH encoder."""
    ecc = bch.encode(data)
    return data + ecc

def inject_errors(data, num_errors):
    """Inject a specified number of bit errors into the data."""
    if isinstance(data, bytearray):
        data_with_errors = bytearray(data)
        data_len_bits = len(data_with_errors) * 8
        error_positions = random.sample(range(data_len_bits), num_errors)
        for bit in error_positions:
            bitflip(data_with_errors, bit)
    elif isinstance(data, list):
        data_with_errors = data[:]
        data_len_bits = len(data_with_errors)
        error_positions = random.sample(range(data_len_bits), num_errors)
        for bit in error_positions:
            bitflip(data_with_errors, bit)
    else:
        raise TypeError("Unsupported data type for inject_errors")
    return data_with_errors, error_positions

def decode_and_correct(bch, corrupted_data):
    """Decode and correct the corrupted data."""
    data = corrupted_data[:-bch.ecc_bytes]
    recv_ecc = corrupted_data[-bch.ecc_bytes:]

    nerr = bch.decode(data, recv_ecc)
    if nerr >= 0:
        corrected_data = bytearray(data)
        corrected_ecc = bytearray(recv_ecc)
        bch.correct(corrected_data, corrected_ecc)
        return corrected_data + corrected_ecc, bch.errloc
    else:
        return None, None

def visualize_changes(original, corrupted, corrected, injected_bits, corrected_bits):
    """Visualize changes with colors for errors and corrections."""
    output = []
    if isinstance(original, bytearray):
        total_bits = len(original) * 8

        for bit in range(total_bits):
            byte_index = bit // 8
            bit_in_byte = 7 - (bit % 8)
            bit_mask = 1 << bit_in_byte

            orig_bit = (original[byte_index] >> bit_in_byte) & 1
            corru_bit = (corrupted[byte_index] >> bit_in_byte) & 1
            corrected_bit = (corrected[byte_index] >> bit_in_byte) & 1

            if bit in injected_bits and bit in corrected_bits:
                # Injected and corrected
                output.append(Fore.RED + f"{orig_bit}" + Fore.GREEN + f"{corrected_bit}" + Style.RESET_ALL)
            elif bit in injected_bits:
                # Injected but not corrected
                output.append(Fore.RED + f"{corru_bit}" + Style.RESET_ALL)
            elif bit in corrected_bits:
                # Corrected
                output.append(Fore.GREEN + f"{corrected_bit}" + Style.RESET_ALL)
            else:
                # Unchanged
                output.append(f"{orig_bit}")

            # Add a space every 8 bits
            if bit % 8 == 7:
                output.append(" ")

    elif isinstance(original, list):
        total_bits = len(original)
        for bit in range(total_bits):
            orig_bit = original[bit]
            corru_bit = corrupted[bit]
            corrected_bit = corrected[bit]

            if bit in injected_bits and bit in corrected_bits:
                # Injected and corrected
                output.append(Fore.RED + f"{orig_bit}" + Fore.GREEN + f"{corrected_bit}" + Style.RESET_ALL)
            elif bit in injected_bits:
                # Injected but not corrected
                output.append(Fore.RED + f"{corru_bit}" + Style.RESET_ALL)
            elif bit in corrected_bits:
                # Corrected
                output.append(Fore.GREEN + f"{corrected_bit}" + Style.RESET_ALL)
            else:
                # Unchanged
                output.append(f"{orig_bit}")
    else:
        raise TypeError("Unsupported data type for visualize_changes")

    return ''.join(output)

def run_test(bch, message, num_errors=0, use_hamming=False):
    """Run a test by encoding, injecting errors, and decoding."""
    logging.info(f"\n{'-'*40}\nOriginal Message:")
    if use_hamming:
        logging.info(''.join(str(b) for b in message))
        # Encode the message
        codeword = hamming_7_4_encode(message)
        logging.info("\nEncoded Codeword:")
        logging.info(''.join(str(b) for b in codeword))

        # Inject errors
        if num_errors > 0:
            corrupted_codeword, injected_bits = inject_errors(codeword, num_errors)
            log_colored(f"\nInjected {num_errors} Errors at bit positions: {injected_bits}", Fore.RED)
            logging.info("Corrupted Codeword:")
            logging.info(''.join(str(b) for b in corrupted_codeword))
        else:
            corrupted_codeword = codeword
            injected_bits = []

        # Decode and correct
        corrected_data_bits, syndrome = hamming_7_4_decode(corrupted_codeword)
        corrected_codeword = corrupted_codeword
        logging.info("\nCorrected Codeword:")
        logging.info(''.join(str(b) for b in corrected_codeword))
        logging.info("\nDecoded Message:")
        logging.info(''.join(str(b) for b in corrected_data_bits))

        # Visualize the changes
        logging.info("\nVisualized Changes (bits):")
        corrected_bits = []
        if syndrome != 0:
            corrected_bits = [syndrome - 1]
        visualization = visualize_changes(codeword, corrupted_codeword, corrected_codeword, injected_bits, corrected_bits)
        logging.info(visualization)

        # Log corrected and injected bits
        if corrected_bits:
            log_colored("\nCorrected Bit Positions:", Fore.GREEN)
            for bit in corrected_bits:
                log_colored(f"Bit {bit}", Fore.GREEN)

        if injected_bits:
            log_colored("\nInjected Bit Positions:", Fore.RED)
            for bit in injected_bits:
                log_colored(f"Bit {bit}", Fore.RED)

        # Check if all injected errors were corrected
        if set(injected_bits) == set(corrected_bits):
            log_colored("\nAll injected errors were successfully corrected!", Fore.GREEN)
        else:
            log_colored("\nSome injected errors were not corrected!", Fore.RED)
    else:
        # Existing code for BCH
        logging.info(message.hex())

        # Encode the message
        codeword = encode_message(bch, message)
        logging.info("\nEncoded Codeword:")
        logging.info(codeword.hex())

        # Inject errors
        if num_errors > 0:
            corrupted_codeword, injected_bits = inject_errors(codeword, num_errors)
            log_colored(f"\nInjected {num_errors} Errors at bit positions: {injected_bits}", Fore.RED)
            logging.info("Corrupted Codeword:")
            logging.info(corrupted_codeword.hex())
        else:
            corrupted_codeword = codeword
            injected_bits = []

        # Decode and correct
        corrected_codeword, corrected_bits = decode_and_correct(bch, corrupted_codeword)
        if corrected_codeword:
            logging.info("\nCorrected Codeword:")
            logging.info(corrected_codeword.hex())

            # Visualize the changes
            logging.info("\nVisualized Changes (bits):")
            visualization = visualize_changes(codeword, corrupted_codeword, corrected_codeword, injected_bits, corrected_bits)
            logging.info(visualization)

            # Log corrected and injected bits
            if corrected_bits:
                log_colored("\nCorrected Bit Positions:", Fore.GREEN)
                for bit in corrected_bits:
                    log_colored(f"Bit {bit}", Fore.GREEN)

            if injected_bits:
                log_colored("\nInjected Bit Positions:", Fore.RED)
                for bit in injected_bits:
                    log_colored(f"Bit {bit}", Fore.RED)

            # Check if all injected errors were corrected
            if set(injected_bits) == set(corrected_bits):
                log_colored("\nAll injected errors were successfully corrected!", Fore.GREEN)
            else:
                log_colored("\nSome injected errors were not corrected!", Fore.RED)
        else:
            logging.error("Decoding failed. Unable to correct the errors.")

def main():
    parser = argparse.ArgumentParser(description='BCH Encoder and Decoder with Error Injection')
    parser.add_argument('-t', type=int, default=5, help='Error correction capability (default: 5)')
    parser.add_argument('-m', type=int, default=8, help='Galois Field order (default: 8)')
    parser.add_argument('-message', type=str, help='Message to encode in hexadecimal')
    parser.add_argument('-num_errors', type=int, default=0, help='Number of bit errors to inject (default: 0)')
    parser.add_argument('-verbose', action='store_true', help='Enable detailed logging')
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine if we should use Hamming code
    if args.m < 5:
        use_hamming = True
    else:
        use_hamming = False

    if use_hamming:
        # For Hamming (7,4) code
        n = 7
        k = 4
        t = 1
        print(f"Using Hamming (7,4) Code")
        print(f"n (codeword length): {n} bits")
        print(f"k (message length): {k} bits")
        print(f"t (error correction capability): {t}")
        # Prepare message
        if args.message:
            message = args.message
            message_bits = bin(int(message, 16))[2:].zfill(4)
            message_bits = [int(b) for b in message_bits[-4:]]
        else:
            message_bits = [random.randint(0,1) for _ in range(4)]
        # Run test
        run_test(None, message_bits, num_errors=args.num_errors, use_hamming=True)
    else:
        # Initialize BCH
        bch = bchlib.BCH(args.t, m=args.m)

        # Compute maximum data length in bits and bytes
        max_data_bits = bch.n - bch.ecc_bits
        max_data_bytes = max_data_bits // 8

        print(f"n (codeword length): {bch.n} bits")
        print(f"ecc_bits: {bch.ecc_bits} bits")
        print(f"ecc_bytes: {bch.ecc_bytes} bytes")
        print(f"t (error correction capability): {bch.t}")
        print(f"Maximum data bits: {max_data_bits} bits")
        print(f"Maximum data bytes: {max_data_bytes} bytes")

        # Prepare message
        if args.message:
            message = bytearray.fromhex(args.message)
            if len(message) > max_data_bytes:
                print(f"Error: Message length exceeds maximum allowed ({max_data_bytes} bytes)")
                sys.exit(1)
            elif len(message) < max_data_bytes:
                message += bytearray(max_data_bytes - len(message))
        else:
            # Generate random message of maximum length
            message = bytearray(random.getrandbits(8) for _ in range(max_data_bytes))

        # Run test
        run_test(bch, message, num_errors=args.num_errors)

if __name__ == "__main__":
    main()
