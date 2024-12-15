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

# Server mode implementation
def server_mode():
    ip_address = input("Enter IP address to bind the server: ").strip()
    port = int(input("Enter port to bind the server: ").strip())
    try:
        authorizer = DummyAuthorizer()
        authorizer.add_user("user", "12345", os.getcwd(), perm="elradfmw")
        authorizer.add_anonymous(os.getcwd(), perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer

        server = FTPServer((ip_address, port), handler)
        print("\n" + "="*50)
        print("SERVER STARTED SUCCESSFULLY!")
        print("="*50)
        print("\nConnection Details for Clients:")
        print(f"Server IP: {ip_address}")
        print(f"Port: {port}")
        print("\nAuthentication Option 1 (User Login):")
        print("Username: user")
        print("Password: 12345")
        print("\nAuthentication Option 2 (Anonymous):")
        print("Username: (leave blank)")
        print("Password: (leave blank)")
        print("\nTo connect from another computer:")
        print(f"1. Run this program in Client Mode")
        print(f"2. Enter server address: {ip_address}")
        print(f"3. Enter server port: {port}")
        print(f"4. Choose either user credentials or anonymous login")
        print("\n" + "="*50)
        print("Press Ctrl+C to stop the server.")
        print("="*50 + "\n")

        server.serve_forever()
    except Exception as e:
        print(f"[ERROR] Failed to start FTP server: {e}")

def client_mode():
    print("\n" + "="*50)
    print("FTP CLIENT CONNECTION")
    print("="*50)
    print("\nTo connect to the server, you need:")
    print("1. The server's IP address")
    print("2. The server's port number")
    print("3. Optional: username and password (or use anonymous login)")
    print("="*50 + "\n")

    server = input("Enter FTP server address: ").strip()
    port = int(input("Enter FTP server port: ").strip())
    print("\nFor anonymous login, leave the following blank:")
    username = input("Enter username (or leave blank for anonymous): ").strip()
    password = input("Enter password (or leave blank for anonymous): ").strip()

    # Rest of the client_mode function remains the same
    try:
        with FTP() as ftp:
            ftp.connect(server, port)
            ftp.login(user=username or "anonymous", passwd=password or "")
            print(f"[SUCCESS] Connected to FTP server: {server}:{port}")
            
            while True:
                print("\nAvailable Commands:")
                print("1. LIST - List files on the server")
                print("2. DOWNLOAD <filename> - Download a file")
                print("3. UPLOAD <filepath> - Upload a file")
                print("4. EXIT - Disconnect")

                command = input("Enter command: ").strip().upper()
                if command == "EXIT":
                    print("[INFO] Disconnecting from the server.")
                    break
                elif command == "LIST":
                    list_files(ftp)
                elif command.startswith("DOWNLOAD"):
                    parts = command.split(" ", 1)
                    if len(parts) < 2:
                        print("[ERROR] Please specify the filename to download.")
                    else:
                        download_file(ftp, parts[1])
                elif command.startswith("UPLOAD"):
                    parts = command.split(" ", 1)
                    if len(parts) < 2:
                        print("[ERROR] Please specify the file path to upload.")
                    else:
                        upload_file(ftp, parts[1])
                else:
                    print("[ERROR] Invalid command.")
    except Exception as e:
        print(f"[ERROR] Unable to connect to FTP server: {e}")

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