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
        self.server_logs = []

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
    
    #* function for printing server messages and appends them to the list
    def server_log(self, tag, msg):
        message = f"[{tag.upper()}] {msg}"
        print(message)
        self.server_logs.append(message)


    #*handling clients
    def handle_client(self, conn, addr):

        #* setting aliases for functions
        send_msg = self.send_msg
        server_log = self.server_log

        #* setting common response messages
        not_admin_msg = "You are not an admin, hence you don't possess the power to do this!"

        try:
            send_msg(conn, "askUSERNAME")
            username = conn.recv(1024).decode(self.FORMAT)
            display_name = username.split("===")[0]

            if "CHAT" not in username:
                server_log("new connection", f"{addr} has connected to the server.")
                send_msg(conn, f"Hey {display_name}, you are connected to server.")
                send_msg(conn, "Type !COMMANDS to see all available commands!")

            else:
                server_log("new chat connection", f"{addr} has connected to the server.")

        except:
            server_log("server error", f"Failed to get username from client.")
            conn.close()

        if "CHAT" in username:
            for message in self.messages_received:
                send_msg(conn, message)
                time.sleep(0.15)

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
                        server_log("new disconnect", f"{addr} disconnected")
                        self.clients_connected.remove((conn, addr, username, admin))

                        for client in self.clients_connected:
                            if "CHAT" in client[2]:
                                conn_chat, addr_chat, _, _ = client
                                self.update_chat(report, (conn_chat, addr_chat))

                        connected = False
                        print(self.check_active_connections(disconnect=True))

                    elif msg == self.SERVER_SHUTDOWN_MSG:
                        if admin:
                            server_log("server shutdown", f"{display_name} has shutdown the server")
                            connected = False
                            self.shutdown()
                        else:
                            send_msg(conn, not_admin_msg)

                    elif msg == self.ALL_CONNECTIONS:
                        if admin:
                            #making the report
                            connections = [f"({client[1]} {client[2]})" for client in self.clients_connected]
                            connections_report = "\n" + "\n".join(connections)
                            #sending the report
                            send_msg(conn, f"Currently connected clients: {connections_report}")
                        else:
                            send_msg(conn, not_admin_msg)

                    elif msg == self.CHAT_MSG:
                        #opens the chat if it's not already opened for the client (if they have the same address) else closes it
                        if not self.check_chat_opened(addr):
                            self.send_msg(conn, "openCHAT")
                            server_log("chat open", f"{display_name} has opened the chat window")
                        else:
                            self.send_msg(conn, "closeCHAT")
                            server_log("chat closed", f"{display_name} has closed the chat window")

                    elif msg == self.ADMIN_REGISTER_MSG:
                        if admin:
                            send_msg(conn, "isADMIN")
                        else:
                            send_msg(conn, "isNOTADMIN")
                            send_msg(conn, "askPASSWORD")
                            password = conn.recv(1024).decode(self.FORMAT)
                            self.PASSWORD = self.get_password()

                            if password == self.PASSWORD:
                                send_msg(conn, "Correct password, access gained!")
                                server_log("admin register", f"{display_name} has registered as admin.")
                                self.clients_connected.remove((conn, addr, username, admin))
                                admin = True
                                self.clients_connected.append((conn, addr, username, admin))
                            else:
                                send_msg(conn, "Wrong password!")
                            
                            self.PASSWORD = ""

                    elif msg == self.LIST_ALL_COMMANDS_MSG:
                        send_msg(conn, f"USER COMMANDS: {self.DISCONNECT_MESSAGE}, {self.CHAT_MSG}, {self.CHECK_ROLE_MSG}, {self.TIME}, {self.LIST_ALL_COMMANDS_MSG}")
                        send_msg(conn, f"ADMIN COMMANDS: {self.SERVER_SHUTDOWN_MSG}, {self.ADMIN_REGISTER_MSG}, {self.ALL_CONNECTIONS}, {self.SAVECHAT}")
            
                    elif msg == self.CHECK_ROLE_MSG:
                        if admin:
                            send_msg(conn, "You have administrator role.")
                        else:
                            send_msg(conn, "You have regular user role.")

                    elif msg == self.TIME:
                        time_msg = time.strftime("%H:%M:%S", time.localtime())
                        send_msg(conn, f"[SERVER] Current time is {time_msg}")
                    
                    elif msg == self.SAVECHAT:
                        if admin:
                            self.save_data(temp=True)
                            send_msg(conn, "Chat data saved!")
                            server_log("save", f"{display_name} has saved the chat data to file.")
                        else:
                            send_msg(conn, "You are not an admin, hence you don't possess the power to do this!")

                    else:
                        if "!" == msg[0]:
                            send_msg(conn, "Unknown command!")

                        else:
                            msg_packet = self.append_messages(msg, display_name)
                            for client in self.clients_connected:
                                if "CHAT" in client[2]:
                                    conn_chat, addr_chat, _, _ = client
                                    self.update_chat(msg_packet, (conn_chat, addr_chat))

            except:
                if "CHAT" in username:
                    server_log("connecting error", f"Chat '{username}' has been closed.")
                    self.clients_connected.remove((conn, addr, username, admin))
                    connected = False
                else:
                    server_log("connecting error", f"{addr} has lost connection.")
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
        self.server_log("listening", f"Server is listening on {self.SERVER}")

        while True:
            self.len_clients_connected = len(self.clients_connected)

            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                print(self.check_active_connections())
            except:
                self.server_log("server shutdown", "Initializing server shutdown...")

                if self.clients_connected:
                    self.server_log("server shutdown", "Closing connections to clients...")
                    for client in self.clients_connected:
                        conn, addr, _, _ = client
                        conn.close()

                break

        self.server_log("server closed", "Server has been closed.")

    #*shutting down the server
    def shutdown(self):
        self.save_data()
        self.save_logs()
        self.server.close()

    #*saving data to file
    def save_data(self, temp=False):
        if temp:
            file_name = time.strftime("%d-%m-%Y_%H-%M", time.localtime()) + ".txt"
            with open(rf"data\{file_name}.txt", "w") as file:
                for msg in self.messages_received:
                    file.write(f"{msg}\r")
        else:
            with open(r"data\data.txt", "a") as file:
                for msg in self.messages_received:
                    file.write(f"{msg}\r")

    #*save server logs to file
    def save_logs(self):
        with open(r"data\logs.log", "a") as file:
            file.write(f"-----------{time.strftime('%d-%m-%Y_%H-%M', time.localtime())}-----------\r")
            for log in self.server_logs:
                file.write(f"{log}\r")


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

