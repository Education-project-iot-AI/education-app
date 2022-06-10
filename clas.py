import sys
import sqlite3
import threading

BUF_SIZE = 1024

lock = threading.Lock()


def dbcon():
    con = sqlite3.connect('edu.db')  # DB 연결
    c = con.cursor()                  # 커서
    return (con, c)


class Msg:
    def recv(sock):  # 메세지 받기 시작
        sys.stdout.flush()  # 버퍼 비우기
        clnt_msg = sock.recv(BUF_SIZE)  # 메세지 받아오기
        clnt_msg = clnt_msg.decode()  # 디코딩
        return clnt_msg
# 메세지 받기 종료

    def send(sock, msg):  # 메세지 보내기 시작
        sys.stdin.flush()  # 버퍼 비우기
        msg = msg.encode()  # 인코딩
        sock.send(msg)
# 메세지 보내기 종료


class Join_n_login:  # 회원가입, 로그인 시작
    def join(sock, clnt_cnt):  # 회원가입 시작
        con, c = dbcon()
        user_data = []
        while True:
            ck_login = 0
            imfor = sock.recv(BUF_SIZE)
            imfor = imfor.decode()

            if imfor == "!Q_join":      # 회원가입 창 닫을 때 함수 종료
                con.close()
                break

            if '!idcheck/' in imfor:  # 아이디 중복확인
                lock.acquire()
                imfor = imfor.replace('!idcheck/', '')
                c.execute(
                    "SELECT DISTINCT teacher.ID, student.ID From teacher LEFT JOIN student ON teacher.ID != student.ID")
                for row in c:  # id 컬럼
                    if imfor in row:       # 클라이언트가 입력한 id가 DB에 있으면
                        sock.send('!no'.encode())
                        ck_login = 1
                        break
                if ck_login == 1:
                    continue
                lock.release()
                sock.send('!ok'.encode())  # 중복된 id 없으면 !OK 전송
            # 중복확인 종료

            if imfor.startswith('!joindata/'):
                lock.acquire()
                imfor = imfor.replace('!joindata/', '')
                imfor = imfor.split('/')  # 구분자 /로 잘라서 리스트 생성

                print(imfor)

                for i in range(3):
                    user_data.append(imfor[i])       # user_data 리스트에 추가

                print(user_data)

                if 's' in imfor[3]:
                    query = "INSERT INTO student(ID, PW, name) VALUES(?, ?, ?)"
                else:
                    query = "INSERT INTO teacher(ID, PW, name) VALUES(?, ?, ?)"
                c.executemany(query, (user_data,))  # DB에 user_data 추가
                con.commit()            # DB에 커밋
                clnt_cnt += 1

                con.close()
                lock.release()
                return clnt_cnt
# 화원가입 종료

    def log_in(sock, data, clnt_info, n):  # 로그인 시작
        con, c = dbcon()
        print(data)
        data = data.split('/')
        user_id = data[1]

        if 's' in data[0]:
            c.execute("SELECT PW FROM student WHERE ID=?",
                      (user_id,))  # DB에서 id 같은 password 컬럼 선택
        else:
            c.execute("SELECT PW FROM teacher WHERE ID=?", (user_id,))

        user_pw = c.fetchone()             # 한 행 추출

        if not user_pw:  # DB에 없는 id 입력시
            sock.send('!no'.encode())
            con.close()
            return

        if (data[2],) == user_pw:
            clnt_info[n].append(data[1])
            # 로그인성공 시그널
            print("login sucess")
            if 's' in data[0]:
                c.execute("SELECT Study_log FROM student WHERE ID=?",
                          (user_id,))
                study = list(c.fetchone())
                study = ','.join(study)
                clnt_info[n].append(data[0])
                sock.send(study.encode())  # 현재까지 공부한 내용을 전송
            else:
                clnt_info[n].append(data[0])
                sock.send('!OK'.encode())
        else:
            # 로그인실패 시그널
            sock.send('!NO'.encode())
            print("login failure")
        con.close()
        return clnt_info
# 로그인 종료


class Menu:
    def Quiz(msg, info, n):  # 문제 관련 함수
        sock = info[n][0]
        Q_msg = ''
        print(info)
        if 'check' in msg:
            Quizs = ''
            con, c = dbcon()
            c.execute("SELECT who,Quiz,Answer FROM quiz")
            while True:
                data = c.fetchone()
                if data is None:
                    break
                data = list(data)
                quiz = ','.join(data)
                Quizs = Quizs + quiz + ' | '
            sock.send(Quizs.encode())

            Quizs = Quizs.split(' | ')

            while True:  # 선생님이 퀴즈를 만들거나 학생이 맞추는 함수
                Q_msg = sock.recv(BUF_SIZE)
                Q_msg = Q_msg.decode()

                if Q_msg.startswith('!aadd/') and 't' == info[n][5]:
                    Q_msg = Q_msg.replace('!aadd/', '')
                    Q_msg = Q_msg.split('/')
                    print(Q_msg)

                    query = "INSERT INTO quiz(who,Quiz,Answer) VALUES(?, ?, ?)"
                    c.executemany(query, (Q_msg,))
                    con.commit()            # DB에 커밋
                    con.close()

                if Q_msg.startswith('!aadd/') and 's' == info[n][5]:
                    # 서버에서 보내준 정답을 받을곳
                    a = 'defult'

        # 문제관련 함수 끝
