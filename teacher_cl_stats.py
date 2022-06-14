import matplotlib.pyplot as plt




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





#####학생별 점수 통계######
if data[0] == '학생통계':
    #[0,0] 위치의 막대 그래프 <현재 그래프는 배열이 1차원이기에 [0]/[1] 이런식으로 범위를 지정해줘야함>
    axes[0].bar([data[1].keys()], [data[1].values()], color=nationColor, alpha = 0.4)       #알파는 뭐임 => 색의 투명도를 지정하는 것
    #막대그래프 제목 설정
    axes[0].set_title('학생별 점수 통계',fontsize=12)
    #막대그래프 x축 제목
    axes[0].set_xlabel('이름', fontsize=10)
    #막대그래프 y축 제목
    axes[0].set_ylabel('점수', fontsize=10)





#####오답문제 통계######
elif data[0] == '오답통계':
    #[0,1] 위치의 선그래프
    axes[1].plot(range(5),[data[1],data[2],data[3],data[4],data[5]],color='red',marker='o')
    axes[1].set_title('문제별 통계', fontsize=12)
    axes[1].set_xlabel('문제', fontsize=10)
    axes[1].set_ylabel('틀린 회수', fontsize=10)


plt.show()


#한글 폰트 깨지는 거 한글폰트 다운 받아서 실행해보기