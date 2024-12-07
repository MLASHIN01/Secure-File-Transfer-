# server/config.py
import os

base_dir = os.path.abspath(os.path.dirname(__file__))

cert_path = os.path.join(base_dir, "cert", "cert.pem")
key_path = os.path.join(base_dir, "cert", "key.pem")
upload_folder = os.path.join(base_dir, "uploads")
max_content_length = 16 * 1024 * 1024  # 16 MB upload limit
