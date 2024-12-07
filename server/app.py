from flask import Flask, request
from routes import routes
import logging
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.routes import routes  # Correct import
from server.config import cert_path, key_path, max_content_length

# Initialize the Flask app
app = Flask(__name__)

# Register Blueprint
app.register_blueprint(routes)

# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(__file__), "logs")  # Relative to the server directory
os.makedirs(log_dir, exist_ok=True)

# Set up logging
log_file = os.path.join(log_dir, "server.log")
logging.basicConfig(
    filename=log_file,  # Store logs in logs/server.log
    level=logging.INFO,  # Logging level
    format="%(asctime)s - %(message)s"  # Log message format
)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.url}")

if __name__ == "__main__":
    # Print Python Path for debugging
    print("Python Path:", sys.path)

    # Run the Flask server with HTTPS enabled
app.run(host="0.0.0.0", port=5000, ssl_context=("server/cert/cert.pem", "server/cert/key.pem"))