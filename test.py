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


class SimpleBCH:
    def __init__(self, n, k, t):
        self.n = n  # Length of codeword
        self.k = k  # Length of message
        self.t = t  # Error correction capability

    def encode(self, message):
        message_bits = self._hex_to_bits(message, self.k)
        if len(message_bits) > self.k:
            raise ValueError("Message length exceeds maximum allowed.")
        parity_bits = self._calculate_parity(message_bits)
        return message_bits + parity_bits

    def decode(self, codeword):
        data_bits = codeword[: self.k]
        recv_parity = codeword[self.k :]
        calc_parity = self._calculate_parity(data_bits)
        errors = [i for i in range(self.n) if recv_parity[i] != calc_parity[i]]
        return data_bits, errors

    def correct(self, codeword, errors):
        for error in errors:
            codeword[error] ^= 1
        return codeword

    def _hex_to_bits(self, hex_data, length):
        bits = [int(b) for b in bin(int(hex_data, 16))[2:].zfill(length)]
        return bits[:length]

    def _calculate_parity(self, data_bits):
        parity_bits = [0] * (self.n - self.k)
        for i in range(self.k):
            for j in range(len(parity_bits)):
                parity_bits[j] ^= data_bits[i] if (i + 1) & (1 << j) else 0
        return parity_bits


def inject_errors(data, num_errors, specific_bits=None):
    if specific_bits:
        error_positions = specific_bits
    else:
        error_positions = random.sample(range(len(data)), num_errors)

    corrupted_data = data[:]
    for bit in error_positions:
        corrupted_data[bit] ^= 1
    return corrupted_data, error_positions


def encode_message_with_fallback(m, t, message):
    try:
        bch = bchlib.BCH(t, m)
        return bch, bch.encode(bytearray.fromhex(message))
    except (RuntimeError, ValueError):
        logging.info("Switching to SimpleBCH for short codes.")
        simple_bch = SimpleBCH(n=7, k=4, t=1)
        codeword = simple_bch.encode(message)
        return simple_bch, codeword


def decode_and_correct_with_fallback(encoder, corrupted_codeword):
    if isinstance(encoder, SimpleBCH):
        data_bits, errors = encoder.decode(corrupted_codeword)
        corrected_codeword = encoder.correct(corrupted_codeword[:], errors)
        return corrected_codeword, errors
    else:
        data = corrupted_codeword[: -encoder.ecc_bytes]
        recv_ecc = corrupted_codeword[-encoder.ecc_bytes :]
        nerr = encoder.decode(data, recv_ecc)
        if nerr >= 0:
            corrected_data = bytearray(data)
            corrected_ecc = bytearray(recv_ecc)
            encoder.correct(corrected_data, corrected_ecc)
            return corrected_data + corrected_ecc, encoder.errloc
        else:
            return None, None


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

    specific_bits = (
        [int(bit.strip()) for bit in args.error_bits.split(",")]
        if args.error_bits
        else None
    )

    encoder, encoded_codeword = encode_message_with_fallback(
        args.m, args.t, args.message
    )
    logging.info(f"\nEncoded Codeword: {encoded_codeword}")

    if args.num_errors > 0:
        corrupted_codeword, injected_bits = inject_errors(
            encoded_codeword, args.num_errors, specific_bits
        )
        logging.info(f"\nCorrupted Codeword: {corrupted_codeword}")
    else:
        corrupted_codeword = encoded_codeword

    corrected_codeword, corrected_bits = decode_and_correct_with_fallback(
        encoder, corrupted_codeword
    )
    if corrected_codeword:
        logging.info(f"\nCorrected Codeword: {corrected_codeword}")
    else:
        logging.error("Decoding failed. Unable to correct the errors.")


if __name__ == "__main__":
    main()
