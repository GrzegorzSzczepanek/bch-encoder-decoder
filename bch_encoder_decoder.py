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

def log_colored(message, color):
    """Log messages with color."""
    logging.info(f"{color}{message}{Style.RESET_ALL}")

def bitflip(data, bit):
    """Flip a specific bit in a bytearray."""
    byte_index = bit // 8
    bit_index = bit % 8
    data[byte_index] ^= 1 << bit_index

def encode_message(bch, data):
    """Encode the data using BCH encoder."""
    ecc = bch.encode(data)
    return data + ecc

def inject_errors(data, num_errors):
    """Inject a specified number of bit errors into the data."""
    data_with_errors = bytearray(data)
    data_len_bits = len(data_with_errors) * 8
    error_positions = random.sample(range(data_len_bits), num_errors)
    for bit in error_positions:
        bitflip(data_with_errors, bit)
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

    return ''.join(output)

def run_test(bch, message, num_errors=0):
    """Run a test by encoding, injecting errors, and decoding."""
    logging.info(f"\n{'-'*40}\nOriginal Message:")
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

        # Check if all injected bits were corrected
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
    else:
        # Generate random message of maximum length
        message = bytearray(random.getrandbits(8) for _ in range(max_data_bytes))

    # Run test
    run_test(bch, message, num_errors=args.num_errors)

if __name__ == "__main__":
    main()
