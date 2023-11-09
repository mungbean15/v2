# File with exceptions related to client


'''
Ensures correct number of arguments and port numbers are integers
Arguments:
    <argv> - array of command line arguments
'''
def c_check_arguments(argv):
    if len(argv) != 4:
        print("===== Error usage: python3 client.py server_IP server_port client_udp_server_port =====")
        exit(0)

    try:
        int(argv[2])
    except:
        print("===== Error usage: server_port is not an integer =====")
        exit(0)
    
    try:
        int(argv[3])
    except:
        print("===== Error usage: client_udp_server_port is not an integer =====")  
        exit(0)


'''
Ensure that the server_port is within the range [1024, 65535]
Arguments:
    <serverPort> - the server_port user wants to use
'''
def c_check_server_port(server_port):
    if server_port < 1024 or server_port > 65535:
        print("===== Error input: argument server_port must be a value in range [1024, 65535] =====")
        exit(0)

'''
Ensure that the client_udp_server_port is within the range [1024, 65535]
Arguments:
    <UDPPort> - the client_udp_server_port user wants to use
'''
def c_check_UDP_port(UDP_port):
    if UDP_port < 1024 or UDP_port > 65535:
        print("===== Error input: argument client_udp_server_port must be a value in range [1024, 65535] =====")
        exit(0)