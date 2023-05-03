#importing modules
import socket
from random import randint
import subprocess

#constants
HEADER = 64
PORT = 5050 
SERVER = f"{socket.gethostbyname(socket.gethostname())}"
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
ADDR = (SERVER, PORT)


#receiving messages from the server
def receive_chat(ret = False):
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
def enter_credentials_chat():
  ask = str(receive_chat(True))
  id_num = randint(1000, 9999)

  if ask == "askUSERNAME":
    username = f"CHAT {id_num}"
  
  #sending username to the server
  client.send(username.encode(FORMAT))


#setting up the client
def main_chat():
  global client
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect(ADDR)

  #check for receiving messages
  enter_credentials_chat()

  #setup the chat window
  subprocess.call("sysConfig\chatConfig.bat", shell=True)
  print("LISTENING FOR MESSAGES")
  print("----------------------------------------------")
  

  #connection loop
  while True:

    try:
      receive_chat()
    
    except ConnectionResetError:
      print("You lost connection to the server!")
      break

    except ConnectionAbortedError:
      print("You destroyed the connection to the server!")
      break
      
  #close the chat window
  print("Disconnected from server...")
  input("Press enter to exit...")
  subprocess.call("exit", shell=True)


#run the chat
main_chat()