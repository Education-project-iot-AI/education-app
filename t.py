
import sqlite3


def dbcon():
    con = sqlite3.connect('edu.db')  # DB 연결
    c = con.cursor()                  # 커서
    return (con, c)


con, c = dbcon()
imfor = "213"
pw ="123"
c.execute("SELECT PW From teacher WHERE ID=?",(imfor,))

for row in c:  # id 컬럼
    print(row)
    if pw in row:       # 클라이언트가 입력한 id가 DB에 있으면
        print("안돼")
        ck_login = 1
        break