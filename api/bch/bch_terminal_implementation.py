import argparse

def poly_mul(a, b):
    """
    Polynomial multiplication over GF(2).

    Args:
        a (int): First polynomial.
        b (int): Second polynomial.

    Returns:
        int: Resulting polynomial after multiplication.
    """
    result = 0
    while b:
        if b & 1:
            result ^= a  # XOR for addition in GF(2)
        a <<= 1
        b >>= 1
    return result

def poly_div(dividend, divisor):
    """
    Polynomial division over GF(2).

    Args:
        dividend (int): Dividend polynomial.
        divisor (int): Divisor polynomial.

    Returns:
        tuple: (quotient, remainder) of the division.
    """
    deg_dividend = dividend.bit_length() - 1
    deg_divisor = divisor.bit_length() - 1
    quotient = 0
    while deg_dividend >= deg_divisor and dividend != 0:
        shift = deg_dividend - deg_divisor
        quotient ^= (1 << shift)
        dividend ^= (divisor << shift)
        deg_dividend = dividend.bit_length() - 1
    remainder = dividend
    return quotient, remainder

def gf16_generate_tables():
    """
    Generate exponentiation and logarithm tables for GF(16).

    Returns:
        tuple: (exp_table, log_table) for GF(16).
    """
    p = 0b10011  # Primitive polynomial for GF(16)
    exp_table = [0] * 30  # Exponentiation table
    log_table = [0] * 16  # Logarithm table
    x = 1
    for i in range(15):
        exp_table[i] = x
        log_table[x] = i
        x <<= 1  # Multiply by alpha
        if x & 0x10:  # If degree >= 4
            x ^= p  # Reduce modulo primitive polynomial
    for i in range(15, 30):
        exp_table[i] = exp_table[i - 15]  # Repeat the table for easy modulo operations
    return exp_table, log_table

def gf16_add(a, b):
    """
    Addition in GF(16), which is just XOR.

    Args:
        a (int): First element.
        b (int): Second element.

    Returns:
        int: Result of addition.
    """
    return a ^ b

def gf16_mul(a, b, exp_table, log_table):
    """
    Multiplication in GF(16) using log and exp tables.

    Args:
        a (int): First element.
        b (int): Second element.
        exp_table (list): Exponentiation table.
        log_table (list): Logarithm table.

    Returns:
        int: Result of multiplication.
    """
    if a == 0 or b == 0:
        return 0
    else:
        log_a = log_table[a]
        log_b = log_table[b]
        log_result = (log_a + log_b) % 15
        return exp_table[log_result]

def gf16_inv(a, exp_table, log_table):
    """
    Multiplicative inverse in GF(16).

    Args:
        a (int): Element to invert.
        exp_table (list): Exponentiation table.
        log_table (list): Logarithm table.

    Returns:
        int: Multiplicative inverse of a.
    """
    if a == 0:
        raise ZeroDivisionError("Cannot invert zero in GF(16)")
    else:
        log_a = log_table[a]
        log_inv = (15 - log_a) % 15
        return exp_table[log_inv]

def codeword_to_bits(codeword_int, n):
    """
    Convert codeword integer to a list of bits.

    Args:
        codeword_int (int): Codeword as an integer.
        n (int): Length of the codeword.

    Returns:
        list: List of bits representing the codeword.
    """
    bits = [(codeword_int >> (n - 1 - i)) & 1 for i in range(n)]
    return bits

def compute_syndromes(codeword_bits, exp_table, log_table):
    """
    Compute syndromes for error detection.

    Args:
        codeword_bits (list): List of bits in the codeword.
        exp_table (list): Exponentiation table.
        log_table (list): Logarithm table.

    Returns:
        list: List of syndromes S1 to S4.
    """
    syndromes = []
    n = len(codeword_bits)
    for i in range(1, 5):
        s = 0
        for j in range(n):
            if codeword_bits[j]:
                exponent = (i * j) % 15
                s = gf16_add(s, exp_table[exponent])
        syndromes.append(s)
    return syndromes

def solve_error_locator(syndromes, exp_table, log_table):
    """
    Solve for the error locator polynomial coefficients.

    Args:
        syndromes (list): List of syndromes S1 to S4.
        exp_table (list): Exponentiation table.
        log_table (list): Logarithm table.

    Returns:
        list or None: Error locator polynomial coefficients or None if errors are uncorrectable.
    """
    S1, S2, S3, S4 = syndromes
    # Compute determinant D
    D = gf16_add(gf16_mul(S1, S3, exp_table, log_table), gf16_mul(S2, S2, exp_table, log_table))
    if D == 0:
        return None  # Cannot solve for error locator polynomial
    else:
        inv_D = gf16_inv(D, exp_table, log_table)
        # Compute error locator polynomial coefficients
        N1 = gf16_add(gf16_mul(S3, S3, exp_table, log_table), gf16_mul(S2, S4, exp_table, log_table))
        σ1 = gf16_mul(N1, inv_D, exp_table, log_table)
        N2 = gf16_add(gf16_mul(S1, S4, exp_table, log_table), gf16_mul(S2, S3, exp_table, log_table))
        σ2 = gf16_mul(N2, inv_D, exp_table, log_table)
        return [1, σ1, σ2]  # Error locator polynomial σ(x) = x^2 + σ1*x + σ2

