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
    def recv(sock):
        sys.stdout.flush()  # 버퍼 비우기
        clnt_msg = sock.recv(BUF_SIZE)  # 메세지 받아오기
        clnt_msg = clnt_msg.decode()  # 디코딩
        return clnt_msg

    def send(sock, msg):
        sys.stdin.flush()  # 버퍼 비우기
        msg = msg.encode()  # 인코딩
        sock.send(msg)  # 메세지 보내기


class Menu:
    def reg(move, clnt_sock):
        con, c = dbcon()
        user_data = []
        while True:
            ck_login = 0
            imfor = clnt_sock.recv(BUF_SIZE)
            imfor = imfor.decode()

            if imfor == "Q_reg":      # 회원가입 창 닫을 때 함수 종료
                con.close()
                break

            c.execute(
                "SELECT DISTINCT teacher.ID, student.ID From teacher LEFT JOIN student ON teacher.ID != student.ID")
            for row in c:  # id 컬럼
                if imfor in row:       # 클라이언트가 입력한 id가 DB에 있으면
                    clnt_sock.send('!NO'.encode())
                    ck_login = 1
                    break
            if ck_login == 1:
                continue

            clnt_sock.send('!OK'.encode())  # 중복된 id 없으면 !OK 전송
            lock.acquire()
            user_data.append(imfor)  # user_data에 id 추가
            imfor = clnt_sock.recv(BUF_SIZE)  # password/name/email
            imfor = imfor.decode()

            if imfor == "Q_reg":  # 회원가입 창 닫을 때 함수 종료
                con.close()
                break

            imfor = imfor.split('/')  # 구분자 /로 잘라서 리스트 생성

            for i in range(3):
                user_data.append(imfor[i])       # user_data 리스트에 추가
            query = "INSERT INTO Users(id, password, name, email) VALUES(?, ?, ?, ?)"
            c.executemany(query, (user_data,))  # DB에 user_data 추가
            con.commit()            # DB에 커밋

            con.close()
            lock.release()
            break

    def log_in(clnt_sock, data, clnt_info):
        con, c = dbcon()
        data = data.split('/')
        user_id = data[1]

        if 'student' in data[0]:
            c.execute("SELECT PW FROM student WHERE ID=?",
                      (user_id,))  # DB에서 id 같은 password 컬럼 선택
        else:
            c.execute("SELECT PW FROM teacher WHERE ID=?", (user_id,))

        user_pw = c.fetchone()             # 한 행 추출
        if not user_pw:  # DB에 없는 id 입력시
            clnt_sock.send('iderror'.encode())
            con.close()
            return
        if (data[2],) == user_pw:
            # 로그인성공 시그널
            print("login sucess")
        else:
            # 로그인실패 시그널
            clnt_sock.send('!NO'.encode())
            print("login failure")
        con.close()
        return clnt_info
