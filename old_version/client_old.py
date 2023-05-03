#importing modules
import socket
import subprocess
from random import randint

#constants
HEADER = 64
PORT = 5050 
SERVER = f"{socket.gethostbyname(socket.gethostname())}"
#SERVER = "192.168.0.14"
FORMAT = "utf-8"
ADDR = (SERVER, PORT)

#command messages
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER_SHUTDOWN_MSG = "!SHUTDOWN"
CHAT_OPEN_MSG = "!CHAT"
ADMIN_REGISTER_MSG = "!ADMIN"
CHECK_ROLE_MSG = "!ROLE"
LIST_ALL_COMMANDS_MSG = "!COMMANDS"


#function for sending messages to the server
def send(msg):
  message = msg.encode(FORMAT)
  msg_length = len(message)
  send_length = str(msg_length).encode(FORMAT)

  send_length += b" " * (HEADER - len(send_length))
  client.send(send_length)
  client.send(message)

  #receive()


#receiving messages from the server
def receive(ret = False):
  msg = client.recv(2048).decode(FORMAT)

  if not ret:
    if msg:
      print(msg)
    else:
      pass
  
  elif ret and msg:
    return msg

  else: pass

#function for entering credentials
def enter_credentials():
  ask = str(receive(True))

  if ask == "askUSERNAME":
    variable = input("Enter username[MAX 32 chars]: ") + "===" + str(randint(1000, 9999))
  
  elif ask == "askPASSWORD":
    variable = input("Enter password: ")

  #sending username to the server
  client.send(variable.encode(FORMAT))


#setting up the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
subprocess.call("sysConfig\clientConfig.bat", shell=True)
#check for receiving messages
enter_credentials()
receive()
receive()


#connection loop
while True:
  msg = input("> ")

  try:
    if msg == DISCONNECT_MESSAGE:
      send(DISCONNECT_MESSAGE)
      break
    
    #opens chat in another terminal
    elif msg == CHAT_OPEN_MSG:
      send(CHAT_OPEN_MSG)
      subprocess.call("sysConfig\openChat.bat", shell=True)

    elif msg == ADMIN_REGISTER_MSG:
      send(ADMIN_REGISTER_MSG)
      enter_credentials()
      receive()

    elif msg == CHECK_ROLE_MSG:
      send(CHECK_ROLE_MSG)
      receive()

    elif msg == LIST_ALL_COMMANDS_MSG:
      send(LIST_ALL_COMMANDS_MSG)
      receive()
      receive()

    elif msg:
      send(msg)

    else:
      pass
  
  except ConnectionResetError:
    print("You lost connection to the server!")
    break

  except ConnectionAbortedError:
    print("You destroyed the connection to the server!")
    break
    
print("Disconnected from server...")