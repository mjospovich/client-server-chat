import os
import socket

#* Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9999))
FORMAT = "utf-8"

#* Prepare the file to be sent
file = open("big_image.jpg", "rb")
file_size = os.path.getsize("big_image.jpg")

#* Send the file name and file size
client.send(f"test.jpg | {file_size}".encode(FORMAT))

#* Start sending the file
data = file.read(1024)
client.sendall(data)
client.send(b"<END>")

#* Close connection and file
file.close()
client.close()