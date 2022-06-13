import socket
import threading
import clas

clnt_sock = []
clnt_info = []  # [sock, id, type,]
clnt_cnt = 0
PORT = 25001
BUF_SIZE = 1024
msg = ''
lock = threading.Lock()


def delete_imfor(clnt_sock):  # 클라이언트 접속해제
    global clnt_cnt
    for i in range(0, clnt_cnt):
        if clnt_sock == clnt_info[i][0]:
            print('exit client')
            while i < clnt_cnt - 1:
                clnt_info[i] = clnt_info[i + 1]
                i += 1
            break
    clnt_cnt -= 1
# 접속해제 종료


def handle_clnt(clnt_sock):
    global clnt_info, clnt_cnt
    lock.acquire()
    for i in range(0, clnt_cnt):                # clnt_info에 해당 클라이언트가 몇 번째에 있는지 추출
        if clnt_info[i][0] == clnt_sock:
            clnt_num = i
            break
    lock.release()

    while True:
        clnt_msg = clas.Msg.recv(clnt_sock)
        print(clnt_msg)
        if not clnt_msg:                        # 클라이언트 연결 끊길 시
            lock.acquire()
            delete_imfor(clnt_sock)
            lock.release()
            break

        if clnt_msg.startswith('!'):            # 특정 기능 실행 시 ! 붙여서 받음
            clnt_msg = clnt_msg.replace('!', '')
            if clnt_msg.startswith('login'):
                clnt_msg = clnt_msg.replace('login', '')
                clnt_info = clas.Join_n_login.log_in(
                    clnt_sock, clnt_msg, clnt_info, clnt_num)
                print(clnt_info)
                print(clnt_info[0][2])
            if clnt_msg.startswith('join'):
                clnt_msg = clnt_msg.replace('join', '')
                clnt_cnt = clas.Join_n_login.join(clnt_sock, clnt_cnt)

            if clnt_msg.startswith('quiz'):
                clnt_msg = clnt_msg.replace('quiz', '')
                clas.Menu.Quiz(clnt_msg, clnt_info, clnt_num)

            if clnt_msg.startswith('study'):
                clnt_msg = clnt_msg.replace('study', '')
                clas.Menu.Student_Study(clnt_msg, clnt_info, clnt_num)
            if clnt_msg.startswith('info'):
                clnt_msg = clnt_msg.replace('info', '')
                clas.Menu.Student_info(clnt_msg, clnt_info, clnt_num)
        else:
            continue


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(5)

    while True:
        clnt_sock, addr = sock.accept()

        lock.acquire()
        clnt_info.insert(clnt_cnt, [clnt_sock, '!log_in', 0])
        clnt_cnt += 1
        lock.release()

        t = threading.Thread(target=handle_clnt, args=(clnt_sock,))
        t.start()
