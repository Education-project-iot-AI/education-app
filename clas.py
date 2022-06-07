import sys

BUF_SIZE = 1024


class Msg:
    def recv(sock):
        sys.stdout.flush()  # 버퍼 비우기
        clnt_msg = sock.recv(BUF_SIZE)  # 메세지 받아오기
        clnt_msg = clnt_msg.decode()  # 디코딩
        return clnt_msg

    def send(sock, msg):
        sys.stdin.flush()  # 버퍼 비우기
        msg = msg.encode()  # 인코딩
        sock.send(msg)  # 메세지 보내기


class user:
    def delete_imfor(sock, info):
        for i in range(0, clnt_cnt):
            if sock == info[i][0]:  # 해당 소켓 가진 클라이언트 정보 찾기
                while i < clnt_cnt - 1:  # 그 뒤에 있는 클라이언트 정보들을 한 칸씩 앞으로 당겨옴
                    info[i] = info[i + 1]
                    i += 1
                break
        clnt_cnt -= 1
        return clnt_cnt, info
