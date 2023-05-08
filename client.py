import socket
import subprocess
from random import randint

#* Client class
class Client:
    def __init__(self, server, port):
        #* constants
        self.SERVER = server
        self.PORT = port

        #* format
        self.FORMAT = "utf-8"
        self.HEADER = 64

        #* address
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #* command messages
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER_SHUTDOWN_MSG = "!SHUTDOWN"
        self.CHAT_OPEN_MSG = "!CHAT"
        self.ADMIN_REGISTER_MSG = "!ADMIN"
        self.CHECK_ROLE_MSG = "!ROLE"
        self.LIST_ALL_COMMANDS_MSG = "!COMMANDS"
        self.TIME = "!TIME"
        self.ALL_CONNECTIONS = "!CONNECTIONS"

    #* function for sending messages to the server
    def send_message(self, message):
        msg = message.encode(self.FORMAT)
        msg_length = len(msg)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b" " * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(msg)

    #* receiving messages from the server
    def receive_message(self, ret=False):
        msg = self.client.recv(2048).decode(self.FORMAT)
        if not ret:
            if msg:
                print(msg)
            else:
                pass
        elif ret and msg:
            return msg

    #* function for entering credentials
    def enter_credentials(self):
        ask = str(self.receive_message(True))
        if ask == "askUSERNAME":
            variable = input("Enter username [MAX 32 chars]: ") + "===" + str(randint(1000, 9999))
        elif ask == "askPASSWORD":
            variable = input("Enter password: ")
        self.client.send(variable.encode(self.FORMAT))

    #* setting up the client
    def setup_client(self):
        try:
            self.client.connect(self.ADDR)
            subprocess.call("sysConfig\clientConfig.bat", shell=True)
            self.enter_credentials()
            self.receive_message()
            self.receive_message()
            return True
        
        except:
            return False
        
    #* main function for running the client
    def run(self):
        ok_check = self.setup_client()

        if not ok_check:
            print("[WRONG IP] Failed to connect to server.")
            return

        while ok_check:
            msg = input("> ")
            try:
                if msg == self.DISCONNECT_MESSAGE:
                    self.send_message(self.DISCONNECT_MESSAGE)
                    break
                elif msg == self.CHAT_OPEN_MSG:
                    self.send_message(self.CHAT_OPEN_MSG)
                    subprocess.call("sysConfig\openChat.bat", shell=True)
                elif msg == self.ADMIN_REGISTER_MSG:
                    self.send_message(self.ADMIN_REGISTER_MSG)
                    self.enter_credentials()
                    self.receive_message()
                elif msg == self.SERVER_SHUTDOWN_MSG:
                    self.send_message(self.SERVER_SHUTDOWN_MSG)
                    self.receive_message()
                elif msg == self.ALL_CONNECTIONS:
                    self.send_message(self.ALL_CONNECTIONS)
                    self.receive_message()
                elif msg == self.CHECK_ROLE_MSG:
                    self.send_message(self.CHECK_ROLE_MSG)
                    self.receive_message()
                elif msg == self.LIST_ALL_COMMANDS_MSG:
                    self.send_message(self.LIST_ALL_COMMANDS_MSG)
                    self.receive_message()
                    self.receive_message()
                elif msg == self.TIME:
                    self.send_message(self.TIME)
                    self.receive_message()
                elif msg:
                    self.send_message(msg)
                else:
                    pass
            except ConnectionResetError:
                print("You lost connection to the server!")
                break
            except ConnectionAbortedError:
                print("You destroyed the connection to the server!")
                break

        print("Disconnected from the server...")

def ask_ip():
    subprocess.call(r"sysConfig\askIP.bat", shell=True)
    ip = input("Enter the server ip: ")
    return ip

#* Create and run the chat client
if __name__ == "__main__":
    #* setting the server and port
    SERVER = ask_ip()
    PORT = 5050

    #* creating the client
    client = Client(SERVER, PORT)
    client.run()
