from audioop import add
import sys
import sqlite3
import threading

BUF_SIZE = 1024
s_join = 0
t_join = 0

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

            if imfor == "^Q_join":      # 회원가입 창 닫을 때 함수 종료
                con.close()
                break

            if '^idcheck/' in imfor:  # 아이디 중복확인
                lock.acquire()
                imfor = imfor.replace('^idcheck/', '')
                c.execute(
                    "SELECT DISTINCT teacher.ID, student.ID From teacher LEFT JOIN student ON teacher.ID != student.ID")
                for row in c:  # id 컬럼
                    if imfor in row:       # 클라이언트가 입력한 id가 DB에 있으면
                        sock.send('^NO'.encode())
                        ck_login = 1
                        break
                lock.release()
                if ck_login == 1:
                    continue
                print('d')
                sock.send('^ok'.encode())  # 중복된 id 없으면 !OK 전송
            # 중복확인 종료

            if imfor.startswith('^joindata/'):
                lock.acquire()
                imfor = imfor.replace('^joindata/', '')
                imfor = imfor.split('/')  # 구분자 /로 잘라서 리스트 생성

                for i in range(3):
                    user_data.append(imfor[i])       # user_data 리스트에 추가

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
            sock.send('^NO'.encode())
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
                study = '^OK/'+study
                clnt_info[n].append(data[0])
                sock.send(study.encode())  # 현재까지 공부한 내용을 전송
            else:
                clnt_info[n].append(data[0])
                sock.send('^OK'.encode())
            if 's' in data[0]:
                c.execute("SELECT name FROM student WHERE ID=?",
                          (user_id,))
            else:
                c.execute("SELECT name FROM teacher WHERE ID=?",
                          (user_id,))
            name = ''.join(c.fetchone())
            clnt_info[n].append(name)
        else:
            # 로그인실패 시그널
            sock.send('^NO'.encode())
            print("login failure")
        con.close()
        return clnt_info
# 로그인 종료


