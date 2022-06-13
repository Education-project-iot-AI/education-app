# 범례
# join ~ : 회원 가입 관련
# login ~ : 로그인 관련
# quiz ~ : 문제 출제/풀기 관련
# qna ~ : qna 답변/질문 관련
# counsel ~ : 상담받기/신청 관련
# info ~ : 학생 통계 관련
# study ~ : 학습하기 관련

import sys
import requests
import random
from socket import *
from PyQt5 import uic, QtCore
# from PyQt5.QtGui import *  # 이하 모듈 계속 안 쓰면 삭제 예정
# from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from xml.etree.ElementTree import fromstring


clientui = uic.loadUiType("tonghap.ui")[0]


class Main(QMainWindow, clientui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.s_skt = socket(AF_INET, SOCK_STREAM)
        self.s_skt.connect(('127.0.0.1', 25001))
        self.stackedWidget.setCurrentIndex(0)
        # 메인 페이지
        self.btn_join.clicked.connect(self.join_start)
        self.btn_login.clicked.connect(self.login_start)
        self.radio_login_t.pressed.connect(self.login_btn)
        self.radio_login_s.pressed.connect(self.login_btn)
        # 회원 가입 페이지
        self.btn_join_backmain.clicked.connect(self.join_back_main)
        self.btn_join_id_check.clicked.connect(self.join_idcheck)
        self.btn_join_confirm.clicked.connect(self.join_confirm)
        self.radio_join_t.pressed.connect(self.join_btn)
        self.radio_join_s.pressed.connect(self.join_btn)
        self.line_join_id.textChanged.connect(self.join_btn2)
        # 교사 페이지
        self.btn_t_logout.clicked.connect(self.debug_logout)  # 디버그-로그아웃(돌아가기) 연결
        self.btn_t_quiz.clicked.connect(self.quiz_start_t)
        self.btn_t_qna.clicked.connect(self.qna_start_t)
        self.btn_t_counsel.clicked.connect(self.counsel_start_t)
        self.btn_t_info.clicked.connect(self.info_start)
        # 문제 출제 페이지
        self.btn_t_quiz_back.clicked.connect(self.quiz_back_t)
        self.btn_t_quiz_add.clicked.connect(self.quiz_add)
        self.btn_t_quiz_check.clicked.connect(self.quiz_check)
        # Q&A 답변 페이지
        self.btn_t_qna_back.clicked.connect(self.qna_back_t)
        self.btn_t_qna_check.clicked.connect(self.qna_check_t)
        self.btn_t_qna_solve.clicked.connect(self.qna_solve)
        self.combo_t_qna.currentIndexChanged.connect(self.qna_view_t)
        # 상담 수락 페이지
        self.btn_t_counsel_back.clicked.connect(self.counsel_back_t)
        self.btn_t_snd.clicked.connect(self.counsel_snd_t)
        self.btn_t_counsel_ok.clicked.connect(self.counsel_ok)
        # 통계보기 페이지
        self.btn_t_info_back.clicked.connect(self.info_back)
        self.btn_t_info_show.clicked.connect(self.info_show)
        # 학생 페이지
        self.btn_s_logout.clicked.connect(self.debug_logout)  # 디버그-로그아웃(돌아가기) 연결
        self.btn_s_quiz.clicked.connect(self.quiz_start_s)
        self.btn_s_qna.clicked.connect(self.qna_start_s)
        self.btn_s_counsel.clicked.connect(self.counsel_start_s)
        self.btn_s_study.clicked.connect(self.study_start)
        # 문제 풀기 페이지
        self.btn_s_quiz_back.clicked.connect(self.quiz_back_s)
        self.btn_s_quiz_list.clicked.connect(self.quiz_list)
        self.btn_s_quiz_solve.clicked.connect(self.quiz_solve)
        # Q&A 질문 페이지
        self.btn_s_qna_back.clicked.connect(self.qna_back_s)
        self.btn_s_qna_check.clicked.connect(self.qna_check_s)
        self.btn_s_qna_add.clicked.connect(self.qna_add)
        self.combo_s_qna.currentIndexChanged.connect(self.qna_view_s)
        # 상담 요청 페이지
        self.btn_s_counsel_back.clicked.connect(self.counsel_back_s)
        self.btn_s_snd.clicked.connect(self.counsel_snd_s)
        self.btn_s_counsel_call.clicked.connect(self.counsel_call)
        # 학습하기 페이지
        self.btn_s_study_back.clicked.connect(self.study_back)
        self.btn_s_study_on.clicked.connect(self.study_on)
        # 버튼/시그널 연결 끝
        self.btn_login.setDisabled(True)

    # def rcv_pageswap(self):  # 페이지 전환할 때 마다 0, 1 신호를 받아서 상담 신청 있는지 체크함 (상담 요청 수신 신호는 생략)
    #     rcv = self.s_skt.recv(1024)
    #     if rcv == '0':
    #         pass
    #     else:
    #         pass  # 상담 요청 있음을 알리는 함수 들어갈 자리

    # 디버그 시작
    def debug_logout(self):
        self.stackedWidget.setCurrentIndex(0)
    # 디버그 끝

    # 회원 가입 시작
    def join_start(self):  # 회원 가입 페이지 진입 함수
        self.s_skt.send('^join'.encode())
        self.stackedWidget.setCurrentIndex(1)
        self.btn_join_id_check.setDisabled(True)
        self.btn_join_confirm.setDisabled(True)
        self.radio_join_t.setAutoExclusive(False)
        self.radio_join_s.setAutoExclusive(False)
        self.radio_join_t.setChecked(False)
        self.radio_join_s.setChecked(False)
        self.radio_join_t.setAutoExclusive(True)
        self.radio_join_s.setAutoExclusive(True)
        self.line_join_id.clear()
        self.line_join_pw.clear()
        self.line_join_pw_check.clear()
        self.line_join_name.clear()

    def join_idcheck(self):  # 아이디 중복 체크 함수
        if not self.line_join_id.text():
            QMessageBox.warning(self, '입력 누락', 'ID를 입력하셔야 합니다')
        elif ' ' in self.line_join_id.text() or '/' in self.line_join_id.text()\
                or '|' in self.line_join_id.text() or '^' in self.line_join_id.text():
            QMessageBox.warning(self, '금지어 포함', '공백, /, |, ^는 사용할 수 없습니다')
            self.line_join_id.clear()
        else:
            self.s_skt.send(f'^idcheck/{self.line_join_id.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')  # 디버그-확인용 출력
                    break
            if rcv.decode() == '^ok':
                QMessageBox.about(self, '사용 가능 ID', '사용이 가능한 ID입니다')
                self.btn_join_confirm.setEnabled(True)
            else:
                QMessageBox.warning(self, '사용 불가 ID', '이미 사용 중인 ID입니다')
                self.line_join_id.clear()

    def join_confirm(self):  # 회원 가입 확정 함수
        if not self.line_join_id.text() or not self.line_join_pw.text() or not self.line_join_name.text():
            QMessageBox.warning(self, '입력 누락', '모든 정보를 입력해야 합니다')
        elif ' ' in self.line_join_id.text()\
                or '/' in self.line_join_id.text() or '|' in self.line_join_id.text()\
                or '^' in self.line_join_id.text() or ' ' in self.line_join_pw.text()\
                or '/' in self.line_join_pw.text()\
                or '|' in self.line_join_pw.text() or '^' in self.line_join_pw.text()\
                or ' ' in self.line_join_name.text()\
                or '/' in self.line_join_name.text() or '|' in self.line_join_name.text()\
                or '^' in self.line_join_name.text():
            QMessageBox.warning(self, '금지어 포함', '공백, /, |, ^는 사용할 수 없습니다')
            if ' ' in self.line_join_id.text() or '/' in self.line_join_id.text()\
                    or '|' in self.line_join_id.text() or '^' in self.line_join_id.text():
                self.line_join_id.clear()
            if ' ' in self.line_join_pw.text() or '/' in self.line_join_pw.text()\
                    or '|' in self.line_join_pw.text() or '^' in self.line_join_pw.text():
                self.line_join_pw.clear()
            if ' ' in self.line_join_name.text()\
                    or '/' in self.line_join_name.text() or '|' in self.line_join_name.text()\
                    or '^' in self.line_join_name.text():
                self.line_join_name.clear()
        elif self.line_join_pw.text() != self.line_join_pw_check.text():
            QMessageBox.warning(self, '비밀번호 불일치', '비밀번호를 다시 한번 확인해 주세요')
            if ' ' in self.line_join_id.text()\
                    or '/' in self.line_join_id.text() or '|' in self.line_join_id.text():
                self.line_join_id.clear()
            if ' ' in self.line_join_pw.text()\
                    or '/' in self.line_join_pw.text() or '|' in self.line_join_pw.text():
                self.line_join_pw.clear()
            if ' ' in self.line_join_name.text()\
                    or '/' in self.line_join_name.text() or '|' in self.line_join_name.text():
                self.line_join_name.clear()
        else:
            if self.radio_join_t.isChecked():
                self.s_skt.send(f'^joindata/{self.line_join_id.text()}/{self.line_join_pw.text()}'
                                f'/{self.line_join_name.text()}/t'.encode())
                QMessageBox.about(self, '회원 가입 완료', '회원 가입이 완료되었습니다')
            else:
                self.s_skt.send(f'^joindata/{self.line_join_id.text()}/{self.line_join_pw.text()}'
                                f'/{self.line_join_name.text()}/s'.encode())
                QMessageBox.about(self, '회원 가입 완료', '회원 가입이 완료되었습니다')
            self.btn_join_id_check.setDisabled(True)
            self.btn_join_confirm.setDisabled(True)
            self.radio_join_t.setAutoExclusive(False)
            self.radio_join_s.setAutoExclusive(False)
            self.radio_join_t.setChecked(False)
            self.radio_join_s.setChecked(False)
            self.radio_join_t.setAutoExclusive(True)
            self.radio_join_s.setAutoExclusive(True)
            self.line_join_id.clear()
            self.line_join_pw.clear()
            self.line_join_pw_check.clear()
            self.line_join_name.clear()

    def join_btn(self):  # 회원 가입 버튼 활성화 함수
        self.btn_join_id_check.setEnabled(True)

    def join_btn2(self):  # 회원 가입 버튼 비활성화 함수
        self.btn_join_confirm.setDisabled(True)

    def join_back_main(self):  # 회원 가입 페이지 나가기 함수
        self.s_skt.send('^Q_join'.encode())
        self.stackedWidget.setCurrentIndex(0)
        self.btn_login.setDisabled(True)
        self.radio_login_t.setAutoExclusive(False)
        self.radio_login_s.setAutoExclusive(False)
        self.radio_login_t.setChecked(False)
        self.radio_login_s.setChecked(False)
        self.radio_login_t.setAutoExclusive(True)
        self.radio_login_s.setAutoExclusive(True)
        self.line_login_id.clear()
        self.line_login_pw.clear()
    # 회원 가입 끝

    # 로그인 시작
    def login_start(self):  # 로그인 시작 함수
        if not self.line_login_id.text() or not self.line_login_pw.text():
            QMessageBox.warning(self, '입력 누락', 'ID와 PW를 모두 입력해야 합니다')
        elif ' ' in self.line_login_id.text()\
                or '/' in self.line_login_id.text() or '|' in self.line_login_id.text()\
                or '^' in self.line_login_id.text() or ' ' in self.line_login_pw.text()\
                or '/' in self.line_login_pw.text()\
                or '|' in self.line_login_pw.text() or '^' in self.line_login_pw.text():
            QMessageBox.warning(self, '금지어 포함', '공백, /, |, ^는 사용할 수 없습니다')
            if ' ' in self.line_login_id.text() or '/' in self.line_login_id.text()\
                    or '|' in self.line_login_id.text() or '^' in self.line_login_id.text():
                self.line_login_id.clear()
            if ' ' in self.line_login_pw.text() or '/' in self.line_login_pw.text()\
                    or '|' in self.line_login_pw.text() or '^' in self.line_login_pw.text():
                self.line_login_pw.clear()
        elif self.radio_login_t.isChecked():
            self.s_skt.send(f'^logint/{self.line_login_id.text()}/{self.line_login_pw.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')  # 디버그-확인용 출력
                    break
            if rcv.decode() == '^OK':
                QMessageBox.about(self, '로그인 성공', '로그인을 환영합니다')
                # self.rcv_pageswap()  # 페이지 전환 시 상담 요청 있는지 체크하는 함수
                self.btn_login.setDisabled(True)
                self.radio_login_t.setAutoExclusive(False)
                self.radio_login_s.setAutoExclusive(False)
                self.radio_login_t.setChecked(False)
                self.radio_login_s.setChecked(False)
                self.radio_login_t.setAutoExclusive(True)
                self.radio_login_s.setAutoExclusive(True)
                self.line_login_id.clear()
                self.line_login_pw.clear()
                self.stackedWidget.setCurrentIndex(2)
            else:
                QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해 주세요')
        else:
            self.s_skt.send(f'^logins/{self.line_login_id.text()}/{self.line_login_pw.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')  # 디버그-확인용 출력
                    break
            if rcv.decode() == '^NO':
                QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해 주세요')
                self.line_login_id.clear()
                self.line_login_pw.clear()
            else:
                QMessageBox.about(self, '로그인 성공', '로그인을 환영합니다')
                self.btn_login.setDisabled(True)
                self.radio_login_t.setAutoExclusive(False)
                self.radio_login_s.setAutoExclusive(False)
                self.radio_login_t.setChecked(False)
                self.radio_login_s.setChecked(False)
                self.radio_login_t.setAutoExclusive(True)
                self.radio_login_s.setAutoExclusive(True)
                self.line_login_id.clear()
                self.line_login_pw.clear()
                self.stackedWidget.setCurrentIndex(7)
                # self.study_list = rcv  # 수신한 학습 정보를 학습 내역 변수로 이동 (예정)

    def login_btn(self):  # 로그인 버튼 활성화 함수
        self.btn_login.setEnabled(True)
    # 로그인 끝

    # 문제 출제/풀기 시작
    def quiz_start_t(self):  # 문제 출제 페이지 진입 함수
        self.s_skt.send('^quiz'.encode())
        self.stackedWidget.setCurrentIndex(3)
        self.text_t_quiz.clear()
        self.line_quiz_add_q.clear()
        self.line_quiz_add_a.clear()

    def quiz_start_s(self):  # 문제 풀기 페이지 진입 함수
        self.s_skt.send('^quiz'.encode())
        self.stackedWidget.setCurrentIndex(8)
        self.text_s_quiz.clear()
        self.text_s_quized.clear()
        self.line_quiz_solve.clear()

    def quiz_add(self):  # 문제 출제 함수
        if not self.line_quiz_add_q.text() or not self.line_quiz_add_a.text():
            QMessageBox.warning(self, '입력 누락', '문제와 정답을 모두 입력해야 합니다')
        elif '^' in self.line_quiz_add_q.text()\
                or '/' in self.line_quiz_add_q.text() or '|' in self.line_quiz_add_q.text() \
                or '^' in self.line_quiz_add_a.text()\
                or '/' in self.line_quiz_add_a.text() or '|' in self.line_quiz_add_a.text():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
            if '^' in self.line_quiz_add_q.text()\
                    or '/' in self.line_quiz_add_q.text() or '|' in self.line_quiz_add_q.text():
                self.line_quiz_add_q.clear()
            if '^' in self.line_quiz_add_a.text()\
                    or '/' in self.line_lline_quiz_add_aogin_pw.text() or '|' in self.line_quiz_add_a.text():
                self.line_quiz_add_a.clear()
        else:
            self.s_skt.send(f'^quizadd/{self.line_quiz_add_q.text()}/{self.line_quiz_add_a.text()}'.encode())
            QMessageBox.about(self, '문제 등록', '문제가 등록되었습니다')
            self.line_quiz_add_q.clear()
            self.line_quiz_add_a.clear()

    def quiz_check(self):  # 전체 문제 보기 함수 (교사측)
        self.text_t_quiz.clear()
        self.s_skt.send('^quizcheck'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                print(f'받은 것 : {rcv.decode()}')
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 문제가 없습니다')
        else:
            rcvquiz = rcv.decode().split(' | ')
            for i in range(len(rcvquiz)):
                if i % 2 == 0:
                    self.text_t_quiz.append(f'문제 : {rcvquiz[i]}')
                else:
                    self.text_t_quiz.append(f'정답 : {rcvquiz[i]}')

    def quiz_list(self):  # 문제 받기 함수 (학생측)
        self.line_quiz_solve.clear()
        self.s_skt.send('^quizlist/'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                print(f'받은 것 : {rcv.decode()}')
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 문제가 없습니다')
        else:
            self.text_s_quiz.setPlainText(f'{rcv.decode()}')

    def quiz_solve(self):  # 문제 답변 함수
        if not self.line_quiz_solve.text():
            QMessageBox.warning(self, '입력 누락', '정답을 입력해야 합니다')
        elif '^' in self.line_quiz_solve.text()\
                or '/' in self.line_quiz_solve.text() or '|' in self.line_quiz_solve.text():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
            self.line_quiz_solve.clear()
        else:
            self.s_skt.send(f'^quizstart/{self.text_s_quiz.toPlainText()}/{self.line_quiz_solve.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(32)
                if sys.getsizeof(rcv) > 0:
                    print(f'받은 것 : {rcv.decode()}')
                    break
            if rcv.decode() == '^OK':
                QMessageBox.about(self, '결과', '정답입니다')
                self.text_s_quized.append(f'문제 : {self.text_s_quiz.toPlainText()}')
                self.text_s_quized.append(f'정답 : {self.line_quiz_solve.text()}')
                self.text_s_quiz.clear()
                self.line_quiz_solve.clear()
            else:
                QMessageBox.warning(self, '결과', '오답입니다')
                self.text_s_quized.append(f'문제 : {self.text_s_quiz.toPlainText()}')
                self.text_s_quized.append(f'오답 : {self.line_quiz_solve.text()}')
                self.line_quiz_solve.clear()

    def quiz_back_t(self):  # 문제 출제 페이지 나가기 함수
        self.s_skt.send('^quizend/'.encode())
        self.stackedWidget.setCurrentIndex(2)

    def quiz_back_s(self):  # 문제 풀기 페이지 나가기 함수
        self.s_skt.send('^quizend/'.encode())
        self.stackedWidget.setCurrentIndex(7)
    # 문제 출제/풀기 끝

    # Q&A 시작
    def qna_start_t(self):  # Q&A 답변하기 페이지 진입 함수
        self.stackedWidget.setCurrentIndex(4)
        self.combo_t_qna.clear()
        self.text_t_qna_check.clear()
        self.text_t_qna_add.clear()
        self.combo_t_qna.addItem('Q&A 질문|답변 목록')
        self.text_t_qna_add.setReadOnly(True)
        self.btn_t_qna_solve.setEnabled(False)

    def qna_start_s(self):  # Q&A 질문하기 페이지 진입 함수
        self.stackedWidget.setCurrentIndex(9)
        self.combo_s_qna.clear()
        self.text_s_qna_check.clear()
        self.text_s_qna_add.clear()
        self.combo_s_qna.addItem('Q&A 질문|답변 목록')

    def qna_check_t(self):  # Q&A 확인 함수 (교사측)
        self.combo_t_qna.clear()
        self.combo_t_qna.addItem('Q&A 질문|답변 목록')
        self.s_skt.send('^qnacheck'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                print(f'받은 것 : {rcv.decode()}')
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 Q&A가 없습니다')
        else:
            rcvqna = rcv.decode().split(' | ')
            for i in range(0, len(rcvqna), 2):
                if rcvqna[i + 1] != '^none':
                    self.combo_t_qna.addItem(f'<해결됨> {rcvqna[i]} | {rcvqna[i + 1]}')
                else:
                    self.combo_t_qna.addItem(f'<미해결> {rcvqna[i]} | 답변 없음')

    def qna_check_s(self):  # Q&A 확인 함수 (학생측)
        self.combo_s_qna.clear()
        self.combo_s_qna.addItem('Q&A 질문|답변 목록')
        self.s_skt.send('^qnacheck'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                print(f'받은 것 : {rcv.decode()}')
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 Q&A가 없습니다')
        else:
            rcvqna = rcv.decode().split(' | ')
            for i in range(0, len(rcvqna), 2):
                if rcvqna[i + 1] != '^none':
                    self.combo_s_qna.addItem(f'<해결됨> {rcvqna[i]} | {rcvqna[i + 1]}')
                else:
                    self.combo_s_qna.addItem(f'<미해결> {rcvqna[i]} | 답변 없음')

    def qna_view_t(self):  # Q&A 목록 선택 시 표시 함수 (교사측)
        if self.combo_t_qna.currentText()[:5] == '<해결됨>':
            self.text_t_qna_check.clear()
            qvt = self.combo_t_qna.currentText().split(' | ')
            self.text_t_qna_check.append(f'질문 / {qvt[0].replace("<해결됨> ", "")}')
            self.text_t_qna_check.append(f'답변 / {qvt[1]}')
            self.text_t_qna_add.clear()
            self.text_t_qna_add.append('이미 답변이 등록된 질문입니다')
            self.text_t_qna_add.setReadOnly(True)
            self.btn_t_qna_solve.setDisabled(True)
        elif self.combo_t_qna.currentText()[:5] == '<미해결>':
            self.text_t_qna_check.clear()
            qvt = self.combo_t_qna.currentText().split(' | ')
            self.text_t_qna_check.append(f'질문 / {qvt[0].replace("<미해결> ", "")}')
            self.text_t_qna_add.clear()
            self.text_t_qna_add.setReadOnly(False)
            self.btn_t_qna_solve.setEnabled(True)

    def qna_view_s(self):  # Q&A 목록 선택 시 표시 함수 (학생측)
        if self.combo_s_qna.currentText()[:5] == '<해결됨>':
            self.text_s_qna_check.clear()
            qvt = self.combo_s_qna.currentText().split(' | ')
            self.text_s_qna_check.append(f'질문 / {qvt[0].replace("<해결됨> ", "")}')
            self.text_s_qna_check.append(f'답변 / {qvt[1]}')
        elif self.combo_s_qna.currentText()[:5] == '<미해결>':
            self.text_s_qna_check.clear()
            qvt = self.combo_s_qna.currentText().split(' | ')
            self.text_s_qna_check.append(f'질문 / {qvt[0].replace("<미해결> ", "")}')

    def qna_solve(self):  # Q&A 답변하기 함수
        if not self.text_t_qna_add.toPlainText():
            QMessageBox.warning(self, '입력 누락', '답변을 입력해야 합니다')
        elif '^' in self.text_t_qna_add.toPlainText() \
                or '/' in self.text_t_qna_add.toPlainText() or '|' in self.text_t_qna_add.toPlainText():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
        else:
            self.s_skt.send(f'^aadd/{self.text_t_qna_check.toPlainText().replace("질문 / ", "")}'
                            f'/{self.text_t_qna_add.toPlainText()}'.encode())
            qsi = self.combo_t_qna.currentIndex()
            qst = self.combo_t_qna.currentText().split(' | ')
            qsa = self.text_t_qna_add.toPlainText()
            self.combo_t_qna.removeItem(qsi)
            self.combo_t_qna.insertItem(qsi, f'<해결됨> {qst[0].replace("<미해결> ", "")} | {qsa}')
            self.combo_t_qna.setCurrentIndex(qsi)
            self.text_t_qna_add.clear()

    def qna_add(self):  # Q&A 질문하기
        if not self.text_s_qna_add.toPlainText():
            QMessageBox.warning(self, '입력 누락', '질문을 입력해야 합니다')
        elif '^' in self.text_s_qna_add.toPlainText() \
                or '/' in self.text_s_qna_add.toPlainText() or '|' in self.text_s_qna_add.toPlainText():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
        else:
            self.s_skt.send(f'^qadd/{self.text_s_qna_add.toPlainText()}/^none'.encode())
            self.text_s_qna_add.clear()

    def qna_back_t(self):  # Q&A 페이지 나가기 함수 (교사측)
        self.stackedWidget.setCurrentIndex(2)

    def qna_back_s(self):  # Q&A 페이지 나가기 함수 (학생측)
        self.stackedWidget.setCurrentIndex(7)
    # Q&A 끝

    # 상담 받기/신청 시작
    def counsel_start_t(self):  # 상담 받기 페이지 진입 함수
        self.stackedWidget.setCurrentIndex(5)

    def counsel_start_s(self):  # 상담 신청 페이지 진입 함수
        self.stackedWidget.setCurrentIndex(10)

    def counsel_ok(self):  # 상담 받기 함수
        pass

    def counsel_call(self):  # 상담 요청 함수
        pass

    def counsel_snd_t(self):  # 상담 대화 전송 함수 (교사측)
        pass

    def counsel_snd_s(self):  # 상담 대화 전송 함수 (학생측)
        pass

    def counsel_back_t(self):  # 상담 받기 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(2)

    def counsel_back_s(self):  # 상담 신청 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(7)
    # 상담 받기/신청 끝

    # 통계 보기 시작
    def info_start(self):  # 통계 보기 페이지 진입 함수
        self.stackedWidget.setCurrentIndex(6)

    def info_show(self):  # 통계 보기 함수
        pass

    def info_back(self):  # 통계 보기 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(2)
    # 통계 보기 끝

    # 학습하기 시작
    def study_start(self):  # 학습하기 페이지 진입 함수
        self.text_study_name.clear()
        self.text_study_info.clear()
        self.stackedWidget.setCurrentIndex(11)

    def study_on(self):  # 학습하기 함수
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
                        'A000001390', 'A000001391', 'A000001393', 'A000001394', 'A000001395', 'A000001397']
        code = random.choice(birdcodelist)
        params = {'serviceKey': '9cCN4TXQK/nLX/tkVrz9+4qnPHIyI5sjjCpkfO9kPAH8y6fDcWtxwsp7JM0bozPvZklvvCVKqnZOig81BIMjmw==', 'q1': code}
        bird_data = fromstring(requests.get('http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo', params=params).content.decode())
        self.text_study_name.setPlainText(bird_data[1][0][6].text)
        self.text_study_info.setPlainText(bird_data[1][0][16].text)

    def study_back(self):  # 학습하기 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(7)
    # 학습하기 끝


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Main()
    myWindow.show()
    app.exec_()
