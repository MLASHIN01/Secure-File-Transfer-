import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from sftp_client import upload_file, download_file
import logging
import json
import os


class SecureFileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure File Transfer")
        self.root.geometry("500x400")

        # Metadata storage
        self.metadata_file = "file_metadata.json"
        self.file_info_mapping = self.load_metadata()

        # File Upload Section
        tk.Label(root, text="Upload File").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.upload_file_path = tk.StringVar()
        tk.Entry(root, textvariable=self.upload_file_path, width=40).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(root, text="Select File", command=self.select_file).grid(row=0, column=2, padx=10)
        tk.Button(root, text="Upload", command=self.upload).grid(row=0, column=3, padx=10)

        # File Download Section
        tk.Label(root, text="Download File").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.download_file_name = tk.StringVar()
        tk.Entry(root, textvariable=self.download_file_name, width=40).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(root, text="Download", command=self.download).grid(row=1, column=2, padx=10)

        # Logs Section
        tk.Label(root, text="Logs").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.log_area = scrolledtext.ScrolledText(root, width=60, height=15)
        self.log_area.grid(row=3, column=0, columnspan=4, padx=10, pady=10)
        self.log_area.config(state="disabled")

    def load_metadata(self):
        """Load file metadata from JSON file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def save_metadata(self):
        """Save file metadata to JSON file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.file_info_mapping, f)

    def select_file(self):
        """Select a file for upload."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_file_path.set(file_path)

    def upload(self):
        """Upload a file to the server."""
        file_path = self.upload_file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload.")
            return

        try:
            file_info = upload_file(file_path)  # Call upload_file from sftp_client.py
            if file_info:
                # Store metadata for later use
                self.file_info_mapping[file_info["original_filename"]] = file_info
                self.save_metadata()
                self.log_message(f"Uploaded file: {file_path}")
            else:
                self.log_message("File upload failed.")
        except Exception as e:
            self.log_message(f"Error during upload: {e}")

    def download(self):
        """Download a file from the server."""
        file_name = self.download_file_name.get()
        if not file_name:
            messagebox.showerror("Error", "Please enter the name of the file to download.")
            return

        try:
            file_info = self.file_info_mapping.get(file_name)
            if not file_info:
                self.log_message(f"Error: File '{file_name}' not found in metadata.")
                messagebox.showerror("Error", f"File '{file_name}' not found in uploaded records.")
                return

            # Pass file_info to download_file
            self.log_message(f"Requesting download for file: {file_info['internal_filename']}")
            download_file(file_info["internal_filename"], file_info)
            self.log_message(f"Downloaded and decrypted file: {file_name}")
        except Exception as e:
            self.log_message(f"Error during download: {e}")

    def log_message(self, message):
        """Log a message to the log area in the GUI."""
        self.log_area.config(state="normal")  # Enable editing in the log area
        self.log_area.insert(tk.END, message + "\n")  # Insert the new message
        self.log_area.config(state="disabled")  # Disable editing in the log area
        self.log_area.see(tk.END)  # Auto-scroll to the latest log entry
        logging.info(message)  # Log to the client log file as well


if __name__ == "__main__":
    root = tk.Tk()
    app = SecureFileTransferGUI(root)
    root.mainloop()