def chien_search(error_locator_poly, exp_table, log_table):
    """
    Perform Chien search to find error positions.

    Args:
        error_locator_poly (list): Error locator polynomial coefficients.
        exp_table (list): Exponentiation table.
        log_table (list): Logarithm table.

    Returns:
        list: Positions of errors in the codeword.
    """
    error_positions = []
    n = 15  # Length of the codeword
    for i in range(n):
        # Evaluate σ(α^{-i}) where α is primitive element
        inv_alpha_i = exp_table[(15 - i) % 15]
        term1 = gf16_mul(error_locator_poly[0], gf16_mul(inv_alpha_i, inv_alpha_i, exp_table, log_table), exp_table, log_table)
        term2 = gf16_mul(error_locator_poly[1], inv_alpha_i, exp_table, log_table)
        term3 = error_locator_poly[2]
        sigma_eval = gf16_add(term1, gf16_add(term2, term3))
        if sigma_eval == 0:
            error_positions.append(i)
    return error_positions

def encode(n, k, message):
    """
    Encode a message using the (15,7) BCH code.

    Args:
        n (int): Length of the codeword.
        k (int): Length of the message.
        message (str): Binary string representing the message.

    Returns:
        None
    """
    try:
        print("Starting encoding process...")
        if n != 15 or k != 7:
            print('This encoder only supports the (15,7) BCH code.')
            return
        if len(message) != k:
            print(f'Message length must be {k} bits.')
            return
        m = int(message, 2)
        print(f"Message integer: {m}")
        m_shifted = m << (n - k)
        print(f"Shifted message: {bin(m_shifted)}")
        g = 0b111010001  # Generator polynomial for (15,7) BCH code
        print(f"Generator polynomial: {bin(g)}")
        _, remainder = poly_div(m_shifted, g)
        print(f"Remainder after division: {bin(remainder)}")
        codeword = m_shifted + remainder
        codeword_str = bin(codeword)[2:].zfill(n)
        print('Encoded codeword:', codeword_str)
    except Exception as e:
        print(f"An error occurred during encoding: {e}")

def decode(n, k, codeword_str):
    """
    Decode a codeword using the (15,7) BCH code.

    Args:
        n (int): Length of the codeword.
        k (int): Length of the message.
        codeword_str (str): Binary string representing the codeword.

    Returns:
        None
    """
    try:
        print("Starting decoding process...")
        if n != 15 or k != 7:
            print('This decoder only supports the (15,7) BCH code.')
            return
        if len(codeword_str) != n:
            print(f'Codeword length must be {n} bits.')
            return
        codeword_int = int(codeword_str, 2)
        codeword_bits = codeword_to_bits(codeword_int, n)
        exp_table, log_table = gf16_generate_tables()
        syndromes = compute_syndromes(codeword_bits, exp_table, log_table)
        print(f"Syndromes: {syndromes}")
        if all(s == 0 for s in syndromes):
            print('No errors detected.')
            corrected_codeword_bits = codeword_bits
        else:
            error_locator_poly = solve_error_locator(syndromes, exp_table, log_table)
            if error_locator_poly is None:
                print('Errors cannot be corrected (more than 2 errors).')
                return
            else:
                error_positions = chien_search(error_locator_poly, exp_table, log_table)
                if len(error_positions) > 2:
                    print('Errors cannot be corrected (more than 2 errors).')
                    return
                else:
                    corrected_codeword_bits = codeword_bits.copy()
                    for pos in error_positions:
                        corrected_codeword_bits[pos] ^= 1  # Correct the error
                    print('Errors corrected at positions:', error_positions)
        # Extract the original message from the corrected codeword
        message_bits = corrected_codeword_bits[:k]
        message_str = ''.join(str(bit) for bit in message_bits)
        print('Decoded message:', message_str)
    except Exception as e:
        print(f"An error occurred during decoding: {e}")

def main():
    """
    Main function to parse command-line arguments and execute encode or decode.
    """
    parser = argparse.ArgumentParser(description='BCH encoder and decoder')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Subparser for encoding
    parser_encode = subparsers.add_parser('encode', help='Encode a message')
    parser_encode.add_argument('-n', type=int, required=True, help='Codeword length (must be 15)')
    parser_encode.add_argument('-k', type=int, required=True, help='Message length (must be 7)')
    parser_encode.add_argument('-message', type=str, required=True, help='Message to encode in binary string')

    # Subparser for decoding
    parser_decode = subparsers.add_parser('decode', help='Decode a codeword')
    parser_decode.add_argument('-n', type=int, required=True, help='Codeword length (must be 15)')
    parser_decode.add_argument('-k', type=int, required=True, help='Message length (must be 7)')
    parser_decode.add_argument('-codeword', type=str, required=True, help='Codeword to decode in binary string')

    args = parser.parse_args()

    if args.command == 'encode':
        encode(args.n, args.k, args.message)
    elif args.command == 'decode':
        decode(args.n, args.k, args.codeword)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
