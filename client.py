import sys
import requests
import random
from socket import *
from PyQt5 import uic, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from xml.etree.ElementTree import fromstring

# 수신 스레드, 스레드 시그널, 시그널 선언, 수신 슬롯
# 유사 로그인
# 회원 가입 ID 입력란 시그널 - 디스에이블 체크
# 채팅 연결 준비


clientui = uic.loadUiType("tonghap.ui")[0]  # ui 불러오기
server_ip = '127.0.0.1'  # 서버 ip (임시로 루프백)
portnumber = '25000'  # 서버 포트
s_skt = socket(AF_INET, SOCK_STREAM)  # 서버 소켓 선언
url = 'http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo'  # API 주소
serviceKey = '9cCN4TXQK/nLX/tkVrz9+4qnPHIyI5sjjCpkfO9kPAH8y6fDcWtxwsp7JM0bozPvZklvvCVKqnZOig81BIMjmw=='  # API 키
birdcodelist = ['A000001149', 'A000001150', 'A000001151', 'A000001152', 'A000001153', 'A000001154', 'A000001155',
                'A000001156', 'A000001160', 'A000001161', 'A000001162', 'A000001164', 'A000001165', 'A000001166',
                'A000001167', 'A000001168', 'A000001169', 'A000001170', 'A000001171', 'A000001172', 'A000001176',
                'A000001177', 'A000001178', 'A000001180', 'A000001181', 'A000001182', 'A000001183', 'A000001184',
                'A000001185', 'A000001188', 'A000001189', 'A000001191', 'A000001195', 'A000001197', 'A000001199',
                'A000001201', 'A000001204', 'A000001205', 'A000001206', 'A000001207', 'A000001209', 'A000001210',
                'A000001211', 'A000001213', 'A000001216', 'A000001218', 'A000001220', 'A000001221', 'A000001222',
                'A000001223', 'A000001224', 'A000001225', 'A000001226', 'A000001227', 'A000001228', 'A000001229',
                'A000001231', 'A000001233', 'A000001235', 'A000001236', 'A000001239', 'A000001241', 'A000001243',
                'A000001246', 'A000001248', 'A000001250', 'A000001251', 'A000001253', 'A000001254', 'A000001255',
                'A000001256', 'A000001257', 'A000001259', 'A000001260', 'A000001261', 'A000001264', 'A000001265',
                'A000001266', 'A000001267', 'A000001270', 'A000001271', 'A000001273', 'A000001275', 'A000001279',
                'A000001280', 'A000001282', 'A000001285', 'A000001287', 'A000001291', 'A000001292', 'A000001295',
                'A000001299', 'A000001304', 'A000001305', 'A000001306', 'A000001307', 'A000001308', 'A000001309',
                'A000001310', 'A000001311', 'A000001313', 'A000001316', 'A000001317', 'A000001318', 'A000001319',
                'A000001320', 'A000001324', 'A000001326', 'A000001327', 'A000001328', 'A000001329', 'A000001330',
                'A000001333', 'A000001334', 'A000001336', 'A000001337', 'A000001338', 'A000001340', 'A000001341',
                'A000001344', 'A000001347', 'A000001354', 'A000001355', 'A000001357', 'A000001358', 'A000001360',
                'A000001361', 'A000001362', 'A000001365', 'A000001366', 'A000001367', 'A000001368', 'A000001369',
                'A000001370', 'A000001371', 'A000001372', 'A000001374', 'A000001376', 'A000001377', 'A000001383',
                'A000001384', 'A000001386', 'A000001387', 'A000001388', 'A000001390', 'A000001391', 'A000001393',
                'A000001394', 'A000001395', 'A000001397']  # 학습 & 출제 대상 코드 리스트


