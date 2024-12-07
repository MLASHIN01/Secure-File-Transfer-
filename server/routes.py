import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
import requests
import json


# Configuration
upload_folder = os.path.join(os.path.dirname(__file__), "uploads")

os.makedirs(upload_folder, exist_ok=True)

# Mapping of original filenames to internal filenames
filename_mapping = {}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'enc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Encrypt a file
def encrypt_file(input_file_path, output_file_path, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    with open(input_file_path, "rb") as infile, open(output_file_path, "wb") as outfile:
        outfile.write(iv)  # Write IV to the start of the file
        encryptor = cipher.encryptor()

        for chunk in iter(lambda: infile.read(1024), b""):
            padded_chunk = padder.update(chunk)
            encrypted_chunk = encryptor.update(padded_chunk)
            outfile.write(encrypted_chunk)

        # Finalize encryption
        outfile.write(encryptor.update(padder.finalize()))
        outfile.write(encryptor.finalize())

# Upload route
routes = Blueprint("routes", __name__)

def decrypt_file(input_file, output_file, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

    with open(input_file, "rb") as infile, open(output_file, "wb") as outfile:
        iv = infile.read(16)  # Read the IV from the start of the file
        decryptor = cipher.decryptor()

        for chunk in iter(lambda: infile.read(1024), b""):
            decrypted_chunk = decryptor.update(chunk)
            unpadded_chunk = unpadder.update(decrypted_chunk)
            outfile.write(unpadded_chunk)
        outfile.write(unpadder.update(decryptor.finalize()))
        outfile.write(unpadder.finalize())

@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        temp_path = os.path.join(upload_folder, f"temp_{original_filename}")
        encrypted_path = os.path.join(upload_folder, f"{original_filename}.enc")

        # Save the raw uploaded file temporarily
        file.save(temp_path)

        # Generate encryption key and IV
        key = os.urandom(32)
        iv = os.urandom(16)

        # Encrypt the file
        encrypt_file(temp_path, encrypted_path, key, iv)

        # Remove the temporary raw file
        os.remove(temp_path)

        # Update filename mapping
        filename_mapping[original_filename] = {
            "internal_filename": f"{original_filename}.enc",
            "key": key.hex(),
            "iv": iv.hex()
        }
        save_filename_mapping()  # Persist mapping to disk
        logging.info(f"Updated filename_mapping: {filename_mapping}")

        logging.info(f"File '{original_filename}' uploaded and encrypted successfully.")
        return jsonify({
            'message': 'File uploaded successfully',
            'original_filename': original_filename,
            'internal_filename': f"{original_filename}.enc",
            'key': key.hex(),
            'iv': iv.hex()
        }), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@routes.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    logging.info(f"Download request received for file: {filename}")
    logging.info(f"Uploads folder path: {upload_folder}")  # Log the upload folder path

    # Reload the filename mapping
    load_filename_mapping()
    logging.info(f"Loaded filename_mapping: {filename_mapping}")

    # Search for the internal filename in filename_mapping
    for original_filename, metadata in filename_mapping.items():
        if metadata["internal_filename"] == filename:
            file_path = os.path.join(upload_folder, metadata["internal_filename"])
            logging.info(f"Resolved file path: {file_path}")  # Log the resolved file path

            if os.path.exists(file_path):
                return send_from_directory(upload_folder, metadata["internal_filename"], as_attachment=True)
            else:
                logging.error(f"File '{metadata['internal_filename']}' not found in uploads folder.")
                return jsonify({'error': f"File '{metadata['internal_filename']}' not found in uploads folder"}), 404

    logging.error(f"File '{filename}' not found in filename mapping.")
    return jsonify({'error': f"File '{filename}' not found in filename mapping"}), 404
   
    logging.error(f"File '{filename}' not found in filename mapping.")
    return jsonify({'error': f"File '{filename}' not found in filename mapping"}), 404
    

filename_mapping_path = os.path.join(upload_folder, "filename_mapping.json")

def save_filename_mapping():
    with open(filename_mapping_path, "w") as f:
        json.dump(filename_mapping, f)

def load_filename_mapping():
    global filename_mapping
    if os.path.exists(filename_mapping_path):
        with open(filename_mapping_path, "r") as f:
            filename_mapping = json.load(f)
    else:
        filename_mapping = {}

