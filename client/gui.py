import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from sftp_client import upload_file, download_file

class SecureFileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure File Transfer")
        self.root.geometry("500x400")

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

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_file_path.set(file_path)

    def upload(self):
        file_path = self.upload_file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload.")
            return
        try:
            upload_file(file_path)
            self.log_message(f"Uploaded file: {file_path}")
        except Exception as e:
            self.log_message(f"Error during upload: {e}")

    def download(self):
        file_name = self.download_file_name.get()
        if not file_name:
            messagebox.showerror("Error", "Please enter the name of the file to download.")
            return
        try:
            download_file(file_name)
            self.log_message(f"Downloaded file: {file_name}")
        except Exception as e:
            self.log_message(f"Error during download: {e}")

    def log_message(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state="disabled")
        self.log_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureFileTransferGUI(root)
    root.mainloop()
