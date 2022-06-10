# threading TCP CHAT server

from socket import *
from threading import *


class ChatServer:
    def __init__(self):
        self.clients = []
        self.last_rcv_msg = ''
        self.s_skt = socket(AF_INET, SOCK_STREAM)
        self.ip = ''
        self.port = 25000
        self.s_skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_skt.bind((self.ip, self.port))
        print('클라이언트 접속 대기 중...')
        self.s_skt.listen(100)
        self.accept_client()

    def accept_client(self):
        while True:
            client = c_skt, (ip, port) = self.s_skt.accept()
            if client not in self.clients:
                self.clients.append(client)
            print(f'{ip} : {str(port)}가 연결되었습니다')
            print(f'현재 연결 중 {self.clients}')
            cth = Thread(target=self.rcv_msg, args=(c_skt,))
            cth.start()

    def rcv_msg(self, c_skt):
        while True:
            try:
                inc_msg = c_skt.recv(256)
                if not inc_msg:
                    break
            except:
                continue
            else:
                self.last_rcv_msg = inc_msg.decode()
                print(f'받은 것 : {self.last_rcv_msg}')
                if self.last_rcv_msg[0] == '!':
                    cmd = self.last_rcv_msg.split('/')
                    if cmd[0] == '!idcheck':
                        if cmd[1] == '1234':
                            self.snd_client('!no')
                        else:
                            self.snd_client('!ok')
                    elif cmd[0] == '!logint':
                        if cmd[1] == '1234':
                            self.snd_client('!NO')
                        else:
                            self.snd_client('!OK')
                    elif cmd[0] == '!logins':
                        if cmd[1] == '1234':
                            self.snd_client('!NO')
                        else:
                            self.snd_client('!OK')
                else:
                    pass
        c_skt.close()

    def snd_client(self, snd_msg):
        skt, (ip, port) = self.clients[0]
        print(f'보내야 하는 것 : {snd_msg}')
        skt.send(snd_msg.encode())
        print(f'보낸 것 : {snd_msg}')


if __name__ == '__main__':
    ChatServer()
