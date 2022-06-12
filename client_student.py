import requests
import re
import pprint
import pandas
import xml.etree.ElementTree as et
import xmltodict
import random
import pymysql
import socket
import json
import time

# api에서 받은 곤충 리스트
exam_list = []
# api에서 받은 곤충 리스트 중 랜덤 5개 추출
num = []



#####공공데이터 오픈API에서 데이터 받아오기######

# 곤충 데이터 범위

for i in range(100,200):

    aa = 'ZRDS0'+str(i)                 # 곤충별 코드넘버

    #공공데이터 API연결
    key = 'mceUd1TSkEs27aaL/yalh1rMGIrp873AwiitSYuFZ0fYETH5X9O5P8vxcb3JYE335Co7c/vCsyMGISin6fHR8w=='        #발급받은 키값(decode주소)
    url = 'http://openapi.nature.go.kr/openapi/service/rest/InsectService/isctIlstrInfo?serviceKey={}&q1={}'.format(key, aa)        #사용하고자하는 주소의 url
    content = requests.get(url).content     #데이터 가져오기
    dict = xmltodict.parse(content)         #ordereddict타입으로 결과값을 리턴함 (xml을 딕셔너리 형태로 데이터 변환)

    # 곤충의 설명과 생태가 있는 데이터만 뽑아옴(곤충 데이터 중 설명 또는 생태가 없는 데이터들이 있기에 학습을 위해)
    try:
        if dict['response']['body']['item']['cont1'] and dict['response']['body']['item']['cont7'] != None:     #count1이 설명이고 count7이 생태임
            exam_list.append(dict['response']['body']['item']['insctOfnmKrlngNm'])      #곤충국명
            exam_list.append(dict['response']['body']['item']['cont1'])                 #곤충설명
            exam_list.append(dict['response']['body']['item']['cont7'])                 #곤충생태

            # 확인용
            # print("국명 : ", dict['response']['body']['item']['insctOfnmKrlngNm'])
            # print("일반특징 : ", dict['response']['body']['item']['cont1'])
            # print("생태 : ", dict['response']['body']['item']['cont7'])

    except:
        pass

#####api에서 받은 데이터 중 랜덤 5개 학습#####(해당 데이터의 순서가 첫번째 국명 두번째 설명 세번째 생태 형태로 뽑아 오게끔 만들어 놨기에 3의 배수가 국명에 들어 갈 수 있게끔 해놓고 순서대로 +1씩 취가되는 형식으로 정리함
#split은 구분자를 사용해 sting형식을 나누고 리스트 형식으로 반환하는데 위 데이터는 리스트 형식으로 이미 정리가 되어있기에 데이터를 split을 사용하는 게 쉽지 않았음.
for i in range(90):
    if i%3 == 0:            #3의 배수에 해당되는 값만 출력하여 num이라는 빈 리스트에 담음
        num.append(i)
print(num)

random_exam = random.sample(num, 5)     #mum에 추가된 3의 배수중 랜덤으로 5개를 추출하여 변수에 저장함
print(random_exam)

#1번 학습
first_1 = exam_list[random_exam[0]]            #국명
first_2 = exam_list[random_exam[0]+1]          #설명
first_3 = exam_list[random_exam[0]+2]          #생태

first_edu = [first_1, first_2, first_3]

#2번 학습
second_1 = exam_list[random_exam[1]]
second_2 = exam_list[random_exam[1]+1]
second_3 = exam_list[random_exam[1]+2]

second_edu = [second_1, second_2, second_3]

#3번 학습
third_1 = exam_list[random_exam[2]]
third_2 = exam_list[random_exam[2]+1]
third_3 = exam_list[random_exam[2]+2]

third_edu = [third_1, third_2, third_3]

#4번 학습
fourth_1 = exam_list[random_exam[3]]
fourth_2 = exam_list[random_exam[3]+1]
fourth_3 = exam_list[random_exam[3]+2]

fourth_edu = [fourth_1, fourth_2, fourth_3]

#5번 학습
fifth_1 = exam_list[random_exam[4]]
fifth_2 = exam_list[random_exam[4]+1]
fifth_3 = exam_list[random_exam[4]+2]

fifth_edu = [fifth_1, fifth_2, fifth_3]

#학습데이터 정리(서버로 보낼 학습데이터 정리)
array_edu = [first_edu, second_edu, third_edu, fourth_edu, fifth_edu]

#확인용
print(array_edu)




########서버에 학습내용 보내기######
port = 13308
address = ("localhost",port)
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(address)

for i in array_edu:
    jsonString = json.dumps(i, ensure_ascii=False)   #xmltodict형태를 json으로 변경해주는 중 (= 아스키 코드가 아니다)
    print(jsonString)
    sock.send(jsonString.encode())
    time.sleep(1)





##### 학습 정보 데이터베이스에 저장(마리아db사용함)##### (학습한 데이터 저장을 원할시 저장할 수 있게 별도의 데이터베이스에 저장할 예정임)
# db 연결
# connection = pymysql.connect(host='localhost', port=3306, user='root', password='1234',db='edu_project', charset = 'utf8')
#
# #커서 만들기
# cursor = connection.cursor()
#
# #테이블생성(곤충 - 이름,설명,생태)
# create_table = ("create table `edu_save`(`name` varchar(20), `intro` varchar(255), `ecology` varchar(255))")
#
# cursor.execute(create_table)
#
# # 1번학습 레코드 추가
# cursor.execute('insert into edu_save values(%s, %s, %s)', (first_1, first_2, first_3))
# connection.commit()
# # 2번학습 레코드 추가
# cursor.execute('insert into edu_save values(%s, %s, %s)', (second_1, second_2, second_3))
# connection.commit()
# # 3번학습 레코드 추가
# cursor.execute('insert into edu_save values(%s, %s, %s)', (third_1, third_2, third_3))
# connection.commit()
# # 4번학습 레코드 추가
# cursor.execute('insert into edu_save values(%s, %s, %s)', (fourth_1, fourth_2, fourth_3))
# connection.commit()
# # 5번학습 레코드 추가
# cursor.execute('insert into edu_save values(%s, %s, %s)', (fifth_1, fifth_2, fifth_3))
# connection.commit()
#
# #나가기
# connection.close()
#
#
#
#
# ######데이터베이스에서 저장된 학습내용 불러오기######
# connection = pymysql.connect(host='localhost', port=3306, user='root', password='1234',db='edu_project', charset = 'utf8')
# cursor = connection.cursor()
# sql = 'select * from edu_save'
# cursor.execute(sql)
#
# result = cursor.fetchall()
# for res in result:
#     print(res)
#
# connection.close()
#
#
#
#








