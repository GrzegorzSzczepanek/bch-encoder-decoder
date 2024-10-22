import logging
from sympy import Poly, GF
from sympy.abc import x, alpha
from code_gen import BchCodeGenerator
from coder import BchCoder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("test_bch_code")

def test_bch_code():
    # Define code parameters
    n = 15  # Code length
    b = 1   # Starting exponent
    d = 5   # Designed minimum distance

    # Generate the code
    code_generator = BchCodeGenerator(n, b, d)
    irr_poly, g_poly = code_generator.gen()

    # Initialize the coder
    coder = BchCoder(n, b, d, irr_poly, g_poly)

    # Determine the message length k
    k = coder.k

    # Define a message to encode (length k)
    message_coeffs = [1 if i % 2 == 0 else 0 for i in range(k)]
    msg_poly = Poly(message_coeffs, x, domain=GF(2))

    # Encode the message
    encoded = coder.encode(msg_poly)
    print("Encoded message:", encoded)

    # Introduce errors (flip bits at specified positions)
    received = encoded.copy()
    error_positions = [2, 5]  # Positions where errors are introduced
    for pos in error_positions:
        received[pos] ^= 1  # Flip the bit

    print("Received message with errors:", received)

    # Decode the message
    received_poly = Poly(received, x, domain=GF(2))
    decoded_coeffs = coder.decode(received_poly)

    print("Decoded message coefficients:", decoded_coeffs)

    # Check if the decoded message matches the original message
    original_message = message_coeffs
    decoded_message = decoded_coeffs.tolist()

    print("Original message coefficients:", original_message)
    print("Decoded message coefficients:", decoded_message)

    if decoded_message == original_message:
        print("Decoding successful! The original message was correctly recovered.")
    else:
        print("Decoding failed. The decoded message does not match the original.")

# Run the test
test_bch_code()