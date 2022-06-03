from crypt import methods
import io
from tracemalloc import stop
from urllib import response

from flask import (Flask, flash, jsonify, make_response, redirect, request,
                   send_file)

from salsa import Salsa

app = Flask(__name__)
app.secret_key = "secret key"

@app.route("/", methods=['GET'])
def hello_world():
	response = {'message': "Welcome to Salsa20 cipher"}
	return response


@app.route("/encrypt-text/", methods=['POST'])
def encrypt_text():
	if request.method == 'POST':
		to_be_encoded = request.get_json()['message']
		result = __salsa_encrypt_text(to_be_encoded)
		message = []
		for i in range(len(result)):
			message.append(chr(result[i]))
		message = ''.join(message)
		response = {'message': message}
		return response


@app.route("/encrypt-image/", methods=['POST'])
def encrypt_image():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)

		fileBytes = request.files['file'].read()
		image = bytearray(fileBytes)

		result = __salsa_encrypt_image(image)

		return send_file(io.BytesIO(bytes(result)), 'image/png')


def __salsa_encrypt_image(image: bytearray) -> list:
	"""Encrypts or decrypts an image with Salsa20 Symmetric Stream Cypher.\n
	Salsa20 output is a 64 bytes array, divided into 16 integers."""

	s = Salsa()
	salsa20 = s()
	result = []
	salsa20 = __int_array_to_bytes_array(salsa20)
	print(image)
	for i in enumerate(image):
		result.append(salsa20[i % 64] ^ image[i])
	return result


def __int_array_to_bytes_array(salsa20: list) -> list:
	bytes_array = []
	for i in range(len(salsa20)):
		temporal_array = salsa20[i].to_bytes(4, 'big')
		for j in range(len(temporal_array)):
			bytes_array.append(temporal_array[j])
	assert len(bytes_array) == 64
	return bytes_array


def __salsa_encrypt_text(text: str) -> list :
	s = Salsa()
	salsa20 = s()
	result = []
	textBytes = bytearray(__string_to_bytes_array(text))
	salsa20 = __int_array_to_bytes_array(salsa20)
	for i in range(len(textBytes)):
		result.append(salsa20[i % 64] ^ textBytes[i])
	
	return result


def __string_to_bytes_array(text: str) -> list:
	char_array = split(text)
	print(char_array)

	bytes_array = []
	for i in range(len(char_array)):
		bytes_array.append(ord(char_array[i]).to_bytes(1, 'big')[0])
	
	print(bytes_array)
	return bytes_array

def split(text: str):
    return [char for char in text]