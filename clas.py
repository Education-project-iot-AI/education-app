import sys
import sqlite3
import threading

BUF_SIZE = 1024

lock = threading.Lock()


def dbopen():
    con = sqlite3.connect('edu.db')  # DB 연결
    c = con.cursor()                  # 커서
    return con, c


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
        con, c = dbopen()
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
        data = data.split('/')
        user_id = data[1]
        con, c = dbopen()

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
                c.execute("SELECT study FROM student WHERE ID=?",
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
        lock.acquire()
        con, c = dbopen()
        sock = info[n][0]
        Q_msg = ''
        print(info)
        if 'check' in msg:
            Quizs = ''
            c.execute("SELECT who,Quiz,Answer FROM quiz")  # 누구에게/문제/답 을 가져온다
            while True:
                data = c.fetchone()  # 한 행 추출
                if data is None:
                    break
                data = list(data)
                quiz = ','.join(data)  # 리스트를 문자열화 킨다
                Quizs = Quizs + quiz + ' | '  # 하나로 합친다
            sock.send(Quizs.encode())  # 전송한다

            Quiz_list = Quizs.split(' | ')  # 문제를 맞출때를 생각하여 미리 문제를 리스트로 나눠둔다

            while True:  # 선생님이 퀴즈를 만들거나 학생이 맞추는 함수
                Q_msg = sock.recv(BUF_SIZE)
                Q_msg = Q_msg.decode()

                if Q_msg.startswith('!quizend/'):  # 나간다고 할시
                    break

                # 만약 선생이면서 !aadd/를 시작으로 입력이 들어올때
                if Q_msg.startswith('!quizadd/') and 't' == info[n][5]:
                    Q_msg = Q_msg.replace('!quizadd/', '')  # aadd를 지워주고
                    Q_msg = Q_msg.split('/')  # 리스트화 시킨뒤

                    query = "INSERT INTO quiz(who,Quiz,Answer) VALUES(?, ?, ?)"
                    c.executemany(query, (Q_msg,))  # 데이터베이스에 누가/무슨 문제를/답 을 넣는다
                    con.commit()
                    break

                if Q_msg.startswith('!quizlist/') and 's' == info[n][5]:
                    Q_msg = Q_msg.replace('!quizlist/', '')
                    sock.send(Quizs.encode())  # 문제 전송

                if Q_msg.startswith('!quizstart/') and 's' == info[n][5]:
                    Q_msg = Q_msg.replace('!quizstart/', '')  # 문제를 푼다고 할 시
                    Q_msg = Q_msg.split('/')  # 문제/입력한 답을 리스트화
                    for i in Quiz_list:
                        if Q_msg[0] == i[0] and Q_msg[1] == i[1]:  # 현재 가지고있는 문제와 답이 일치할 시
                            ck_answer = 1
                            break
                    if ck_answer == 1:
                        sock.send('!OK'.encode())  # 맞췃다고 알려줌
                    else:
                        sock.send('!NO'.encode())  # 틀렷다고 알려줌
                    # 서버에서 보내준 정답을 받을곳
        lock.release()
        con.close()
        # 문제관련 함수 끝

    def Student_Study(msg, info, n):  # 학습하기
        con, c = dbopen()
        sock = info[n][0]
        lock.acquire()
        if msg.startswith('save/'):
            msg = msg.replace('save/', '')
            c.execute("SELECT study FROM student WHERE ID=?",
                      (info[n][1],))  # 해당 학생의 공부내용을 불러오기
            temp = c.fetchone()
            temp = ','.join(temp)  # 현재까지 공부한 내용 코드를 문자열로 바꿈
            temp = temp+','+msg  # 추가될 코드를 문자열에 더함
            c.executemany("UPDATE Users SET study = ? WHERE id = ?",
                          (temp, info[1]))  # 데이터베이스에 저장
            con.commit()  # db에 커밋
        if msg.startswith('view'):
            c.execute("SELECT study FROM student WHERE ID=?",
                      (info[1],))  # 해당 학생이 공부한 내용 가져오기
            temp = c.fetchone()
            temp = ','.join(temp)  # 문자열로 변경
            sock.send(temp.encode())  # 클라로 보내기
        lock.release()
        con.close()
# 학습하기 끝

    def Student_info(msg, info, n):  # 학생 통계
        con, c = dbopen()
        sock = info[n][0]
        if msg.startswith('list'):
            lock.acquire()
            c.execute("SELECT name FROM student")  # 모든 학생들의 이름을 가져와서
            S_list = c.fetchall()
            S_list = ','.join(S_list)  # 튜플형태의 학생이름들을 문자열로 변환
            sock.send(S_list.encode())  # 보내기
            lock.release()
            con.close()

        if msg.startswith('study'):
            lock.acquire()
            msg = msg.replace('study/', '')
            c.execute("SELECT study FROM student WHERE name=?",
                      (msg,))  # 검색된 학생의 지금까지의 공부내용 가져오기
            temp = c.fetchone()
            if sys.getsizeof(temp) > 0:  # 공부한 내용이 있는지 없는지 확인
                temp = ','.join(temp)
            else:
                temp = "현재까지 공부한 내용이 없습니다"
            sock.send(temp.encode())
            lock.release()

        if msg.startswith('quiz/'):
            lock.acquire()
            msg = msg.replace('quiz/', '')
            c.execute("SELECT name FROM quiz WHERE name=?",
                      (msg,))  # 검색한 학생의 문제풀이 상황 가져오기
            temp = c.fetchone()
            if sys.getsizeof(temp) > 0:  # 있는지 없는지 확인
                temp = ','.join(temp)
            else:
                temp = "현재까지 받은 문제가 없습니다"
            sock.send(temp.encode())
            lock.release()
        con.close()
# 학생 통계 끝
