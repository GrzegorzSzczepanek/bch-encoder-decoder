from flask import Flask, request, jsonify, render_template
from api.bch.bch import BchCoder, BchCodeGenerator
from api.bch.utils import padding_encode, padding_decode
from sympy import Poly, symbols


app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return 'About'

@app.route('/encode', methods=['POST'])
def encode_message():
    # Get message from request
    message = request.json.get('message')
    
    # Validate that the message only contains binary digits (0 or 1)
    if not all(bit in '01' for bit in message):
        return jsonify({"error": "Input message must be a binary string (only 0s and 1s)"}), 400
    
    # Initialize the BCH code generator and encoder
    bch_gen = BchCodeGenerator(15, 7, 3)
    r, g = bch_gen.gen()
    bch = BchCoder(15, 7, 3, r, g)

    # Convert the binary message string into a list of integers
    message_bits = [int(bit) for bit in message]  # Convert string to a list of integers
    x = symbols('x')
    encoded_message = bch.encode(Poly(message_bits[::-1], x))

    # Convert to a list of integers that can be serialized
    encoded_message_list = [int(coeff) for coeff in encoded_message]

    return jsonify({"encoded_message": encoded_message_list})



@app.route('/decode', methods=['POST'])
def decode_message():
    # Get the received (potentially noisy) message from request
    received_message = request.json.get('received_message')
    
    # Initialize the BCH code generator and decoder
    bch_gen = BchCodeGenerator(15, 7, 3)
    r, g = bch_gen.gen()
    bch = BchCoder(15, 7, 3, r, g)

    x = symbols('x')
    try:
        # Convert the received message to list of integers
        received_message_list = [int(bit) for bit in received_message]
        decoded_message = bch.decode(Poly(received_message_list[::-1], x))

        # Convert decoded message to a list of integers
        decoded_message_list = [int(coeff) for coeff in decoded_message]

        return jsonify({"decoded_message": decoded_message_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
