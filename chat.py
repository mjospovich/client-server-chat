import socket
from random import randint
import subprocess

#* Chat client class
class ChatClient:
    #* constructor
    def __init__(self, server, port):
        #* constants
        self.SERVER = server
        self.PORT = port
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.ADDR = (self.SERVER, self.PORT)
        
        #* setting up the client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #* function for receiving messages from the server
    def receive_chat(self, ret=False):
        msg = self.client.recv(2048).decode(self.FORMAT)

        if not ret:
            if msg:
                print(msg)
        elif ret and msg:
            return msg
        
    #* function for entering credentials
    def enter_credentials_chat(self):
        ask = str(self.receive_chat(True))
        id_num = randint(1000, 9999)

        if ask == "askUSERNAME":
            username = f"CHAT {id_num}"

        self.client.send(username.encode(self.FORMAT))

    #* main chat function
    def main_chat(self):
        self.client.connect(self.ADDR)

        self.enter_credentials_chat()

        subprocess.call("sysConfig\chatConfig.bat", shell=True)
        print("LISTENING FOR MESSAGES")
        print("----------------------------------------------")

        while True:
            try:
                self.receive_chat()
            except ConnectionResetError:
                print("You lost connection to the server!")
                break
            except ConnectionAbortedError:
                print("You destroyed the connection to the server!")
                break

        print("Disconnected from server...")
        input("Press enter to exit...")
        subprocess.call("exit", shell=True)


#* Create and run the chat client
if __name__ == "__main__":
    #* setting the server and port
    SERVER = socket.gethostbyname(socket.gethostname())
    PORT = 5050

    #* creating the chat client
    chat_client = ChatClient(SERVER, PORT)
    chat_client.main_chat()
