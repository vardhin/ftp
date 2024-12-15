import os
import socket
import threading

def server_mode(ip, port):
    def handle_client(conn, addr):
        print(f"Connected by {addr}")
        while True:
            command = conn.recv(1024).decode()
            if not command:
                break

            if command == "LIST":
                files = os.listdir("./server_files")
                conn.send("\n".join(files).encode())

            elif command.startswith("FETCH"):
                filename = command.split(" ")[1]
                filepath = os.path.join("./server_files", filename)

                if os.path.exists(filepath):
                    conn.send("FOUND".encode())
                    with open(filepath, "rb") as f:
                        conn.sendfile(f)
                else:
                    conn.send("NOTFOUND".encode())

        conn.close()

    # Ensure the server_files directory exists
    os.makedirs("server_files", exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen(5)
        print(f"Server listening on {ip}:{port}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

def client_mode(ip, port):
    def fetch_file(client_socket, filename):
        client_socket.send(f"FETCH {filename}".encode())
        response = client_socket.recv(1024).decode()

        if response == "FOUND":
            with open(f"./client_files/{filename}", "wb") as f:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"File {filename} downloaded successfully!")
        else:
            print(f"File {filename} not found on the server.")

    # Ensure the client_files directory exists
    os.makedirs("client_files", exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        print("Connected to the server.")

        while True:
            print("\nCommands:")
            print("1. LIST - List files on the server")
            print("2. FETCH <filename> - Download a file")
            print("3. EXIT - Disconnect")

            command = input("Enter command: ").strip()
            if command == "EXIT":
                break
            elif command == "LIST":
                s.send(command.encode())
                response = s.recv(1024).decode()
                print("Available files:\n" + response)
            elif command.startswith("FETCH"):
                _, filename = command.split(" ", 1)
                fetch_file(s, filename)
            else:
                print("Invalid command.")

if __name__ == "__main__":
    print("FTP Application")
    print("1. Server Mode")
    print("2. Client Mode")

    choice = input("Select mode (1/2): ").strip()
    ip = input("Enter IP address: ").strip()
    port = int(input("Enter port: ").strip())

    if choice == "1":
        print("Starting server...")
        server_mode(ip, port)
    elif choice == "2":
        print("Starting client...")
        client_mode(ip, port)
    else:
        print("Invalid choice.")
