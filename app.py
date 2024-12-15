from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# Ensure the client_files directory exists
os.makedirs("client_files", exist_ok=True)

# Client mode functions
def list_files(ftp):
    try:
        print("[INFO] Listing files on the server:")
        files = ftp.nlst()
        if not files:
            print("[INFO] No files found on the server.")
        else:
            for file in files:
                print(file)
    except Exception as e:
        print(f"[ERROR] Failed to list files: {e}")

def download_file(ftp, filename):
    local_filename = os.path.join("client_files", filename)
    try:
        with open(local_filename, "wb") as f:
            ftp.retrbinary(f"RETR {filename}", f.write)
        print(f"[SUCCESS] File '{filename}' downloaded successfully to '{local_filename}'.")
    except FileNotFoundError:
        print(f"[ERROR] Directory 'client_files' does not exist.")
    except Exception as e:
        print(f"[ERROR] Failed to download file '{filename}': {e}")

def upload_file(ftp, filepath):
    try:
        if not os.path.isfile(filepath):
            print(f"[ERROR] File '{filepath}' does not exist.")
            return
        
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            ftp.storbinary(f"STOR {filename}", f)
        print(f"[SUCCESS] File '{filepath}' uploaded successfully as '{filename}'.")
    except Exception as e:
        print(f"[ERROR] Failed to upload file '{filepath}': {e}")

def client_mode():
    server = input("Enter FTP server address: ").strip()
    username = input("Enter username (or leave blank for anonymous): ").strip()
    password = input("Enter password (or leave blank for anonymous): ").strip()

    try:
        with FTP(server) as ftp:
            ftp.login(user=username or "anonymous", passwd=password or "")
            print(f"[INFO] Connected to FTP server: {server}")

            while True:
                print("\nCommands:")
                print("1. LIST - List files on the server")
                print("2. DOWNLOAD <filename> - Download a file")
                print("3. UPLOAD <filepath> - Upload a file")
                print("4. EXIT - Disconnect")

                command = input("Enter command: ").strip()
                if command.upper() == "EXIT":
                    print("[INFO] Disconnecting from the server.")
                    break
                elif command.upper() == "LIST":
                    list_files(ftp)
                elif command.upper().startswith("DOWNLOAD"):
                    parts = command.split(" ", 1)
                    if len(parts) < 2:
                        print("[ERROR] Please specify the filename to download.")
                    else:
                        download_file(ftp, parts[1])
                elif command.upper().startswith("UPLOAD"):
                    parts = command.split(" ", 1)
                    if len(parts) < 2:
                        print("[ERROR] Please specify the file path to upload.")
                    else:
                        upload_file(ftp, parts[1])
                else:
                    print("[ERROR] Invalid command.")
    except Exception as e:
        print(f"[ERROR] Unable to connect to FTP server: {e}")

# Server mode implementation
def server_mode():
    try:
        authorizer = DummyAuthorizer()
        authorizer.add_user("user", "12345", os.getcwd(), perm="elradfmw")  # Change username and password as needed
        authorizer.add_anonymous(os.getcwd(), perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer

        server = FTPServer(("0.0.0.0", 2121), handler)
        print("[INFO] FTP Server started on port 2121")
        print("[INFO] User: user, Password: 12345")
        print("[INFO] Press Ctrl+C to stop the server.")

        server.serve_forever()
    except Exception as e:
        print(f"[ERROR] Failed to start FTP server: {e}")

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Client Mode")
        print("2. Server Mode")
        print("3. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            client_mode()
        elif choice == "2":
            server_mode()
        elif choice == "3":
            print("[INFO] Exiting application.")
            break
        else:
            print("[ERROR] Invalid selection. Please choose a valid option.")

if __name__ == "__main__":
    main_menu()
