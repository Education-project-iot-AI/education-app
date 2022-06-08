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
    def move_to(move,clnt_sock):
        if move == 'reg':
            con,c = dbcon()
            user_data=[]
            while True:
                ck_login=0
                imfor = clnt_sock.recv(BUF_SIZE)
                imfor = imfor.decode()
                if imfor == "Q_reg":      # 회원가입 창 닫을 때 함수 종료
                    con.close()
                    break
                c.execute("SELECT id FROM Users")  # Users 테이블에서 id 컬럼 추출
                for row in c:  # id 컬럼
                    if imfor in row:       # 클라이언트가 입력한 id가 DB에 있으면
                        clnt_sock.send('!NO'.encode())
                        ck_login=1
                        break
                if ck_login==1:
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
