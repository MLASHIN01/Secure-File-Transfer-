import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import logging

# Set up logging
logging.basicConfig(
    filename="client.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Server URL
server_url = "https://localhost:5000"

# AES Key and IV (Initialization Vector) for encryption
AES_KEY = os.urandom(32)  # 256-bit key
AES_IV = os.urandom(16)   # 128-bit IV

# Encryption function
def encrypt_file(input_file, output_file):
    try:
        cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        with open(input_file, "rb") as infile, open(output_file, "wb") as outfile:
            outfile.write(AES_IV)  # Write IV to the beginning of the file
            encryptor = cipher.encryptor()

            for chunk in iter(lambda: infile.read(1024), b""):
                outfile.write(encryptor.update(padder.update(chunk)))
            outfile.write(encryptor.update(padder.finalize()))
            outfile.write(encryptor.finalize())
        
        logging.info(f"File '{input_file}' encrypted successfully as '{output_file}'.")
    except Exception as e:
        logging.error(f"Error encrypting file '{input_file}': {e}")
        raise

# Decryption function
def decrypt_file(input_file, output_file):
    try:
        with open(input_file, "rb") as infile, open(output_file, "wb") as outfile:
            iv = infile.read(16)  # Read IV from the beginning of the file
            cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

            decryptor = cipher.decryptor()
            for chunk in iter(lambda: infile.read(1024), b""):
                outfile.write(unpadder.update(decryptor.update(chunk)))
            outfile.write(unpadder.update(decryptor.finalize()))
            outfile.write(unpadder.finalize())
        
        logging.info(f"File '{input_file}' decrypted successfully as '{output_file}'.")
    except Exception as e:
        logging.error(f"Error decrypting file '{input_file}': {e}")
        raise

# Upload file
def upload_file(filename):
    try:
        encrypted_file = f"encrypted_{filename}"
        encrypt_file(filename, encrypted_file)
        logging.info(f"Encrypting file '{filename}' as '{encrypted_file}' for upload.")

        url = f"{server_url}/upload"
        with open(encrypted_file, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, verify=False)
        
        logging.info(f"File '{encrypted_file}' uploaded to '{url}' with response: {response.json()}.")
        print("Upload:", response.json())
    except Exception as e:
        logging.error(f"Error uploading file '{filename}': {e}")
        raise

# Download file
def download_file(filename):
    try:
        url = f"{server_url}/download/{filename}"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            encrypted_file = f"downloaded_encrypted_{filename}"
            with open(encrypted_file, "wb") as f:
                f.write(response.content)
            
            decrypted_file = f"decrypted_{filename}"
            decrypt_file(encrypted_file, decrypted_file)
            logging.info(f"File '{filename}' downloaded and decrypted as '{decrypted_file}'.")
            print(f"File downloaded and decrypted as '{decrypted_file}'.")
        else:
            logging.error(f"Failed to download file '{filename}': {response.json()}")
            print("Download:", response.json())
    except Exception as e:
        logging.error(f"Error downloading file '{filename}': {e}")
        raise

# Example usage
if __name__ == "__main__":
    upload_file("test.txt")         # Replace with the path to your test file
    download_file("test.txt")
