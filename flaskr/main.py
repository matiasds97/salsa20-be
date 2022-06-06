from crypt import methods
import io
from os import stat
from PIL import Image

from flask import (Flask, flash, make_response, redirect, request, send_file)
from flask_cors import CORS, cross_origin
from salsa import Salsa

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.secret_key = "secret key"

@app.route("/", methods=['GET'])
def hello_world():
	"""Handles get requests to the API."""

	response = {'message': "Welcome to Salsa20 cipher"}
	return response


@app.route("/encrypt-text/", methods=['POST'])
def encrypt_text():
	"""Handles requests to encrypt or decrypt
	text with Salsa20 stream cipher."""

	if request.method == 'POST':
		to_be_encoded = request.get_json()['message']
		result = __salsa_encrypt_text(to_be_encoded)
		message = []
		for i in range(len(result)):
			message.append(chr(result[i]))
		message = ''.join(message)
		response = {'message': message}
		return response, 200
		# return response


@app.route("/encrypt-image/", methods=['POST'])
def encrypt_image():
	"""Handles requests to encrypt or decrypt
	an image with Salsa20 stream cipher."""

	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)

		im = Image.open(file)
		im = im.convert("RGB")

		result = __salsa_encrypt_image(im)
		img_io = io.BytesIO()
		result.save(img_io, 'PNG', quality=100)
		img_io.seek(0)
	
		return send_file(img_io, 'image/png')


def __salsa_encrypt_image(image: Image) -> Image:
	"""Encrypts or decrypts an image with Salsa20 Symmetric Stream Cypher."""


	s = Salsa()
	salsa20 = s()
	result = []
	salsa20 = __int_array_to_bytes_array(salsa20)
	pixel_map = image.load()
	width = image.size[0]
	height = image.size[1]

	z = 0
	for i in range(width):
		for j in range(height):
			r, g, b = pixel_map[i,j]
			r = salsa20[z % 64] ^ r
			g = salsa20[z % 64] ^ g
			b = salsa20[z % 64] ^ b
			pixel_map[i,j] = r, g, b
			z = z + 1

	return image


def __int_array_to_bytes_array(salsa20: list) -> list:
	"""Converts an int array from Salsa20 to a bytes array."""

	bytes_array = []
	for i in range(len(salsa20)):
		temporal_array = salsa20[i].to_bytes(4, 'big')
		for j in range(len(temporal_array)):
			bytes_array.append(temporal_array[j])
	assert len(bytes_array) == 64
	return bytes_array


def __salsa_encrypt_text(text: str) -> list :
	"""Encrypts or decrypts a plain text with Salsa20 Symmetric Stream Cypher."""

	s = Salsa()
	salsa20 = s()
	result = []
	textBytes = bytearray(__string_to_bytes_array(text))
	salsa20 = __int_array_to_bytes_array(salsa20)
	for i in range(len(textBytes)):
		result.append(salsa20[i % 64] ^ textBytes[i])
	
	return result


def __string_to_bytes_array(text: str) -> list:
	"""Converts a string into a bytes array."""

	char_array = split(text)

	bytes_array = []
	for i in range(len(char_array)):
		bytes_array.append(ord(char_array[i]).to_bytes(1, 'big')[0])
	
	return bytes_array

def split(text: str):
	"""Splits a string into a char array."""
	
	return [char for char in text]


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response