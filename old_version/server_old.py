# importing modules
import threading
import socket
import time

# constants
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "192.168.0.14"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
PASSWORD = "vodabaska23"

# command messages
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER_SHUTDOWN_MSG = "!SHUTDOWN"
CHAT_OPEN_MSG = "!CHAT"
ADMIN_REGISTER_MSG = "!ADMIN"
CHECK_ROLE_MSG = "!ROLE"
LIST_ALL_COMMANDS_MSG = "!COMMANDS"


# setting up the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                  1)  # added to prevent errors
server.bind(ADDR)

# server data
messages_received = []
clients_connected = []
len_clients_connected = 0

# function for appending recieved messages to list


def append_messages(msg, username):
  global messages_received

  time_msg = time.strftime("%H:%M:%S", time.localtime())

  msg_packet = f"[{time_msg} | {username}] :: {msg}"
  messages_received.append(msg_packet)

  return msg_packet


# handling clients
def handle_client(conn, addr):
  global clients_connected

  print(f"[NEW CONNECTION] {addr} connected.")

  # ask client for credentials and check if they are correct
  try:
    conn.send("askUSERNAME".encode(FORMAT))
    username = conn.recv(1024).decode(FORMAT)
    display_name = username.split("===")[0]

    if "CHAT" not in username:
      conn.send(
          f"Hey {display_name}, you are connected to server.".encode(FORMAT))
      conn.send("Type !COMMANDS to see all available commands!".encode(FORMAT))

  except:
    print("[SERVER ERROR] Failed to get username from client.")
    conn.close()

  # if client is the chat window, send it all previous messages
  if "CHAT" in username:
    for message in messages_received:
      conn.send(message.encode(FORMAT))
      time.sleep(0.1)

  # adding client to the list of connected clients
  admin = False
  clients_connected.append((conn, addr, username, admin))

  # connection established
  connected = True
  if "CHAT" not in username:
    report = f"{display_name} has connected to the server."
    for client in clients_connected:
        if "CHAT" in client[2]:
            conn_chat, addr_chat, _, _ = client
            update_chat(report, (conn_chat, addr_chat))

  # connection loop
  while connected:
    try:
      msg_length = conn.recv(HEADER).decode(FORMAT)

      # checking if the message is not empty
      if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)

        # do if msg is disconnect message
        if msg == DISCONNECT_MESSAGE:
          report = f"{display_name} has disconnected."
          print(f"[NEW DISCONNECT] {display_name} disconnected")
          clients_connected.remove((conn, addr, username, admin))

          for client in clients_connected:
            if "CHAT" in client[2]:
              conn_chat, addr_chat, _, _ = client
              update_chat(report, (conn_chat, addr_chat))

          connected = False

        # do if msg is server shutdown message
        elif msg == SERVER_SHUTDOWN_MSG:
          if admin:
            print(f"[SERVER SHUTDOWN] {display_name} has shutdown the server")
            connected = False
            shutdown()
          else:
            conn.send(
                "You are not an admin, hence you don't posses the power to do this!".encode(FORMAT))

        # do if msg is chat open message
        elif msg == CHAT_OPEN_MSG:
          print(f"[CHAT OPEN] {display_name} has opened the chat window")

        # do if msg is admin register message
        elif msg == ADMIN_REGISTER_MSG:
          conn.send("askPASSWORD".encode(FORMAT))
          password = conn.recv(1024).decode(FORMAT)

          # if password is correct, make the client an admin
          if password == PASSWORD:
            conn.send("Correct password, access gained!".encode(FORMAT))
            print(
                f"[ADMIN] Admin has registered to the server as {display_name}.")
            clients_connected.remove((conn, addr, username, admin))
            admin = True
            clients_connected.append((conn, addr, username, admin))

          # if password is incorrect, send error message
          else:
            conn.send("Wrong password!".encode(FORMAT))

        # do if msg is list all commands message
        elif msg == LIST_ALL_COMMANDS_MSG:
          conn.send(
              f"USER COMMANDS: {DISCONNECT_MESSAGE}, {CHAT_OPEN_MSG}, {CHECK_ROLE_MSG}, {LIST_ALL_COMMANDS_MSG}".encode(FORMAT))
          conn.send(
              f"ADMIN COMMANDS: {SERVER_SHUTDOWN_MSG}, {ADMIN_REGISTER_MSG}".encode(FORMAT))

        # do if msg is check role message
        elif msg == CHECK_ROLE_MSG:
          if admin:
            conn.send("You have administrator role.".encode(FORMAT))
          else:
            conn.send("You have regular user role.".encode(FORMAT))

        # do if msg is not a command
        else:
          msg_packet = append_messages(msg, display_name)
          # conn.send(msg_packet.encode(FORMAT))
          for client in clients_connected:
            if "CHAT" in client[2]:
              conn_chat, addr_chat, _, _ = client
              update_chat(msg_packet, (conn_chat, addr_chat))

    except:

      if "CHAT" in username:
        print(
            f"[CONNECTING ERROR] Chat '{username}' window has lost connection.")
        connected = False

      else:
        print(f"[CONNECTING ERROR] Connection to {addr} lost.")
        connected = False

  # closing the connection
  conn.close()


# starting the server
def start():
  global clients_connected
  global len_clients_connected

  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")

  while True:

    # checking if there are any new clients
    len_clients_connected = len(clients_connected)

    try:
      conn, addr = server.accept()
      thread = threading.Thread(target=handle_client, args=(conn, addr))
      thread.start()

      # how many clients are connected
      print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    except:
      print("[SERVER ERROR] Initializing server shutdown...")

      # if there were any clients connected, disconnect them
      if clients_connected != []:
        print("[SERVER ERROR] Closing connections to clients...")
        for client in clients_connected:
          conn, addr, _, _ = client

          conn.close()

      break

    # checking number of clients connected
    len_clients_connected = len(clients_connected)

# fumction for shutting down the server
def shutdown():
  global server
  server.close()


# function for saving the data after the server is closed
def save_data():
  global messages_recieved

  with open("Random projects\clientServer\data.txt", "a") as file:
    for msg in messages_received:
      file.write(f"{msg}\r")

# function that shows messages from all clients to other clients
def update_chat(msg, chat):
  try:
    conn, _ = chat
    conn.send(msg.encode(FORMAT))

  except WindowsError as _:
    pass


# starting the server
print(f"[STARTING] Server is starting...")
start()

print("[SERVER CLOSED] Server is closed.")

# saving the data
print("[SAVING] Saving data...")
save_data()
