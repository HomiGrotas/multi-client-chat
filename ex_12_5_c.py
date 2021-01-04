import socket
from threading import Thread


__author__ = "Nadav Shani"


IP = '127.0.0.1'  # local machine ip
PORT = 50000      # server's port

# the max length of a msg (1020, 1020 + header_length = 1024)
MAX_MSG_LENGTH = 1020

#  length of the messages is formatted to 4 -> len(4   ) = 4
HEADER_LENGTH = 4
run = True

name = input("Enter your name: ")  # the client's name

# ipv4, TCP connection
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server by it's ip on port 50000
my_socket.connect((IP, PORT))


def send() -> None:
    """
    send data to the server
    Returns: None

    """
    global run

    while run:
        data = name + ": " + input()

        # send buffered data (1024 per chunk)
        while data:
            # msg length is formatted to 4, length of msg is formatted to 1024
            to_send = '{:<{}}'.format(len(data), HEADER_LENGTH) +\
                      '{:<{}}'.format(data, MAX_MSG_LENGTH)

            # msg example: '2   hi'

            # send the byte-code data (1024 per chunk)
            try:
                my_socket.send(to_send[:HEADER_LENGTH + MAX_MSG_LENGTH]
                               .encode())

            # if the server is down now
            except ConnectionResetError:
                run = False
                data = ''  # there is no need to send anymore data

            else:
                data = data[MAX_MSG_LENGTH:]  # move to next chunk


def receive() -> None:
    """
    receive data from server
    Returns: None

    """
    global run

    # while the app is still running -> receive data (1024) and print it
    while run:
        try:
            data = my_socket.recv(MAX_MSG_LENGTH + HEADER_LENGTH)\
                .decode()[HEADER_LENGTH:]

        # if the server is down now
        except ConnectionResetError:
            run = False
            data = "Client disconnected"

        # remove unnecessary spaces (due to the formatting)
        print("\n" + data.strip())


def main() -> None:
    """
    main function - starts threads for writing and receiving
    Returns: None

    """

    # loop until user requested to exit
    send_t = Thread(target=send)
    receive_t = Thread(target=receive)

    # start the threads
    send_t.start()
    receive_t.start()

    # add thread to main thread
    send_t.join()
    receive_t.join()


if __name__ == '__main__':
    main()
