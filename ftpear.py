import os
import socket
import threading
import tkinter as tk
import logging
from tkinter import filedialog, messagebox
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler

class FTPApp:
    def __init__(self, root):
        logging.basicConfig(level=logging.DEBUG)
        self.root = root
        self.root.title("FTPear - Quick FTP Server")
        self.root.geometry("400x200")
        
        self.folder_path = tk.StringVar()
        self.server = None  # Store FTP server instance
        self.ftp_thread = None  # Store thread

        # File selection
        tk.Button(root, text="Select Folder", command=self.select_folder).pack(pady=5)
        tk.Entry(root, textvariable=self.folder_path, width=50, state="readonly").pack(pady=5)

        # Start/Stop FTP
        self.ftp_button = tk.Button(root, text="Start FTP Server", command=self.toggle_ftp)
        self.ftp_button.pack(pady=10)

        # Status
        self.status_label = tk.Label(root, text="Status: Stopped", fg="red")
        self.status_label.pack(pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start_ftp(self):
        path = self.folder_path.get()
        if not path:
            messagebox.showerror("Error", "Please select a folder first!")
            return

        authorizer = DummyAuthorizer()
        authorizer.add_anonymous(path, perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer

        self.server = FTPServer(("0.0.0.0", 2121), handler)

        # Start FTP server in a thread
        self.ftp_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.ftp_thread.start()

        ip = self.get_local_ip()
        self.status_label.config(text=f"FTP running at ftp://{ip}:2121", fg="green")
        self.ftp_button.config(text="Stop FTP Server")

    def stop_ftp(self):
        if self.server:
            self.server.close_all()
            self.server = None
            self.ftp_thread = None
            self.status_label.config(text="Status: Stopped", fg="red")
            self.ftp_button.config(text="Start FTP Server")

    def toggle_ftp(self):
        if self.server:
            self.stop_ftp()
        else:
            self.start_ftp()

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPApp(root)
    root.mainloop()