class Main(QMainWindow, clientui):  # 메인 클래스
    rcv_idcheck_ok = pyqtSignal()  # 이하 시그널 선언
    rcv_idcheck_no = pyqtSignal()
    rcv_logintcheck_ok = pyqtSignal()
    rcv_loginscheck_ok = pyqtSignal()
    rcv_logincheck_no = pyqtSignal()

    def __init__(self):  # 이니셜라이저
        super().__init__()  # 상속
        self.setupUi(self)  # ui 로딩
        self.stackedWidget.setCurrentIndex(0)  # 초기 페이지 설정
        self.cdr = ClientDataRecv()  # 데이터 수신 스레드 선언
        self.btn_connect()  # 버튼 연결 함수 호출
        self.client_ready()  # 클라이언트 초기 함수 호출

        self.cdr.rcv_idcheck_ok.connect(self.join_idcheck_ok)  # 데이터 수신 대기 스레드의 ID 중복확인 ok 시그널 선언
        self.cdr.rcv_idcheck_no.connect(self.join_idcheck_no)  # 데이터 수신 대기 스레드의 ID 중복확인 no 시그널 선언
        self.cdr.rcv_logintcheck_ok.connect(self.rcv_logintcheck_ok)  # 데이터 수신 대기 스레드의 교사로그인확인 ok 시그널 선언
        self.cdr.rcv_loginscheck_ok.connect(self.rcv_loginscheck_ok)  # 데이터 수신 대기 스레드의 학생로그인확인 ok 시그널 선언
        self.cdr.rcv_logincheck_no.connect(self.rcv_logincheck_no)  # 데이터 수신 대기 스레드의 로그인확인 no 시그널 선언

    def client_ready(self):  # 클라이언트 초기 함수
        s_skt.connect((server_ip, int(portnumber)))  # 서버 소켓 커넥트
        self.cdr.start()  # 데이터 수신 대기 스레드 시작

    def btn_connect(self):  # 버튼 연결 함수
        self.btn_join.clicked.connect(self.join_start)  # 메인 화면, 회원 가입 연결
        # self.btn_login.clicked.connect(self.join_start)

        self.btn_debug_t.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))  # 메인 화면, 디버그-교사로그인 연결
        self.btn_debug_s.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))  # 메인 화면, 디버그-학생로그인 연결

        self.btn_join_backmain.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))  # 회원 가입, 돌아가기 연결
        self.btn_join_id_check.clicked.connect(self.join_idcheck)  # 회원 가입, ID 중복 체크 확인
        self.btn_join_confirm.clicked.connect(self.join_confirm)  # 회원 가입, ID 중복 체크 확인

        self.btn_t_logout.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))  # 교사 페이지, 로그아웃(돌아가기) 연결

        self.btn_s_logout.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))  # 학생 페이지, 로그아웃(돌아가기) 연결
        self.btn_s_study.clicked.connect(self.student_study_start)  # 학생 페이지, 학습하기 연결

        self.btn_s_study_back.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))  # 학습하기 페이지, 돌아가기 연결
        self.btn_s_study_on.clicked.connect(self.student_study)  # 학습하기 페이지, 학습 자료 보기 연결

    def join_start(self):  # 회원 가입 - 페이지 초기화 함수
        self.stackedWidget.setCurrentIndex(1)  # 회원 가입 페이지로 전환
        for i in ['id', 'pw', 'pw_check', 'name']:  # 회원 가입 페이지의 라인 초기화
            exec(f'self.line_join_{i}.clear()')
        self.btn_join_confirm.setDisabled(True)  # 회원 가입 버튼 비활성화
        self.radio_join_t.setChecked(False)  # 이하 회원 속성 라디오 버튼 초기화
        self.radio_join_s.setChecked(False)

    def join_idcheck(self):  # 회원 가입 - 아이디 중복 체크 함수
        if not self.line_join_id.text():  # ID 란이 비었으면
            QMessageBox.warning(self, 'ID 입력', 'ID를 입력하셔야 합니다')  # 경고 메시지 출력
            self.line_join_id.clear()  # ID 란 초기화
        elif self.forbidden_word_check(self.line_join_id.text()):  # 금지어가 포함되어 있으면
            QMessageBox.warning(self, '금지어 포함', '공백, !, /, |, ^는 사용할 수 없습니다')
            self.line_join_id.clear()
        else:  # ID가 존재하고 금지어도 포함되어 있지 않으면
            sendid = '!idcheck' + '/' + self.line_join_id.text()  # !idcheck 헤더 붙여서 (확정 아님)
            s_skt.send(sendid.encode())  # 서버로 송신

    @pyqtSlot()
    def join_idcheck_ok(self):
        self.btn_join_confirm.setEnabled(True)

    @pyqtSlot()
    def join_idcheck_no(self):
        QMessageBox.warning(self, '사용 불가 ID', '사용할 수 없는 ID입니다')
        self.line_join_id.clear()

    @pyqtSlot()
    def join_logintcheck_ok(self):
        self.btn_join_confirm.setEnabled(True)

    @pyqtSlot()
    def join_loginscheck_ok(self):
        self.btn_join_confirm.setEnabled(True)

    @pyqtSlot()
    def join_logincheck_no(self):
        QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해주세요')
        self.line_login_id.clear()
        self.line_login_pw.clear()

    def join_confirm(self):  # 회원 가입 - 회원 가입 확정 함수
        if not self.line_join_id.text() or not self.line_join_pw.text() or not self.line_join_name.text():  # 입력란이 비었으면
            QMessageBox.warning(self, '입력 누락', '모든 정보를 입력해야 합니다')  # 경고 메시지 출력
        elif self.forbidden_word_check(self.line_join_id.text())\
                or self.forbidden_word_check(self.line_join_pw.text())\
                or self.forbidden_word_check(self.line_join_name.text()):
            QMessageBox.warning(self, '금지어 포함', '공백, !, /, |, ^는 사용할 수 없습니다')  # 경고 메시지 출력
            self.join_clear()  # 금지어 포함 입력란 초기화 함수 호출
        elif self.line_join_pw.text() != self.line_join_pw_check.text():  # 비밀번호와 비밀번호 확인이 일치하지 않으면
            QMessageBox.warning(self, '비밀번호 불일치', '비밀번호를 다시 한번 확인해 주세요')  # 경고 메시지 출력
            self.join_clear()  # 금지어 포함 입력란 초기화 함수 호출
        else:  # 금지어도 없고 비밀번호 확인도 일치하면
            if self.radio_join_t.isChecked():  # 교사 회원이 체크되어 있을 때
                joindata = '!newteacher' + '/' + self.line_join_id.text() +\
                           '/' + self.line_join_pw.text() + '/' + self.line_join_name.text()  # 교사회원 헤더 붙여서(확정 아님)
                s_skt.send(joindata.encode())  # 송신
                QMessageBox.about(self, '회원 가입 완료', '회원 가입이 완료되었습니다')  # 완료 메시지 출력
                self.stackedWidget.setCurrentIndex(0)  # 메인 페이지로 이동
            elif self.radio_join_s.isChecked():  # 학생 회원이 체크되어 있을 때
                joindata = '!newstudent' + '/' + self.line_join_id.text() +\
                           '/' + self.line_join_pw.text() + '/' + self.line_join_name.text()  # 이하 동일
                s_skt.send(joindata.encode())
                QMessageBox.about(self, '회원 가입 완료', '회원 가입이 완료되었습니다')
                self.stackedWidget.setCurrentIndex(0)
            else:  # 라디오 버튼이 체크되어 있지 않을 때
                QMessageBox.warning(self, '회원 선택', '교사 회원 / 학생 회원을 선택해 주세요')  # 경고 메시지 출력

    def forbidden_word_check(self, text):
        if ' ' in text or '?' in text or '/' in text or '|' in text:
            return True
        else:
            return False

    def join_clear(self):  # 금지어 포함 입력란 초기화 함수
        self.line_join_pw_check.clear()
        if self.forbidden_word_check(self.line_join_id.text()):
            self.line_join_id.clear()
        if self.forbidden_word_check(self.line_join_pw.text()):
            self.line_join_pw.clear()
        if self.forbidden_word_check(self.line_join_name.text()):
            self.line_join_name.clear()

    def student_study_start(self):  # 학습하기 페이지 초기 함수
        self.text_study_name.clear()  # 이름란 초기화
        self.text_study_info.clear()  # 정보란 초기화
        self.stackedWidget.setCurrentIndex(4)  # 학습하기 페이지로 전환

    def student_study(self):  # 학습하기 함수
        code = random.choice(birdcodelist)  # 학습 & 출제 대상 코드 리스트에서 랜덤 추출
        params = {'serviceKey': serviceKey, 'q1': code}  # 패러미터에 입력
        bird_data = fromstring(requests.get(url, params=params).content.decode())  # 조류 정보 API에서 획득
        self.text_study_name.clear()  # 이름란 초기화
        self.text_study_info.clear()  # 정보란 초기화
        self.text_study_name.append(bird_data[1][0][6].text)  # 이름란 이름 표시
        self.text_study_info.append(bird_data[1][0][16].text)  # 정보란 정보 표시


