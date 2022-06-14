import matplotlib.pyplot as plt
import socket


class stats:
    def __init__(self):
        self.port = 15369
        self.address = ("localhost", self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)
        print("서버와 연결완료")
        # self.sock.listen(5)
        self.student_stats = {}  # 학생 별 통계 처리 시 사용될 딕
        self.first_x = []
        self.first_y = []


        # gui에서 버튼을 눌렀다고 가정
        self.button_click()





########이 부분 버튼 클릭시 연결##########
    def button_click(self):
        self.sock.send('통계'.encode())
        print('데이터 보냄')
        self.data = self.sock.recv(8192).decode()
        self.data = eval(self.data)
        print(type(self.data[0]))
        print('데이터 받음')
        print(self.data)
        print(self.data[0])

        f, axes = plt.subplots(2,1)     #다중플롯 생성 가로=>2개, 세로=>1개
        #여기서 위 f는 figure전체를 컨트롤할 수 있는 변수이고 axes는 그래프 각각을 조절할 수 있는 변수임
        # 격자 크기 설정
        f.set_size_inches((10,5))   #위젯의 크기 첫번째는 가로길이, 두번째는 세로길이
        #격자 여백 설정
        plt.subplots_adjust(wspace= 0.5, hspace= 0.5)       #w는 가로 여백, h는 세로여백
        #막대그래프 색상 정리
        nationColor = ['red', 'green','yellow','blue']
        #위젯 전제 제목설정시 사용
        # f.suptitle('Subplot Example', fontsize = 15)
        print("확인용 43번째 줄")




        #####학생별 점수 통계######
        #에러잡자..
        self.student_stats = self.data[0]
        print('56번째',self.student_stats.values())
        self.first_x = list(self.student_stats.keys())
        print('58번째', self.first_x)
        self.first_y = list(self.student_stats.values())
        print('60번째', self.first_y)
        print(type(self.first_y[0]))


        #[0] 위치의 막대 그래프 <현재 그래프는 배열이 1차원이기에 [0]/[1] 이런식으로 범위를 지정해줘야함>
        axes[0].set_yticks([1,2,3,4,5])   #y축 눈금단위 조정
        axes[0].bar(self.first_x, self.first_y, color=nationColor, alpha = 0.4)       #알파는 뭐임 => 색의 투명도를 지정하는 것
        #막대그래프 제목 설정
        axes[0].set_title('학생별 점수 통계',fontsize=12)
        #막대그래프 x축 제목
        axes[0].set_xlabel('이름', fontsize=10)
        #막대그래프 y축 제목
        axes[0].set_ylabel('점수', fontsize=10)
        print("확인용 62번째줄")

        self.data.pop(0)


    #####오답문제 통계######
        #[1]위치의 선그래프
        axes[1].set_xticks([1,2,3,4,5])         # x축 눈금단위 조정
        axes[1].plot([1,2,3,4,5],[i for i in self.data],color='red',marker='o')
        axes[1].set_title('문제별 통계', fontsize=12)
        axes[1].set_xlabel('문제', fontsize=10)
        axes[1].set_ylabel('틀린 회수', fontsize=10)
        print("확인용 72번째")

        plt.show()





if __name__ == "__main__":
    stats()

        #한글 폰트 깨지는 거 한글폰트 다운 받아서 실행해보기