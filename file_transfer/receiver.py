import socket
import tqdm

#* Define server address and port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 9999)
FORMAT = "utf-8"

#* Bind the socket to the port
print(f"[*] Starting server on {server_address[0]}:{server_address[1]}...")
server.bind(server_address)
server.listen()

#* Accept any incoming connections
client, client_address = server.accept()
print(f"[+] {client_address} is connected.")

file_name, file_size = client.recv(1024).decode().split(" | ")
print(f"[+] File name: {file_name}")
print(f"[+] File size: {file_size}")