class Menu:
    def Quiz(msg, info, n):  # 문제 관련 함수
        con, c = dbopen()
        sock = info[n][0]
        name = info[n][4]
        id = info[n][2]
        ck_answer = 0
        Quiz_list = []
        Quizs = ''
        # 문제/답/점수/현재까지 정답을 말한 인원을 가져온다
        c.execute("SELECT Quiz,Answer,point,who FROM quiz")
        for row in c:
            row = ','.join(row)
            Quizs = Quizs + row + ' | '  # 하나로 합친다
        Quiz_list = Quizs.split(' | ')
        lock.acquire()
        if 'check' in msg:
            sock.send(Quizs.encode())  # 전송한다

        # 만약 선생이면서 add/를 시작으로 입력이 들어올때
        if msg.startswith('add/') and 't' == info[n][3]:
            msg = msg.replace('add/', '')  # aadd를 지워주고
            msg = msg.split('/')  # 리스트화 시킨뒤

            query = "INSERT INTO quiz(Quiz,Answer,point) VALUES(?, ?, ?)"
            c.executemany(query, (msg,))  # 데이터베이스에 누가/무슨 문제를/답 을 넣는다
            con.commit()

        if msg.startswith('start/') and 's' == info[n][3]:
            msg = msg.replace('start/', '')  # 문제를 푼다고 할 시
            msg = msg.split('/')  # 문제/입력한 답을 리스트화
            for i in Quiz_list:
                i = i.split(',')
                if msg[0] == i[0] and msg[1] == i[1]:  # 현재 가지고있는 문제와 답이 일치할 시
                    if id in i[3]:
                        sock.send("이미 답을 낸 문제입니다".encode())
                        break
                    c.execute("SELECT point FROM student WHERE ID = ?",
                              (id,))
                    addpoint = ''.join(c.fetchone())
                    addpoint = str(int(addpoint) + int(i[2]))

                    c.execute("UPDATE student SET point = ? WHERE id = ?",
                              (addpoint, id))  # 데이터베이스에 저장
                    con.commit()
                    c.execute("SELECT who FROM quiz")
                    temp = c.fetchone()

                    if temp == ('X',):
                        temp = name
                    else:
                        temp = ','.join(c.fetchone)
                        temp = temp + ',' + name

                    c.execute("UPDATE quiz SET who = ? WHERE Quiz = ?",
                              (temp, i[0]))  # 데이터베이스에 저장
                    con.commit()

                    sock.send('^OK'.encode())  # 맞췃다고 알려줌
                    ck_answer = 1
                    break
            if ck_answer != 1:
                sock.send('^NO'.encode())  # 틀렷다고 알려줌
            # 서버에서 보내준 정답을 받을곳
        lock.release()
        con.close()
        # 문제관련 함수 끝

    def Student_Study(msg, info, n):  # 학습하기
        con, c = dbopen()
        id = info[n][2]
        sock = info[n][0]
        lock.acquire()
        if msg.startswith('save/'):
            msg = msg.replace('save/', '')
            c.execute("SELECT study FROM student WHERE ID=?",
                      (id,))
            temp = c.fetchone()
            print(temp)
            if temp == ('X',):
                temp = msg
            else:
                temp = ','.join(temp)  # 현재까지 공부한 내용 코드를 문자열로 바꿈
                temp = temp+','+msg  # 추가될 코드를 문자열에 더함
            c.execute("UPDATE student SET study = ? WHERE id = ?",
                      (temp, id))  # 데이터베이스에 저장
            con.commit()  # db에 커밋
        if msg.startswith('view'):
            c.execute("SELECT study FROM student WHERE ID=?",
                      (id,))  # 해당 학생이 공부한 내용 가져오기
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
            S_list = []
            lock.acquire()
            c.execute("SELECT name FROM student")  # 모든 학생들의 이름을 가져와서
            for row in c:
                row = ''.join(row)
                S_list.append(row)
            S_list = ','.join(S_list)  # 문자열로 변경
            sock.send(S_list.encode())  # 보내기
            lock.release()
            con.close()

        if msg.startswith('study/'):
            lock.acquire()
            msg = msg.replace('study/', '')
            c.execute("SELECT study FROM student WHERE name=?",
                      (msg,))  # 검색된 학생의 지금까지의 공부내용 가져오기
            temp = c.fetchone()
            print(temp)
            if temp == ('X',):  # 공부한 내용이 있는지 없는지 확인
                temp = "현재까지 공부한 내용이 없습니다"
            else:
                temp = ','.join(temp)
            sock.send(temp.encode())
            lock.release()

        if msg.startswith('quiz/'):
            s_list = []
            lock.acquire()
            msg = msg.replace('quiz/', '')
            c.execute("SELECT Quiz,who FROM quiz")  # 검색한 학생의 문제풀이 상황 가져오기
            for row in c:
                if row != ('X',) and row[1] in msg:
                    row = list(row)
                    s_list.append(row[0])
            s_list = ','.join(s_list)

            sock.send(s_list.encode())
            lock.release()
        con.close()
# 학생 통계 끝

    def Sangdam(msg, info, n): #채팅 시작
        global s_join, t_join
        sock = info[n][0]
        msg = ''
        if s_join != 0 and info[n][3] == 's': #상담중인 사람이 있을 시
            sock.send("다른 학생이 상담하고있습니다".encode())
            return
        if t_join != 0 and info[n][3] == 't':
            sock.send("다른 선생님이 상담하고있습니다".encode())
            return
        if info[n][3] == 's':
            s_join = 1
        else:
            t_join = 1
        info[n][1] = 1  #[n][1]이 1인 사람에게만 채팅이 들어감
        name = info[n][4]
        print("들어옴")
        while True:
            msg = sock.recv(BUF_SIZE)
            msg = msg.decode()

            if msg.startswith('^Q_chat') or not msg:    #나갈때
                if info[n][3] == 's':
                    s_join = 0
                else:
                    t_join = 0
                info[n][1] = 0
                break

            for C_sock in info:
                if C_sock[1] == 1:
                    if info[n][0] != C_sock[0]:
                        C_sock = C_sock[0]
                        msg = name + ' : ' + msg#메세지에 이름 추가
                        C_sock.send(msg.encode())
