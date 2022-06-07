import sys
import socket

BUF_SIZE = 2048
IP = "127.0.0.1"
Port = 3022
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, Port))

while True:
    msg = input("입력 : ")
    sock.send(msg.encode())
    if len(msg) >= 1:
        print(msg)
