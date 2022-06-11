import sys
import requests
import random
from socket import *
from PyQt5 import uic, QtCore
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *  # 계속 안 쓰면 삭제 예정
from PyQt5.QtWidgets import *
from xml.etree.ElementTree import fromstring


clientui = uic.loadUiType("tonghap.ui")[0]  # ui 불러오기


class Main(QMainWindow, clientui):  # 메인 클래스
    def __init__(self):  # 이니셜라이저
        super().__init__()  # 상속
        self.setupUi(self)  # ui 로딩
        self.s_skt = socket(AF_INET, SOCK_STREAM)
        self.s_skt.connect(('127.0.0.1', 25000))  # 서버 소켓 커넥트
        self.stackedWidget.setCurrentIndex(0)  # 초기 페이지 설정
        # 메인 페이지
        self.btn_join.clicked.connect(self.join_start)  # 회원 가입 버튼 연결
        self.btn_login.clicked.connect(self.login_start)  # 로그인 버튼 연결
        self.radio_login_t.pressed.connect(lambda: self.btn_login.setEnabled(True))
        self.radio_login_s.pressed.connect(lambda: self.btn_login.setEnabled(True))
        # 회원 가입 페이지
        self.btn_join_backmain.clicked.connect(self.join_back_main)  # 돌아가기 연결
        self.btn_join_id_check.clicked.connect(self.join_idcheck)  # ID 중복 체크 연결
        self.btn_join_confirm.clicked.connect(self.join_confirm)  # 회원 가입 연결
        self.radio_join_t.pressed.connect(lambda: self.btn_join_id_check.setEnabled(True))
        self.radio_join_s.pressed.connect(lambda: self.btn_join_id_check.setEnabled(True))
        self.line_join_id.textChanged.connect(lambda: self.btn_join_confirm.setDisabled(True))
        # 교사 페이지
        self.btn_t_logout.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))  # 디버그-로그아웃(돌아가기) 연결
        # 학생 페이지
        self.btn_s_logout.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))  # 디버그-로그아웃(돌아가기) 연결
        self.btn_s_study.clicked.connect(self.student_study_start)  # 학습하기 연결
        # 학습하기 페이지
        self.btn_s_study_back.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))  # 돌아가기 연결
        self.btn_s_study_on.clicked.connect(self.student_study)  # 학습 자료 보기 연결
        # 버튼/시그널 연결 끝
        self.btn_login.setDisabled(True)

    # def rcv_pageswap(self):  # 페이지 전환할 때 마다 0, 1 신호를 받아서 상담 신청 있는지 체크함 (상담 요청 수신 신호는 생략)
    #     rcv = self.s_skt.recv(1024)
    #     if rcv == '0':
    #         pass
    #     else:
    #         pass  # 상담 요청 있음을 알리는 함수 들어갈 자리

    def join_start(self):  # 회원 가입 - 페이지 초기화 함수
        self.s_skt.send('!join'.encode())  # 서버로 송신
        self.stackedWidget.setCurrentIndex(1)  # 회원 가입 페이지로 전환
        self.btn_join_id_check.setDisabled(True)  # ID 중복 확인 버튼 비활성화
        self.btn_join_confirm.setDisabled(True)  # 회원 가입 버튼 비활성화
        self.radio_join_t.setAutoExclusive(False)  # 이하 회원 속성 라디오 버튼 초기화
        self.radio_join_s.setAutoExclusive(False)
        self.radio_join_t.setChecked(False)
        self.radio_join_s.setChecked(False)
        self.radio_join_t.setAutoExclusive(True)
        self.radio_join_s.setAutoExclusive(True)
        self.line_join_id.clear()  # 회원 가입 페이지의 라인 초기화
        self.line_join_pw.clear()
        self.line_join_pw_check.clear()
        self.line_join_name.clear()

    def join_idcheck(self):  # 회원 가입 - 아이디 중복 체크 함수
        idt = self.line_join_id.text()
        if not idt:  # ID 란이 비었으면
            QMessageBox.warning(self, 'ID 입력', 'ID를 입력하셔야 합니다')  # 경고 메시지 출력
            self.line_join_id.clear()  # ID 란 초기화
        elif ' ' in idt or '?' in idt or '/' in idt or '|' in idt:  # 금지어가 포함되어 있으면
            QMessageBox.warning(self, '금지어 포함', '공백, !, /, |, ^는 사용할 수 없습니다')
            self.line_join_id.clear()
        else:  # ID가 존재하고 금지어도 포함되어 있지 않으면
            self.s_skt.send(f'!idcheck/{self.line_join_id.text()}'.encode())  # 서버로 송신
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')  # 디버그-확인용 출력
                    break
            if rcv.decode() == '!ok':
                QMessageBox.about(self, '사용 가능 ID', '사용이 가능한 ID입니다')  # 알림 메시지 출력
                self.btn_join_confirm.setEnabled(True)
            else:
                QMessageBox.warning(self, '사용 불가 ID', '이미 사용 중인 ID입니다')  # 경고 메시지 출력
                self.line_join_id.clear()

    def join_confirm(self):  # 회원 가입 - 회원 가입 확정 함수
        idt = self.line_join_id.text()
        pwt = self.line_join_pw.text()
        pct = self.line_join_pw_check.text()
        nmt = self.line_join_name.text()
        if not idt or not pwt or not nmt:  # 입력란이 비었으면
            QMessageBox.warning(self, '입력 누락', '모든 정보를 입력해야 합니다')  # 경고 메시지 출력
        elif ' ' in idt or '?' in idt or '/' in idt or '|' in idt\
                or ' ' in pwt or '?' in pwt or '/' in pwt or '|' in pwt\
                or ' ' in nmt or '?' in nmt or '/' in nmt or '|' in nmt:
            QMessageBox.warning(self, '금지어 포함', '공백, !, /, |, ^는 사용할 수 없습니다')  # 경고 메시지 출력
            if ' ' in idt or '?' in idt or '/' in idt or '|' in idt:
                self.line_join_id.clear()
            if ' ' in pwt or '?' in pwt or '/' in pwt or '|' in pwt:
                self.line_join_pw.clear()
            if ' ' in nmt or '?' in nmt or '/' in nmt or '|' in nmt:
                self.line_join_name.clear()
        elif pwt != pct:  # 비밀번호와 비밀번호 확인이 일치하지 않으면
            QMessageBox.warning(self, '비밀번호 불일치', '비밀번호를 다시 한번 확인해 주세요')  # 경고 메시지 출력
            if ' ' in idt or '?' in idt or '/' in idt or '|' in idt:
                self.line_join_id.clear()
            if ' ' in pwt or '?' in pwt or '/' in pwt or '|' in pwt:
                self.line_join_pw.clear()
            if ' ' in nmt or '?' in nmt or '/' in nmt or '|' in nmt:
                self.line_join_name.clear()
        else:  # 금지어도 없고 비밀번호 확인도 일치하면
            if self.radio_join_t.isChecked():  # 교사 회원이 체크되어 있을 때
                self.s_skt.send(f'!joindata/{idt}/{pwt}/{nmt}/t'.encode())  # 송신
                QMessageBox.about(self, '회원 가입 완료', '회원 가입이 완료되었습니다')  # 완료 메시지 출력
            else:  # 학생 회원이 체크되어 있을 때
                self.s_skt.send(f'!joindata/{idt}/{pwt}/{nmt}/s'.encode())
                QMessageBox.about(self, '회원 가입 완료', '회원 가입이 완료되었습니다')
            self.btn_join_id_check.setDisabled(True)  # ID 중복 확인 버튼 비활성화
            self.btn_join_confirm.setDisabled(True)  # 회원 가입 버튼 비활성화
            self.radio_join_t.setAutoExclusive(False)  # 이하 회원 속성 라디오 버튼 초기화
            self.radio_join_s.setAutoExclusive(False)
            self.radio_join_t.setChecked(False)
            self.radio_join_s.setChecked(False)
            self.radio_join_t.setAutoExclusive(True)
            self.radio_join_s.setAutoExclusive(True)
            self.line_join_id.clear()
            self.line_join_pw.clear()
            self.line_join_pw_check.clear()
            self.line_join_name.clear()

    def join_back_main(self):
        self.s_skt.send('!Q_join'.encode())  # 회원 가입 창을 나갈 때 !Q_join 전송할 것
        self.stackedWidget.setCurrentIndex(0)
        self.btn_login.setDisabled(True)
        self.radio_login_t.setAutoExclusive(False)  # 이하 회원 속성 라디오 버튼 초기화
        self.radio_login_s.setAutoExclusive(False)
        self.radio_login_t.setChecked(False)
        self.radio_login_s.setChecked(False)
        self.radio_login_t.setAutoExclusive(True)
        self.radio_login_s.setAutoExclusive(True)
        self.line_login_id.clear()  # 메인 페이지의 라인 초기화
        self.line_login_pw.clear()

    def login_start(self):
        lid = self.line_login_id.text()
        lpw = self.line_login_pw.text()
        if ' ' in lid or '?' in lid or '/' in lid or '|' in lid\
                or ' ' in lpw or '?' in lpw or '/' in lpw or '|' in lpw:
            QMessageBox.warning(self, '금지어 포함', '공백, !, /, |, ^는 사용할 수 없습니다')  # 경고 메시지 출력
            if ' ' in lid or '?' in lid or '/' in lid or '|' in lid:
                self.line_login_id.clear()
            if ' ' in lpw or '?' in lpw or '/' in lpw or '|' in lpw:
                self.line_login_pw.clear()
        elif self.radio_login_t.isChecked():  # 교사 회원이 체크되어 있을 때
            self.s_skt.send(f'!logint/{lid}/{lpw}'.encode())  # 송신
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')  # 디버그-확인용 출력
                    break
            if rcv.decode() == '!OK':
                QMessageBox.about(self, '로그인 성공', '로그인을 환영합니다')
                # self.rcv_pageswap()  # 페이지 전환 시 상담 요청 있는지 체크하는 함수
                self.stackedWidget.setCurrentIndex(2)
            else:
                QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해 주세요')
        elif self.radio_login_s.isChecked():  # 학생 회원이 체크되어 있을 때
            self.s_skt.send(f'!logins/{lid}/{lpw}'.encode())
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')  # 디버그-확인용 출력
                    break
            if rcv.decode() == '!NO':
                QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해 주세요')
                self.line_login_id.clear()
                self.line_login_pw.clear()
            else:
                QMessageBox.about(self, '로그인 성공', '로그인을 환영합니다')
                self.stackedWidget.setCurrentIndex(3)
                # self.study_list = rcv  # 수신한 학습 정보를 학습 내역 변수로 이동 (예정)
        else:
            QMessageBox.warning(self, '로그인 오류', '회원 종류를 반드시 선택해 주세요')

    # 이하 임시 땜빵

    def student_study_start(self):  # 학습하기 페이지 초기 함수
        self.text_study_name.clear()  # 이름란 초기화
        self.text_study_info.clear()  # 정보란 초기화
        self.stackedWidget.setCurrentIndex(4)  # 학습하기 페이지로 전환

    def student_study(self):  # 학습하기 함수
        birdcodelist = ['A000001149', 'A000001150', 'A000001151', 'A000001152', 'A000001153', 'A000001154',
                        'A000001155', 'A000001156', 'A000001160', 'A000001161', 'A000001162', 'A000001164',
                        'A000001165', 'A000001166', 'A000001167', 'A000001168', 'A000001169', 'A000001170',
                        'A000001171', 'A000001172', 'A000001176', 'A000001177', 'A000001178', 'A000001180',
                        'A000001181', 'A000001182', 'A000001183', 'A000001184', 'A000001185', 'A000001188',
                        'A000001189', 'A000001191', 'A000001195', 'A000001197', 'A000001199', 'A000001201',
                        'A000001204', 'A000001205', 'A000001206', 'A000001207', 'A000001209', 'A000001210',
                        'A000001211', 'A000001213', 'A000001216', 'A000001218', 'A000001220', 'A000001221',
                        'A000001222', 'A000001223', 'A000001224', 'A000001225', 'A000001226', 'A000001227',
                        'A000001228', 'A000001229', 'A000001231', 'A000001233', 'A000001235', 'A000001236',
                        'A000001239', 'A000001241', 'A000001243', 'A000001246', 'A000001248', 'A000001250',
                        'A000001251', 'A000001253', 'A000001254', 'A000001255', 'A000001256', 'A000001257',
                        'A000001259', 'A000001260', 'A000001261', 'A000001264', 'A000001265', 'A000001266',
                        'A000001267', 'A000001270', 'A000001271', 'A000001273', 'A000001275', 'A000001279',
                        'A000001280', 'A000001282', 'A000001285', 'A000001287', 'A000001291', 'A000001292',
                        'A000001295', 'A000001299', 'A000001304', 'A000001305', 'A000001306', 'A000001307',
                        'A000001308', 'A000001309', 'A000001310', 'A000001311', 'A000001313', 'A000001316',
                        'A000001317', 'A000001318', 'A000001319', 'A000001320', 'A000001324', 'A000001326',
                        'A000001327', 'A000001328', 'A000001329', 'A000001330', 'A000001333', 'A000001334',
                        'A000001336', 'A000001337', 'A000001338', 'A000001340', 'A000001341', 'A000001344',
                        'A000001347', 'A000001354', 'A000001355', 'A000001357', 'A000001358', 'A000001360',
                        'A000001361', 'A000001362', 'A000001365', 'A000001366', 'A000001367', 'A000001368',
                        'A000001369', 'A000001370', 'A000001371', 'A000001372', 'A000001374', 'A000001376',
                        'A000001377', 'A000001383', 'A000001384', 'A000001386', 'A000001387', 'A000001388',
                        'A000001390', 'A000001391', 'A000001393', 'A000001394', 'A000001395', 'A000001397']  # 학습 & 출제 대상 코드 리스트 (변경 or 삭제 예정)
        code = random.choice(birdcodelist)  # 학습 & 출제 대상 코드 리스트에서 랜덤 추출
        params = {'serviceKey': '9cCN4TXQK/nLX/tkVrz9+4qnPHIyI5sjjCpkfO9kPAH8y6fDcWtxwsp7JM0bozPvZklvvCVKqnZOig81BIMjmw==', 'q1': code}  # 패러미터에 입력
        bird_data = fromstring(requests.get('http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo', params=params).content.decode())  # 조류 정보 API에서 획득
        self.text_study_name.clear()  # 이름란 초기화
        self.text_study_info.clear()  # 정보란 초기화
        self.text_study_name.append(bird_data[1][0][6].text)  # 이름란 이름 표시
        self.text_study_info.append(bird_data[1][0][16].text)  # 정보란 정보 표시


if __name__ == "__main__":  # 이하 생략
    app = QApplication(sys.argv)
    myWindow = Main()
    myWindow.show()
    app.exec_()
