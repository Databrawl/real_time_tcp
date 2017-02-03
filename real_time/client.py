from socket import *


if __name__ == '__main__':

    host = 'localhost'
    port = 55567
    buf = 1024

    address = (host, port)

    client_socket = socket(AF_INET, SOCK_STREAM)

    client_socket.connect(address)

    while True:
        data = input(">> ")
        data += '\n'
        if not data:
            break
        else:
            client_socket.send(bytes(data, encoding='utf8'))
            data = client_socket.recv(buf)
            if not data:
                break
            else:
                print(data)
    client_socket.close()
