
import sqlite3


def dbcon():
    con = sqlite3.connect('edu.db')  # DB 연결
    c = con.cursor()                  # 커서
    return (con, c)


con, c = dbcon()

c.execute("SELECT DISTINCT teacher.ID, student.ID From teacher LEFT JOIN student ON teacher.ID != student.ID")
imfor = "213"
for row in c:  # id 컬럼
    if imfor in row:       # 클라이언트가 입력한 id가 DB에 있으면
        print("안돼")
        ck_login = 1
        break
