# File with exceptions related to server


'''
Ensures correct number of arguments and port number and number of fail attempts are integers
Arguments:
    <argv> - array of command line arguments
'''
def s_check_arguments(argv):
    if len(argv) != 3:
        print("===== Error usage: python3 server.py server_port number_of_consecutive_failed_attempts =====")
        exit(0)

    try:
        int(argv[1])
    except:
        print("===== Error input: argument server_port must be an integer =====")
        exit(0)

    try:
        int(argv[2])
    except:
        print("===== Error input: argument number_of_consecutive_failed_attempts must be an integer =====")
        exit(0)


'''
Ensure that the server_port is within the range [1024, 65535]
Arguments:
    <serverPort> - the server_port user wants to use
'''
def s_check_serverPort(serverPort):
    if serverPort < 1024 or serverPort > 65535:
        print("===== Error input: argument server_port must be a value in range [1024, 65535] =====")
        exit(0)

'''
Ensure that the number_of_consecutive_failed_attempts is within the range [1, 5]
Arguments:
    <failAttempts> - the number_of_consecutive_failed_attempts user wants to use
'''
def s_check_failAttempts(failAttempts):
    if failAttempts <= 0 or failAttempts >= 6:
        print("===== Error input: argument number_of_consecutive_failed_attempts must be a value in range [1, 5] =====")
        exit(0)