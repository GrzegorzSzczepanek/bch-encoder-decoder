from sympy.abc import x, alpha
from sympy.polys.galoistools import gf_irreducible, gf_irreducible_p
from sympy import Poly, lcm, ZZ, GF
import numpy as np
from logging import log
from api.bch.utils import order, power_dict, minimal_poly

class BchCodeGenerator:
    """Class to generate BCH codes"""
    def __init__(self, n, b, d):
        """
        Initializes the BCH code parameters
        :param n: Code length
        :param b: Data length (number of information bits)
        :param d: Minimum Hamming distance
        """
        self.n = n
        self.b = b
        self.d = d
        self.q = 2
        self.m = order(self.q, self.n)
        print(f"BchCodeGenerator(n={self.n}, q={self.q}, m={self.m}, b={self.b}, d={self.d}) initiated")
    
    def gen(self):
        # Define the irreducible polynomial over GF(2)
        irr_poly = Poly(alpha ** self.m + alpha + 1, alpha, domain=GF(self.q))
        # Check if irr_poly is irreducible
        if gf_irreducible_p([int(c) for c in irr_poly.all_coeffs()], self.q, ZZ):
            quotient_size = len(power_dict(self.n, irr_poly, self.q))
        else:
            quotient_size = 0
        while quotient_size < self.n:
            irr_coeffs = [int(c.numerator) for c in gf_irreducible(self.m, self.q, ZZ)]
            irr_poly = Poly(irr_coeffs, alpha, domain=GF(self.q))
            quotient_size = len(power_dict(self.n, irr_poly, self.q))
        g_poly = None
        for i in range(self.b, self.b + self.d - 1):
            min_poly = minimal_poly(i, self.n, self.q, irr_poly)
            if g_poly is None:
                g_poly = min_poly
            else:
                g_poly = lcm(g_poly, min_poly).trunc(self.q)
        g_poly = g_poly.set_domain(GF(self.q))
        return irr_poly, g_poly


class BchCoder:
    """Class to encode and decode messages using BCH code"""
    def __init__(self, n, b, d, r, g):
        """
        Initializes the BCH encoder/decoder with provided generator and parity polynomials.
        :param n: Code length
        :param b: Data length
        :param d: Minimum Hamming distance
        :param r: Parity check polynomial
        :param g: Generator polynomial
        """
        self.n = n
        self.b = b
        self.d = d
        self.r = r
        self.g = g
        self.k = n - b  # The number of parity bits

    def encode(self, message_poly):
        """
        Encodes a message using the BCH code.
        :param message_poly: Polynomial representing the message
        :return: Encoded message as a numpy array
        """
        # Multiply message by generator polynomial to get the encoded codeword
        encoded = message_poly * self.g
        return np.array(encoded.all_coeffs())

    def decode(self, received_poly):
        """
        Decodes the received polynomial, detecting and correcting errors if needed.
        :param received_poly: Polynomial representing the received message (with errors)
        :return: Decoded message
        """
        # Syndrome computation to detect errors (needs more detail in practical scenarios)
        syndrome = received_poly % self.g
        if syndrome == 0:
            # No errors
            return np.array(received_poly.all_coeffs())
        else:
            # Error correction logic would go here (e.g., Berlekamp-Massey)
            raise Exception("Error detected in received message")

