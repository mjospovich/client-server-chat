from cryptography.fernet import Fernet
import threading
import socket
import time


class Server:
    def __init__(self):
        #*constants
        self.HEADER = 64
        self.PORT = 5050

        #*dynamic address
        self.SERVER = socket.gethostbyname(socket.gethostname())

        #*format
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = "utf-8"

        #*command messages
        self.PASSWORD = ""
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER_SHUTDOWN_MSG = "!SHUTDOWN"
        self.CHAT_MSG = "!CHAT"
        self.ADMIN_REGISTER_MSG = "!ADMIN"
        self.CHECK_ROLE_MSG = "!ROLE"
        self.LIST_ALL_COMMANDS_MSG = "!COMMANDS"
        self.TIME = "!TIME"
        self.ALL_CONNECTIONS = "!CONNECTIONS"
        self.SAVECHAT = "!SAVECHAT"

        #*server setup
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.ADDR)

        #*server data
        self.messages_received = []
        self.clients_connected = []
        self.len_clients_connected = 0

    #*function that gets the password from encrypted file using key
    def get_password(self):
        #get the key from key.key file
        with open("keys\key.key", "rb") as f:
            key = f.read()

        #decrypt the password from pass.key file
        with open("keys\pass.key", "rb") as f:
            data = f.read()

        fernet = Fernet(key)
        decrypted = fernet.decrypt(data)
        return decrypted.decode()


    #*function that checks if a client has a chat open (by ip address)
    def check_chat_opened(self, addr):
        for client in self.clients_connected:
            if client[1][0] == addr[0]:
                if "CHAT" in client[2]:
                    return True
                else:
                    continue
        return False

    #*function for appending recieved messages to list
    def append_messages(self, msg, username):
        time_msg = time.strftime("%H:%M:%S", time.localtime())
        msg_packet = f"[{time_msg} | {username}] :: {msg}"
        self.messages_received.append(msg_packet)
        return msg_packet

    #* function for sending message to the client
    def send_msg(self, conn, msg):
        conn.send(msg.encode(self.FORMAT))

    #*handling clients
    def handle_client(self, conn, addr):

        try:
            self.send_msg(conn, "askUSERNAME")
            username = conn.recv(1024).decode(self.FORMAT)
            display_name = username.split("===")[0]

            if "CHAT" not in username:
                print(f"[NEW CONNECTION] {addr} connected.")
                self.send_msg(conn, f"Hey {display_name}, you are connected to server.")
                self.send_msg(conn, "Type !COMMANDS to see all available commands!")

            else:
                print(f"[NEW CHAT CONNECTION] {addr} connected.")

        except:
            print("[SERVER ERROR] Failed to get username from client.")
            conn.close()

        if "CHAT" in username:
            for message in self.messages_received:
                self.send_msg(conn, message)
                time.sleep(0.1)

        admin = False
        self.clients_connected.append((conn, addr, username, admin))
        connected = True

        if "CHAT" not in username:
            report = f"{display_name} has connected to the server."
            for client in self.clients_connected:
                if "CHAT" in client[2]:
                    conn_chat, addr_chat, _, _ = client
                    self.update_chat(report, (conn_chat, addr_chat))

        while connected:
            try:
                msg_length = conn.recv(self.HEADER).decode(self.FORMAT)

                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(self.FORMAT)

                    if msg == self.DISCONNECT_MESSAGE:
                        report = f"{display_name} has disconnected."
                        print(f"[NEW DISCONNECT] {addr} disconnected")
                        self.clients_connected.remove((conn, addr, username, admin))

                        for client in self.clients_connected:
                            if "CHAT" in client[2]:
                                conn_chat, addr_chat, _, _ = client
                                self.update_chat(report, (conn_chat, addr_chat))

                        connected = False
                        print(self.check_active_connections(disconnect=True))

                    elif msg == self.SERVER_SHUTDOWN_MSG:
                        if admin:
                            print(f"[SERVER SHUTDOWN] {display_name} has shutdown the server")
                            connected = False
                            self.shutdown()
                        else:
                            self.send_msg(conn, "You are not an admin, hence you don't possess the power to do this!")

                    elif msg == self.ALL_CONNECTIONS:
                        if admin:
                            #making the report
                            connections = [f"({client[1]} {client[2]})" for client in self.clients_connected]
                            connections_report = "\n" + "\n".join(connections)
                            #sending the report
                            self.send_msg(conn, f"Currently connected clients: {connections_report}")
                        else:
                            self.send_msg(conn, "You are not an admin, hence you don't possess the power to do this!")

                    elif msg == self.CHAT_MSG:
                        #opens the chat if it's not already opened for the client (if they have the same address) else closes it
                        if not self.check_chat_opened(addr):
                            self.send_msg(conn, "openCHAT")
                            print(f"[CHAT OPEN] {display_name} has opened the chat window")
                        else:
                            self.send_msg(conn, "closeCHAT")
                            print(f"[CHAT CLOSED] {display_name} has closed the chat window")

                    elif msg == self.ADMIN_REGISTER_MSG:
                        if admin:
                            self.send_msg(conn, "isADMIN")
                        else:
                            self.send_msg(conn, "isNOTADMIN")
                            self.send_msg(conn, "askPASSWORD")
                            password = conn.recv(1024).decode(self.FORMAT)
                            self.PASSWORD = self.get_password()

                            if password == self.PASSWORD:
                                self.send_msg(conn, "Correct password, access gained!")
                                print(f"[ADMIN] Admin has registered to the server as {display_name}.")
                                self.clients_connected.remove((conn, addr, username, admin))
                                admin = True
                                self.clients_connected.append((conn, addr, username, admin))
                            else:
                                self.send_msg(conn, "Wrong password!")
                            
                            self.PASSWORD = ""

                    elif msg == self.LIST_ALL_COMMANDS_MSG:
                        self.send_msg(conn, f"USER COMMANDS: {self.DISCONNECT_MESSAGE}, {self.CHAT_MSG}, {self.CHECK_ROLE_MSG}, {self.TIME}, {self.LIST_ALL_COMMANDS_MSG}")
                        self.send_msg(conn, f"ADMIN COMMANDS: {self.SERVER_SHUTDOWN_MSG}, {self.ADMIN_REGISTER_MSG}, {self.ALL_CONNECTIONS}, {self.SAVECHAT}")
            
                    elif msg == self.CHECK_ROLE_MSG:
                        if admin:
                            self.send_msg(conn, "You have administrator role.")
                        else:
                            self.send_msg(conn, "You have regular user role.")

                    elif msg == self.TIME:
                        time_msg = time.strftime("%H:%M:%S", time.localtime())
                        self.send_msg(conn, f"[SERVER] Current time is {time_msg}")
                    
                    elif msg == self.SAVECHAT:
                        if admin:
                            self.save_data(temp=True)
                            self.send_msg(conn, "Chat data saved!")
                            print("[SAVE] Chat data saved to file!")
                        else:
                            self.send_msg(conn, "You are not an admin, hence you don't possess the power to do this!")

                    else:
                        if "!" == msg[0]:
                            self.send_msg(conn, "Unknown command!")

                        else:
                            msg_packet = self.append_messages(msg, display_name)
                            for client in self.clients_connected:
                                if "CHAT" in client[2]:
                                    conn_chat, addr_chat, _, _ = client
                                    self.update_chat(msg_packet, (conn_chat, addr_chat))

            except:
                if "CHAT" in username:
                    print(f"[CONNECTING ERROR] Chat '{username}' window has lost connection.")
                    self.clients_connected.remove((conn, addr, username, admin))
                    connected = False
                else:
                    print(f"[CONNECTING ERROR] Connection to {addr} lost.")
                    connected = False

        conn.close()

    #* checking the number of active connections
    def check_active_connections(self, disconnect=False):
        if disconnect:
            return f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}"
        return f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}"

    #*starting up the server and handling connections
    def start(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")

        while True:
            self.len_clients_connected = len(self.clients_connected)

            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                print(self.check_active_connections())
            except:
                print("[SERVER ERROR] Initializing server shutdown...")

                if self.clients_connected:
                    print("[SERVER ERROR] Closing connections to clients...")
                    for client in self.clients_connected:
                        conn, addr, _, _ = client
                        conn.close()

                break

        print("[SERVER CLOSED] Server is closed.")

    #*shutting down the server
    def shutdown(self):
        self.save_data()
        self.server.close()

    #*saving data to file
    def save_data(self, temp=False):
        if temp:
            with open(r"data\temp_data.txt", "w") as file:
                for msg in self.messages_received:
                    file.write(f"{msg}\r")
        else:
            with open(r"data\data.txt", "a") as file:
                for msg in self.messages_received:
                    file.write(f"{msg}\r")

    #*updating chat window
    def update_chat(self, msg, chat):
        try:
            conn, _ = chat
            conn.send(msg.encode(self.FORMAT))
        except WindowsError:
            pass


#* Starting the server
server = Server()
print(f"[STARTING] Server is starting...")
server.start()

