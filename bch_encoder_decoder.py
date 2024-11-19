#!/usr/bin/env python3

import bchlib
import random
import logging
import sys

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

    # Debugging statements
    print(f"Data length: {len(data)} bytes")
    print(f"Recv ECC length: {len(recv_ecc)} bytes")
    print(f"Expected ECC bytes: {bch.ecc_bytes}")

    nerr = bch.decode(data, recv_ecc)
    if nerr >= 0:
        corrected_data = bytearray(data)
        corrected_ecc = bytearray(recv_ecc)
        bch.correct(corrected_data, corrected_ecc)
        return corrected_data + corrected_ecc, bch.errloc
    else:
        return None, None

def run_test(bch, message, num_errors=0):
    """Run a test by encoding, injecting errors, and decoding."""
    logging.info("Original Message:")
    logging.info(message.hex())

    # Encode the message
    codeword = encode_message(bch, message)
    logging.info("\nEncoded Codeword:")
    logging.info(codeword.hex())

    # Inject errors
    if num_errors > 0:
        corrupted_codeword, error_positions = inject_errors(codeword, num_errors)
        logging.info(f"\nInjected {num_errors} Errors at bit positions: {error_positions}")
        logging.info("Corrupted Codeword:")
        logging.info(corrupted_codeword.hex())
    else:
        corrupted_codeword = codeword
        error_positions = []

    # Decode and correct
    corrected_codeword, corrected_positions = decode_and_correct(bch, corrupted_codeword)
    if corrected_codeword:
        logging.info("\nCorrected Codeword:")
        logging.info(corrected_codeword.hex())

        # Compare original and corrected codeword
        differences = []
        for i in range(len(codeword)):
            if codeword[i] != corrected_codeword[i]:
                differences.append(i)

        # Logging the corrections
        if differences:
            logging.info("\nDifferences found at byte positions:")
            for idx in differences:
                byte_diff = f"Byte {idx}: Original {codeword[idx]:02X}, Corrected {corrected_codeword[idx]:02X}"
                log_colored(byte_diff, Fore.RED)

        else:
            logging.info("\nNo differences found between original and corrected codeword.")

        # Show corrected bits
        if corrected_positions:
            logging.info("\nCorrected Bit Positions:")
            for bit in corrected_positions:
                bit_info = f"Bit {bit}"
                log_colored(bit_info, Fore.GREEN)

    else:
        logging.error("Decoding failed. Unable to correct the errors.")

def main():
    # Parameters for BCH
    t = 5  # Error correction capability
    m = 8  # Galois Field GF(2^m), allows codeword lengths up to 2^m - 1
    bch = bchlib.BCH(t, m=m)

    # Compute maximum data length in bits and bytes
    max_data_bits = bch.n - bch.ecc_bits
    max_data_bytes = max_data_bits // 8

    print(f"n (codeword length): {bch.n} bits")
    print(f"ecc_bits: {bch.ecc_bits} bits")
    print(f"ecc_bytes: {bch.ecc_bytes} bytes")
    print(f"t (error correction capability): {bch.t}")
    print(f"Maximum data bits: {max_data_bits} bits")
    print(f"Maximum data bytes: {max_data_bytes} bytes")

    # Generate random message of maximum length
    message = bytearray(random.getrandbits(8) for _ in range(max_data_bytes))

    # Run test without error injection
    logging.info("\nRunning test without error injection:")
    run_test(bch, message, num_errors=0)

    # Run test with error injection
    logging.info("\nRunning test with error injection:")
    num_errors = t  # Inject up to t errors
    run_test(bch, message, num_errors=num_errors)

if __name__ == "__main__":
    main()
