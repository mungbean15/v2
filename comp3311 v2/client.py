import atexit
import json
import readline
import signal
import sys
import threading
import time
from socket import *
from typing import Dict

from c_exceptions import (c_check_arguments,
                          c_check_server_port,
                          c_check_UDP_port)


# captures ctrl+c exit keyboard signal
def keyboard_interrupt_handler(signal, frame):
    print("\rClient has left")
    exit(0)


## CHECK ARGUMENTS WHEN EXECUTING ##
c_check_arguments(sys.argv)

# storing values of arguments into variables
server_IP = sys.argv[1]
server_port = int(sys.argv[2])
UDP_port = int(sys.argv[3])

c_check_server_port(server_port)
c_check_UDP_port(UDP_port)


## SET UP VALUES FOR RUNNING OF SERVER ##
# communicates to server every second
UPDATE_INTERVAL = 1

# will exit main thread when set to True
to_exit = False


## NOW CONNECT CLIENT TO SERVER ##
# connect to server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((server_IP, server_port))

# get thread
t_lock = threading.Condition()

# map username to private TCP socket
priv_TCP_socket_map: Dict = dict()

# connect private socket
priv_recv_socket = socket(AF_INET, SOCK_STREAM)
priv_recv_socket.bind(('localhost', 0))
priv_recv_socket.listen(1)
priv_recv_port = priv_recv_socket.getsockname()[1]


## AUTHENTICATION ##
username = input("Username: ")
# username may be overwritten
# USERNAME = username
message = json.dumps({
    'command': 'login',
    'username': username,
    'password': input("Password: "),
    'port': priv_recv_port,
})


# logout handler
def logout():
    print("You are logged out.")
    clientSocket.send(json.dumps({
        'action': 'out'
    }).encode())
    clientSocket.close()


# NOTE: DOUBLE CHECK THIS IDK WHAT THIS DOES
# print without breaking input thread
# https://stackoverflow.com/a/4653306/12208789 resolve line buffer issue
def safe_print(*args):
    sys.stdout.write('\r' + ' ' * (len(readline.get_line_buffer()) + 2) + '\r')
    print(*args)
    sys.stdout.write('> ' + readline.get_line_buffer())
    sys.stdout.flush()


# return function as connection handler for specific socket for multi-threading
def priv_connection_handler(connection_socket):
    def real_connection_handler():
        while True:
            data = connection_socket.recv(1024)
            # if data is empty
            if not data:
                # socket is closed
                safe_print('Private connection stopped.')
                exit(0)
            
            # when data is received from the client
            data = data.decode()
            data - json.loads(data)
            from_user = data['from']
            message = data['message']

            safe_print('[PRIVATE]', from_user, ':', message)
    
    return real_connection_handler


# handles all incoming data and replies to those
def priv_recv_handler():
    while True:
        # create new connection for client
        connection_socket, client_address = priv_recv_socket.accept()
        safe_print('Private connection started.')

        # create new function handler for the client
        priv_socket_handler = priv_connection_handler(connection_socket, client_address)

        # create new thread for client socket
        priv_socket_thread = threading.Thread(name=str(client_address), target=priv_socket_handler)
        priv_socket_thread.daemon = False
        priv_socket_thread.start()


def priv_connect(address: str, port: int, username: str):
    # connect with address directly
    new_priv_socket = socket(AF_INET, SOCK_STREAM)
    new_priv_socket.connect((address, port))
    priv_TCP_socket_map[username] = new_priv_socket
    safe_print('Private connection connected.')


def priv_disconnect(username: str):
    # disconnect user
    if username in priv_TCP_socket_map and priv_TCP_socket_map[username]:
        priv_TCP_socket_map[username].close()
        safe_print('Closed.')
    else:
        safe_print('Not connected.')


# incoming data and its respective diplay to user
def recv_handler():
    '''
    global to_exit
    while True:
        login_result = clientSocket.recv(1024)
        data = json.loads(login_result.decode())
    '''


# outgoing data
def send_handler():
    global to_exit
    while True:
        commandPromt = "Please enter one of the following commands:\n\tAED - list active edge devices\n\tDTE - delete data file from server\n\tEDG - generate edge data\n\tOUT - exit network\n\tSCS - use server computation service\n\tUED - upload edge data to server\n\tUVF - send video file to edge device"
        command = input(commandPromt).strip()
        if command.startswith('OUT'):
            to_exit = True
        # NOTE: ENTER REST OF COMMANDS HERE


# start the interactions between client and server
def interact():
    global priv_recv_socket
    revc_thread = threading.Thread(name="RecvHandler", target=recv_handler)
    revc_thread.daemon = True
    revc_thread.start()

    send_thread = threading.Thread(name="SendHandler", target=send_handler)
    send_thread.daemon = True
    send_thread.start()

    revc_thread = threading.Thread(name="PrivateRecvHandler", target=priv_recv_handler)
    revc_thread.daemon = True
    revc_thread.start()

    while True:
        time.sleep(0.1)

        if to_exit:
            exit(0)
    

# start interaction after successful authentication
def log_in():
    global message
    clientSocket.send(message.encode())

    # wait for reply from server
    login_result = clientSocket.recv(1024)
    login_result = json.loads(login_result.decode())

    if login_result['command'] == 'login' and login_result['status'] == 'SUCCESS':
        print('You are logged in.')
        atexit.register(logout)
        interact()
    elif login_result['command'] == 'login' and login_result['status'] == 'INVALID_PASSWORD_BLOCKED':
        print()
    elif login_result['command'] == 'login' and login_result['status'] == 'BLOCKED':
        print()
    elif login_result['command'] == 'login' and login_result['status'] == 'INVALID_PASSWORD':
        message = json.dumps({
            'command': 'login',
            'username': username,
            'password': input("Invalid password. Please try again."),
            'port': priv_recv_port
        })
        log_in()
    elif login_result['command'] == 'login' and login_result['status'] == 'ALREADY_LOGGED_IN':
        print()
    elif login_result['command'] == 'login' and login_result['status'] == 'USERNAME_DOES_NOT_EXIST':
        print()
    else:
        print("FATAL: unexpected message")
        exit(1)

signal.signal(signal.SIGINT, keyboard_interrupt_handler)

if __name__ == "__main__":
    log_in()








################################################################################
#                             old multithread code                             #
################################################################################
# while True:
    # commandPromt = "Please enter one of the following commands:\n\tAED - list active edge devices\n\tDTE - delete data file from server\n\tEDG - generate edge data\n\tOUT - exit network\n\tSCS - use server computation service\n\tUED - upload edge data to server\n\tUVF - send video file to edge device"
    # message = input(commandPromt)
    # clientSocket.sendall(message.encode())

    # # receive response from server
    # # NOTE: YOU CAN CHANGE 1024 (maybe to 2048?)
    # data = clientSocket.recv(1024)
    # receivedMessage = data.decode()

    # # parse the message received from server and take corresponding actions
    # if receivedMessage == "":
    #     print("[recv] Message from server is empty!")
    # elif receivedMessage == "user credentials request":
    #     print("[recv] You need to provide username and password to login")
    # elif receivedMessage == "download filename":
    #     print("[recv] You need to provide the file name you want to download")
    # else:
    #     print("[recv] Message makes no sense")
        
    # ans = input('\nDo you want to continue(y/n) :')
    # if ans == 'y':
    #     continue
    # else:
    #     break

# close socket
# clientSocket.close()