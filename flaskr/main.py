from crypt import methods
import io
from tracemalloc import stop
from urllib import response
from PIL import Image

from flask import (Flask, flash, jsonify, make_response, redirect, request,
                   send_file)

from salsa import Salsa

app = Flask(__name__)
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
		return response


@app.route("/encrypt-image/", methods=['GET','POST'])
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

		fileBytes = request.files['file'].read()
		im = Image.open(fileBytes)
		print(im)


		image = bytearray(fileBytes)

		result = __salsa_encrypt_image(image)

		return send_file(io.BytesIO(bytes(result)), 'image/png')


def __salsa_encrypt_image(image: bytearray) -> list:
	"""Encrypts or decrypts an image with Salsa20 Symmetric Stream Cypher."""

	s = Salsa()
	salsa20 = s()
	result = []
	salsa20 = __int_array_to_bytes_array(salsa20)
	for i in enumerate(image):
		result.append(salsa20[i % 64] ^ image[i])
	return result


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