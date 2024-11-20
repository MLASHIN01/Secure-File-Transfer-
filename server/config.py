# server/config.py
import os


cert_path = "server/cert/cert.pem"  # Path to your certificate
key_path = "server/cert/key.pem"    # Path to your private key
upload_folder = "uploads/"          # Directory to store uploaded files
max_content_length = 16 * 1024 * 1024  # 16 MB file upload limit
upload_folder = os.path.join(os.path.dirname(__file__), "uploads")  # Example path
