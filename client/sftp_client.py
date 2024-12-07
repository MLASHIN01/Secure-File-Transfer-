import os
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
server_url = "https://localhost:5000"
logging.basicConfig(filename="client.log", level=logging.INFO, format="%(asctime)s - %(message)s")


# Decrypt a file
def decrypt_file(input_file, output_file, key_hex, iv_hex):
    """Decrypts an encrypted file using the provided key and IV."""
    key = bytes.fromhex(key_hex)  # Convert key from hex to bytes
    iv = bytes.fromhex(iv_hex)    # Convert IV from hex to bytes
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

    with open(input_file, "rb") as infile, open(output_file, "wb") as outfile:
        decryptor = cipher.decryptor()

        for chunk in iter(lambda: infile.read(1024), b""):
            decrypted_chunk = decryptor.update(chunk)
            unpadded_chunk = unpadder.update(decrypted_chunk)
            outfile.write(unpadded_chunk)

        outfile.write(unpadder.update(decryptor.finalize()))
        outfile.write(unpadder.finalize())


# Upload a file
def upload_file(filename):
    try:
        url = f"{server_url}/upload"
        with open(filename, "rb") as f:
            response = requests.post(url, files={"file": f}, verify="server/cert/cert.pem")
            response_data = response.json()

        if response.status_code == 200:
            logging.info(f"File uploaded successfully: {response_data}")
            return response_data
        else:
            logging.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        raise


# Download a file
def download_file(filename, file_info):
    try:
        url = f"{server_url}/download/{filename}"
        logging.info(f"Requesting download for file: {filename} from {url}")
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            # Save the downloaded encrypted file temporarily
            encrypted_file = os.path.join(os.path.expanduser("~"), f"encrypted_{filename}")
            with open(encrypted_file, "wb") as f:
                f.write(response.content)

            logging.info(f"Encrypted file saved temporarily at: {encrypted_file}")

            # Decrypt the file
            decrypted_file = os.path.join(os.path.expanduser("~"), "Desktop", filename.replace(".enc", ""))
            decrypt_file(encrypted_file, decrypted_file, file_info["key"], file_info["iv"])

            # Clean up the temporary encrypted file
            os.remove(encrypted_file)
            logging.info(f"File downloaded and decrypted successfully: {decrypted_file}")
        else:
            logging.error(f"Download failed: {response.status_code} - {response.text}")
            raise Exception(f"Download failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during file download: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during file download: {e}")
        raise


if __name__ == "__main__":
    original_filename = "C:/Users/Marwan/Desktop/TEST FILE.TXT"

    try:
        # Upload the file and get metadata
        file_info = upload_file(original_filename)
        if file_info:
            try:
                # Pass both filename and metadata to download_file
                download_file(file_info["original_filename"], file_info)
            except Exception as e:
                logging.error(f"Error during download: {e}")
                print("An error occurred during the download process.")
        else:
            logging.error("File upload failed. Cannot proceed to download.")
            print("File upload failed. Please check the logs for more details.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print("An unexpected error occurred. Please check the logs.")
