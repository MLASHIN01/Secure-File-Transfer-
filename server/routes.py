from flask import Blueprint, request, jsonify, send_from_directory
import os
import sys
from werkzeug.utils import secure_filename
from config import upload_folder

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

# Ensure upload folder exists
os.makedirs(upload_folder, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'enc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File upload route
@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@routes.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Construct the file path
    file_path = os.path.join(upload_folder, filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Send the file to the client
        return send_from_directory(upload_folder, filename, as_attachment=True)
    else:
        # Return an error if the file is not found
        return jsonify({'error': f"File '{filename}' not found"}), 404