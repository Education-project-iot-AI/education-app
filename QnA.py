def QnA(sock, clnt_info):
    con, c= clas.dbcon()    
    msg = clas.Msg.send(sock)    
    
    if 's' in clnt_info[2]: #학생일때
        if '!qnacheck' in msg:
            c.execute("SELECT name, Question, Answer FROM QnA") #학생꺼만
            print(con.fetchall())
            
            print(f'QnA등록 하시겠습니까?') 
            sock.send('!aadd'.encode())          
            if # 등록시
                query="INSERT INTO QnA(Name, Question) VALUES(?, ?)"
                c.executemany(query, (clnt_info,))

            
    elif 't' in clnt_info[2]: #선생일때
        if '!qnacheck' in msg:
            c.execute("SELECT * FROM QnA") #전체 QnA
            print(con.fetchall())    
            
            print('QnA답변 하시겠습니까?')
            sock.send('!qadd'.encode())     
            if # 등록시/ 선생이 선택해서 등록 해야되는데..
                query="UPDATE QnA SET Answer=?"
                c.executemany(query, (msg,))
    con.close()