class ClientDataRecv(QThread):  # 데이터 수신 대기 스레드 - 다른 프로젝트에서 썼던 코드를 그대로 들어다 박은 거라 거의 다 고칠겁니다
    rcv_idcheck_ok = pyqtSignal()  # 이하 시그널 선언
    rcv_idcheck_no = pyqtSignal()
    rcv_logintcheck_ok = pyqtSignal()
    rcv_loginscheck_ok = pyqtSignal()
    rcv_logincheck_no = pyqtSignal()

    def __init__(self):  # 이니셜라이저
        super().__init__()  # 상속

    def run(self):  # 실행 함수
        while True:  # 무한 루프
            # s_skt = Main.server_addr[0]  # 서버 소켓을 서버 주소 리스트에서 추출
            try:  # 예외 처리 준비
                rcv_msg = s_skt.recv(1024).decode()
                print(f'받은 값 : {rcv_msg}')
                # rcv_msg = pickle.loads(s_skt.recv(1024))  # 서버 소켓에서 수신한 데이터 디코드
            except EOFError:  # 접속이 끊긴 경우
                print('EOF Error?')
                continue
                # break  # 루프 종료
            else:  # 예외가 발생하지 않았다면
                if '!idcheckok' in rcv_msg:  # 수신 메시지에 ID 중복확인 ok 헤더가 있으면
                    print('!idcheckok')
                    self.rcv_idcheck_ok.emit()  # ID 중복확인 ok 시그널 발신인
                elif '!idcheckno' in rcv_msg:  # 수신 메시지에 ID 중복확인 no 헤더가 있으면
                    print('!idcheckno')
                    self.rcv_idcheck_no.emit()  # ID 중복확인 no 시그널 발신
                elif '!logintok' in rcv_msg:  # 수신 메시지에 교사로그인확인 ok 헤더가 있으면
                    print('!logintok')
                    self.rcv_logintcheck_ok.emit()  # 로그인확인 교사로그인확인 ok 시그널 발신
                elif '!loginsok' in rcv_msg:  # 수신 메시지에 학생로그인확인 ok 헤더가 있으면
                    print('!loginsok')
                    self.rcv_loginscheck_ok.emit()  # 로그인확인 학생로그인확인 ok 시그널 발신
                elif '!logincheckno' in rcv_msg:  # 수신 메시지에 로그인확인 no 헤더가 있으면
                    print('!loginno')
                    self.rcv_logincheck_no.emit()  # 로그인확인 no 시그널 발신
        print('서버 연결 종료')  # 루프 종료시 연결 종료 디버그 메시지 출력
        s_skt.close()  # 서버 소켓 종료


if __name__ == "__main__":  # 이하 생략
    app = QApplication(sys.argv)
    myWindow = Main()
    myWindow.show()
    app.exec_()
