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
        self.PASSWORD = "vodabaska23"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER_SHUTDOWN_MSG = "!SHUTDOWN"
        self.CHAT_OPEN_MSG = "!CHAT"
        self.ADMIN_REGISTER_MSG = "!ADMIN"
        self.CHECK_ROLE_MSG = "!ROLE"
        self.LIST_ALL_COMMANDS_MSG = "!COMMANDS"
        self.TIME = "!TIME"

        #*server setup
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.ADDR)

        #*server data
        self.messages_received = []
        self.clients_connected = []
        self.len_clients_connected = 0

    #*function for appending recieved messages to list
    def append_messages(self, msg, username):
        time_msg = time.strftime("%H:%M:%S", time.localtime())
        msg_packet = f"[{time_msg} | {username}] :: {msg}"
        self.messages_received.append(msg_packet)
        return msg_packet

    #*handling clients
    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        try:
            conn.send("askUSERNAME".encode(self.FORMAT))
            username = conn.recv(1024).decode(self.FORMAT)
            display_name = username.split("===")[0]

            if "CHAT" not in username:
                conn.send(f"Hey {display_name}, you are connected to server.".encode(self.FORMAT))
                conn.send("Type !COMMANDS to see all available commands!".encode(self.FORMAT))

        except:
            print("[SERVER ERROR] Failed to get username from client.")
            conn.close()

        if "CHAT" in username:
            for message in self.messages_received:
                conn.send(message.encode(self.FORMAT))
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
                        print(f"[NEW DISCONNECT] {display_name} disconnected")
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
                            conn.send("You are not an admin, hence you don't possess the power to do this!".encode(self.FORMAT))

                    elif msg == self.CHAT_OPEN_MSG:
                        print(f"[CHAT OPEN] {display_name} has opened the chat window")

                    elif msg == self.ADMIN_REGISTER_MSG:
                        conn.send("askPASSWORD".encode(self.FORMAT))
                        password = conn.recv(1024).decode(self.FORMAT)

                        if password == self.PASSWORD:
                            conn.send("Correct password, access gained!".encode(self.FORMAT))
                            print(f"[ADMIN] Admin has registered to the server as {display_name}.")
                            self.clients_connected.remove((conn, addr, username, admin))
                            admin = True
                            self.clients_connected.append((conn, addr, username, admin))
                        else:
                            conn.send("Wrong password!".encode(self.FORMAT))

                    elif msg == self.LIST_ALL_COMMANDS_MSG:
                        conn.send(f"""USER COMMANDS: {self.DISCONNECT_MESSAGE}, {self.CHAT_OPEN_MSG}, {self.CHECK_ROLE_MSG}, {self.TIME}, {self.LIST_ALL_COMMANDS_MSG}""".encode(self.FORMAT))
                        conn.send(f"ADMIN COMMANDS: {self.SERVER_SHUTDOWN_MSG}, {self.ADMIN_REGISTER_MSG}".encode(self.FORMAT))

                    elif msg == self.CHECK_ROLE_MSG:
                        if admin:
                            conn.send("You have administrator role.".encode(self.FORMAT))
                        else:
                            conn.send("You have regular user role.".encode(self.FORMAT))

                    elif msg == self.TIME:
                        time_msg = time.strftime("%H:%M:%S", time.localtime())
                        conn.send(f"[SERVER] Current time is {time_msg}".encode(self.FORMAT))
                    else:
                        msg_packet = self.append_messages(msg, display_name)
                        for client in self.clients_connected:
                            if "CHAT" in client[2]:
                                conn_chat, addr_chat, _, _ = client
                                self.update_chat(msg_packet, (conn_chat, addr_chat))

            except:
                if "CHAT" in username:
                    print(f"[CONNECTING ERROR] Chat '{username}' window has lost connection.")
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
        self.save_data()

    #*shutting down the server
    def shutdown(self):
        self.save_data()
        self.server.close()

    #*saving data to file
    def save_data(self):
        with open("clientServer\data.txt", "a") as file:
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

