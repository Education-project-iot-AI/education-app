import requests
from xml.etree.ElementTree import fromstring

code = 'A000001149'
service = '9cCN4TXQK/nLX/tkVrz9+4qnPHIyI5sjjCpkfO9kPAH8y6fDcWtxwsp7JM0bozPvZklvvCVKqnZOig81BIMjmw=='

url = 'http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo'
params = {'serviceKey': service, 'q1': code}

doc = fromstring(requests.get(url, params=params).content.decode())
print(f'이름 : {doc[1][0][6].text}')
print(f'정보 : {doc[1][0][16].text}')

