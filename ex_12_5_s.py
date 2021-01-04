import socket
from select import select
from queue import Queue
from typing import List

__author__ = "Nadav Shani"


#  length of the messages is formatted to 4 -> len(4   ) = 4
HEADER_LENGTH = 4
MAX_MSG_LENGTH = 1024  # the max length of a msg (1024)

# ipv4, TCP connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# all IPv4 addresses on the local machine, port 50,000
server.bind(('0.0.0.0', 50000))

# the number of unaccepted connections that the system will
# allow before refusing new connections
server.listen(5)

client_sockets = [server]  # all the client sockets

# messages queue for every client, key: client socket  value: client's queue
messages_q = dict()
run = True


def add_msg(from_soc: socket.socket, msg: str) -> None:
    """
    add messages to the queues of the other users
    Args:
        from_soc: the socket from which the message was sent
        msg: the message the user sent

    Returns:

    """
    for soc in messages_q.keys():
        if soc != from_soc:
            messages_q[soc].put(msg)


def read_data(read: List[socket.socket]) -> None:
    """
    reads data from the available sockets

    Args:
        read: list of available sockets for reading from

    Returns:

    """

    def client_disconnected() -> None:
        """
        a procedure which is called when a client disconnected
        Returns:

        """
        print("Client disconnected")
        client_sockets.remove(s)
        s.close()

    # for every readable socket
    for s in read:
        if s is server:  # if it's a server socket -> accept the new client
            connection, client_address = s.accept()

            # add the new client to the socket list
            client_sockets.append(connection)

            # add a queue for the client
            # for more reading about this module:
            # https://docs.python.org/3/library/queue.html?highlight=queue#module-queue
            messages_q[connection] = Queue()

            # add a welcome msg to the new client
            messages_q[connection].put(b'15  Server: Welcome!')
            print("new connection:", client_address)

        else:  # if the socket isn't a server socket
            try:
                # receive data from the client
                data = s.recv(MAX_MSG_LENGTH)

            except ConnectionResetError:  # the client disconnected
                client_disconnected()

            else:
                if data:  # if the data has value (not empty)
                    print("received:", data[:10])
                    add_msg(s, data)

                else:  # the client had disconnected
                    client_disconnected()


def write_data(write: List[socket.socket]) -> None:
    """
    write data to the writeable sockets
    Args:
        write: list of available sockets for writing to

    Returns: None

    """
    for s in write:
        if not messages_q[s].empty():
            #  get a msg from the client's queue and sent it to him
            next_msg = messages_q[s].get()
            s.send(next_msg)

            print("sent", next_msg[:10])


def main() -> None:
    """
    main function - gets readable, writable, exceptional sockets
    and calling functions to handle them

    Returns: None

    """
    # main loop
    while run:
        readable, writable, exceptional = select(
            client_sockets, client_sockets, [])  # get available sockets

        read_data(readable)   # read data from readable sockets
        write_data(writable)  # write data to writeable sockets


if __name__ == '__main__':
    main()
