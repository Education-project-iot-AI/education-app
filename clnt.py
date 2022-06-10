import sys
import threading
import socket

BUF_SIZE = 2048
IP = "127.0.0.1"
Port = 3026
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, Port))


def recv(sock):
    while True:
        a = sock.recv(BUF_SIZE)
        a = a.decode()
        if sys.getsizeof(a) >= 1:
            print(a)


t = threading.Thread(target=recv, args=(sock,))
t.start()

while True:
    msg = input("입력 : ")
    sock.send(msg.encode())
