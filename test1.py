import requests
import time
from xml.etree.ElementTree import fromstring

url = 'http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo'
data = []
counter = 0
code_back = 1147
while counter < 151:
    code_back += 1
    code = 'A00000' + str(code_back)
    params = {'serviceKey': '9cCN4TXQK/nLX/tkVrz9+4qnPHIyI5sjjCpkfO9kPAH8y6fDcWtxwsp7JM0bozPvZklvvCVKqnZOig81BIMjmw==', 'q1': code}  # 번호에서 도감
    doc = fromstring(requests.get(url, params=params).content.decode())
    try:
        name = doc[1][0][6].text
    except IndexError:
        continue
    counter += 1
    print(f'연번 : {counter}')
    print(f'코드 : {code}')
    print(f'이름 : {doc[1][0][6].text}')
    dat_write = f'{counter}, {code}, {doc[1][0][6].text}\n'
    with open('data.txt', 'a') as dat:
        dat.write(dat_write)
    time.sleep(1)
else:
    pass
