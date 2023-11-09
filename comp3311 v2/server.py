import atexit
import json
import signal
import sys
import threading
import time
from socket import *
from typing import Dict
from UserManager import UserManager

from s_exceptions import (s_check_arguments,
                          s_check_serverPort,
                          s_check_failAttempts)


# catch the ctrl+c exit signal
def keyboard_interrupt_handler(signal, frame):
    print("\rServer is shutdown")
    exit(0)


## CHECKS FOR IF THE EXECUTION IS EXECUTABLE ##
s_check_arguments(sys.argv)

LOCALHOST = "127.0.0.1"
serverPort = int(sys.argv[1])
failAttempts = int(sys.argv[2])

s_check_serverPort(serverPort)
s_check_failAttempts(failAttempts)


## MAKE SURE NETWORK IS EMPTY AT START UP ##
# make sure network is empty at start up
    # no logs
    # no files
    # no connected devices
uploadLog = 'upload-log.txt'
edLog = 'edge-device-log.txt'
deletionLog = 'deletion-log.txt'
with open(uploadLog, 'w') as file:
    pass
with open(edLog, 'w') as file:
    pass
with open(deletionLog, 'w') as file:
    pass


t_lock = threading.Condition()
clients = []
user_to_socket: Dict = dict()
UPDATE_INTERVAL = 1
user_manager = UserManager()


def on_close():
    serverSocket.close()


def connection_handler(connection_socket, client_address):
    def real_connection_handler():
        while True:
            data = connection_socket.recv(1024)
            if not data:
                exit(0)

            data = data.decode()
            data = json.loads(data)
            action = data['action']

            with t_lock:
                print(client_address, ":", data)

                # the data to reply to client
                server_message = dict()
                server_message['action'] = action

                if action == 'login':
                    username = data['username']
                    password = data['password']
                    clients.append(client_address)
                    #auth the user and reply the status
                    status = user_manager.authenticate(username, password)
                    server_message['status'] = status
                    if status == 'SUCCESS':
                        user_manager.set_private_port(username, int(data['port']))
                # enter other commands and what they do
                else:
                    server_message['reply'] = 'Unkown action.'
                connection_socket.send(json.dumps(server_message).encode())
                t_lock.notify()
    
    return real_connection_handler


def recv_handler():
    global t_lock
    global clients
    global serverSocket
    print('Server is up.')
    while True:
        # create a new connection for a new client
        connection_socket, client_address = serverSocket.accept()
        # create a new function handler for the client
        socket_handler = connection_handler(connection_socket, client_address)
        # create a new thread for the client socket
        socket_thread = threading.Thread(name=str(client_address), target=socket_handler)
        socket_thread.daemon = False
        socket_thread.start()


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((LOCALHOST, serverPort))
serverSocket.listen(1)

recv_thread = threading.Thread(name="RevcHandler", target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

signal.signal(signal.SIGINT, keyboard_interrupt_handler)

atexit.register(on_close)

# while True:
#     time.sleep(0.1)
#     user_manager.update()


################################################################################
#                             old multithread code                             #
################################################################################
'''
## NOW SERVER STARTS ##
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((LOCALHOST, serverPort))

    # Multi-thread class for client
    # Code from example provided on webcms3

class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False

        print("===== New connection created for: ", clientAddress, " =====")
        self.clientAlive = True

    def run(self):
        message = ''

        while self.clientAlive:
            # use recv() to receive message from the client
            # NOTE: YOU MAY HAVE TO CHANGE 1024
            data = self.clientSocket.recv(1024)
            message = data.decode()

            # if the message from client is empty, the client would be off-line then set the client as offline (alive=False)
            if message == '':
                self.clientAlive = False
                print("===== The user disconnected - ", clientAddress, " =====")
                break

            # handle message from the client
            # NOTE: the below has to be changed
            if message == 'login':
                print("[recv] New login request")
                self.process_login()
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())

    """
        NOTE: CHANGE?
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self):
        message = 'user credentials request'
        print('[send] ' + message);
        self.clientSocket.send(message.encode())

print("===== Server is running =====")
print("===== Waiting for connection request from clients... =====")

while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    ClientThread = ClientThread(clientAddress, clientSockt)
    ClientThread.start()

# do you need to close?
'''