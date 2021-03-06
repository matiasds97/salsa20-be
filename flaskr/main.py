from http.client import UNSUPPORTED_MEDIA_TYPE
import io
from PIL import Image
from flask import (Flask, flash, redirect, request, send_file)
from flask_cors import CORS
from salsa import Salsa

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.secret_key = "secret key"

ALLOWED_EXTENSIONS = {'png'}
UNSUPPORTED_MEDIA_TYPE = 415

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


@app.route("/encrypt-image/", methods=['POST'])
def encrypt_image():
	"""Handles requests to encrypt or decrypt
	an image with Salsa20 stream cipher."""

	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return {'error': 'No file part'}, 400
		
		
		file = request.files['file']
		if file.filename == '':
			return {'error': 'No file selected for uploading'}, 400


		if file and _allowed_file(file.filename):
			im = Image.open(file)
			im = im.convert("RGB")

			result = __salsa_encrypt_image(im)
			img_io = io.BytesIO()
			result.save(img_io, 'PNG', quality=100)
			img_io.seek(0)
	
			return send_file(img_io, 'image/png')

		response = {'error': "The uploaded file is not allowed."}
		return response, UNSUPPORTED_MEDIA_TYPE


def __salsa_encrypt_image(image: Image) -> Image:
	"""Encrypts or decrypts an image with Salsa20 Symmetric Stream Cypher."""

#Changed the key (1,33) #NONCE:  [3,1,4,1,5,9,2,6]
	vector = [range(101,133), [3,1,4,1,5,9,2,6], [7,0,0,0,0,0,0,0]]
	result = []
	z = 0
	block_counter = [0,0,0,0,0,0,0,0]
	s = Salsa()
	salsa20 = s(key=vector[0],nonce=vector[1], block_counter=block_counter) #Added
	salsa20 = __int_array_to_bytes_array(salsa20)
	pixel_map = image.load()
	width = image.size[0]
	height = image.size[1]
	
	
	for i in range(width):
		for j in range(height):
			r, g, b = pixel_map[i,j]
			r = salsa20[z % 64] ^ r
			g = salsa20[z % 64] ^ g
			b = salsa20[z % 64] ^ b
			pixel_map[i,j] = r, g, b
			z = z + 1

			#print("Z : ", z)
			if(z%64==63):
				block_counter[0]=block_counter[0]+1
				salsa20 = s(key=vector[0],nonce=vector[1], block_counter=block_counter) #Added
				salsa20 = __int_array_to_bytes_array(salsa20)

			#print("Z%64: ",z[0]%64)
			

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


def _allowed_file(filename):
	"""Checks if the file has an allowed extension."""

	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS