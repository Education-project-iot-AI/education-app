import re
import sys
import requests
import random
import sqlite3
from socket import *
from threading import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from xml.etree.ElementTree import fromstring
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


clientui = uic.loadUiType("tonghap.ui")[0]


class Main(QMainWindow, clientui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.s_skt = socket(AF_INET, SOCK_STREAM)
        self.s_skt.connect(('127.0.0.1', 25000))
        self.stackedWidget.setCurrentIndex(0)
        self.flag_t = True
        self.flag_s = True
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
        self.btn_t_logout.clicked.connect(self.logout)
        self.btn_t_quiz.clicked.connect(self.quiz_start_t)
        self.btn_t_qna.clicked.connect(self.qna_start_t)
        self.btn_t_counsel.clicked.connect(self.counsel_start_t)
        self.btn_t_info.clicked.connect(self.info_start)
        # 문제 출제 페이지
        self.btn_t_quiz_back.clicked.connect(self.quiz_back_t)
        self.btn_t_quiz_add.clicked.connect(self.quiz_add)
        self.btn_t_quiz_check.clicked.connect(self.quiz_check)
        self.line_quiz_add_n.setValidator(QIntValidator(1, 100, self))
        # Q&A 답변 페이지
        self.btn_t_qna_back.clicked.connect(self.qna_back_t)
        self.btn_t_qna_check.clicked.connect(self.qna_check_t)
        self.btn_t_qna_solve.clicked.connect(self.qna_solve)
        self.combo_t_qna.currentIndexChanged.connect(self.qna_view_t)
        # 상담 수락 페이지
        self.btn_t_counsel_back.clicked.connect(self.counsel_back_t)
        self.btn_t_snd.clicked.connect(self.counsel_snd_t)
        self.btn_t_end.clicked.connect(self.counsel_end_t)
        self.btn_t_counsel_ok.clicked.connect(self.counsel_go_t)
        # 통계보기 페이지
        self.btn_t_info_back.clicked.connect(self.info_back)
        self.btn_t_info_show_1.clicked.connect(self.info_show_1)
        self.btn_t_info_show_2.clicked.connect(self.info_show_2)
        # 학생 페이지
        self.btn_s_logout.clicked.connect(self.logout)
        self.btn_s_quiz.clicked.connect(self.quiz_start_s)
        self.btn_s_qna.clicked.connect(self.qna_start_s)
        self.btn_s_counsel.clicked.connect(self.counsel_start_s)
        self.btn_s_study.clicked.connect(self.study_start)
        # 문제 풀기 페이지
        self.btn_s_quiz_back.clicked.connect(self.quiz_back_s)
        self.btn_s_quiz_list.clicked.connect(self.quiz_list)
        self.btn_s_quiz_solve.clicked.connect(self.quiz_solve)
        self.btn_s_quiz_point.clicked.connect(self.info_myself)  # 하나만 명명 규칙 예외
        # Q&A 질문 페이지
        self.btn_s_qna_back.clicked.connect(self.qna_back_s)
        self.btn_s_qna_check.clicked.connect(self.qna_check_s)
        self.btn_s_qna_add.clicked.connect(self.qna_add)
        self.combo_s_qna.currentIndexChanged.connect(self.qna_view_s)
        # 상담 요청 페이지
        self.btn_s_counsel_back.clicked.connect(self.counsel_back_s)
        self.btn_s_snd.clicked.connect(self.counsel_snd_s)
        self.btn_s_end.clicked.connect(self.counsel_end_s)
        self.btn_s_counsel_call.clicked.connect(self.counsel_go_s)
        # 학습하기 페이지
        self.btn_s_study_back.clicked.connect(self.study_back)
        self.btn_s_study_on.clicked.connect(self.study_on)
        # 버튼/시그널 연결 끝
        self.btn_login.setDisabled(True)
        self.birdcodelist = []
        self.study_list = []
        # matplotlib 설정 시작
        self.nationColor = ['red', 'green', 'yellow', 'blue']
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.gridLayout.addWidget(self.canvas)
        self.ax = self.fig.add_subplot()
        # matplotlib 설정 끝

    def logout(self):
        self.stackedWidget.setCurrentIndex(0)

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
        join_id = re.sub('[a-zA-Z_!\\d]', '', self.line_join_id.text())
        if not self.line_join_id.text():
            QMessageBox.warning(self, '입력 누락', 'ID를 입력하셔야 합니다')
        elif join_id:
            QMessageBox.warning(self, '금지어 포함', '공백을 제외한 영문 대소문자, 숫자, _, !만 사용할 수 있습니다')
            self.line_join_id.clear()
        else:
            self.s_skt.send(f'^idcheck/{self.line_join_id.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    break
            if rcv.decode() == '^ok':
                QMessageBox.about(self, '사용 가능 ID', '사용이 가능한 ID입니다')
                self.btn_join_confirm.setEnabled(True)
            else:
                QMessageBox.warning(self, '사용 불가 ID', '이미 사용 중인 ID입니다')
                self.line_join_id.clear()

    def join_confirm(self):  # 회원 가입 확정 함수
        join_id = re.sub('[a-zA-Z_!\\d]', '', self.line_join_id.text())
        join_pw = re.sub('[a-zA-Z_!\\d]', '', self.line_join_pw.text())
        join_nm = re.sub('[a-zA-Z_!\\d]', '', self.line_join_name.text())
        if not self.line_join_id.text() or not self.line_join_pw.text() or not self.line_join_name.text():
            QMessageBox.warning(self, '입력 누락', '모든 정보를 입력해야 합니다')
        elif join_id or join_pw or join_nm:
            QMessageBox.warning(self, '금지어 포함', '공백을 제외한 영문 대소문자, 숫자, _, !만 사용할 수 있습니다')
            if join_id:
                self.line_join_id.clear()
            if join_pw:
                self.line_join_pw.clear()
            if join_nm:
                self.line_join_name.clear()
        elif self.line_join_pw.text() != self.line_join_pw_check.text():
            QMessageBox.warning(self, '비밀번호 불일치', '비밀번호를 다시 한번 확인해 주세요')
            if join_id:
                self.line_join_id.clear()
            if join_pw:
                self.line_join_pw.clear()
            if join_nm:
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
        login_id = re.sub('[a-zA-Z_!\\d]', '', self.line_login_id.text())
        login_pw = re.sub('[a-zA-Z_!\\d]', '', self.line_login_pw.text())
        if not self.line_login_id.text() or not self.line_login_pw.text():
            QMessageBox.warning(self, '입력 누락', 'ID와 PW를 모두 입력해야 합니다')
        elif login_id or login_pw:
            QMessageBox.warning(self, '금지어 포함', '공백을 제외한 영문 대소문자, 숫자, _, !만 사용할 수 있습니다')
            if login_id:
                self.line_login_id.clear()
            if login_pw:
                self.line_login_pw.clear()
        elif self.radio_login_t.isChecked():
            self.s_skt.send(f'^logint/{self.line_login_id.text()}/{self.line_login_pw.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(16)
                if sys.getsizeof(rcv) > 0:
                    break
            if rcv.decode() == '^OK':
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
                self.stackedWidget.setCurrentIndex(2)
            else:
                QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해 주세요')
        else:
            self.s_skt.send(f'^logins/{self.line_login_id.text()}/{self.line_login_pw.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(1024)
                if sys.getsizeof(rcv) > 0:
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
                if rcv.decode() == 'X':
                    pass
                else:
                    self.study_list = rcv.decode()[4:].split('|')

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
        self.list_s_quiz.clear()
        self.line_quiz_solve.clear()

    def quiz_add(self):  # 문제 출제 함수
        if not self.line_quiz_add_q.text() or not self.line_quiz_add_a.text() or not self.line_quiz_add_n.text():
            QMessageBox.warning(self, '입력 누락', '문제와 정답과 점수를 모두 입력해야 합니다')
        elif '^' in self.line_quiz_add_q.text() or '/' in self.line_quiz_add_q.text()\
                or '|' in self.line_quiz_add_q.text() or '^' in self.line_quiz_add_a.text()\
                or '/' in self.line_quiz_add_a.text() or '|' in self.line_quiz_add_a.text():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
            if '^' in self.line_quiz_add_q.text()\
                    or '/' in self.line_quiz_add_q.text() or '|' in self.line_quiz_add_q.text():
                self.line_quiz_add_q.clear()
            if '^' in self.line_quiz_add_a.text()\
                    or '/' in self.line_lline_quiz_add_aogin_pw.text() or '|' in self.line_quiz_add_a.text():
                self.line_quiz_add_a.clear()
        elif int(self.line_quiz_add_n.text()) > 100:
            QMessageBox.warning(self, '범위 초과', '점수는 100 이하의 정수여야 합니다')
            self.line_quiz_add_n.clear()
        else:
            self.s_skt.send(f'^quizadd/{self.line_quiz_add_q.text()}/'
                            f'{self.line_quiz_add_a.text()}/{self.line_quiz_add_n.text()}'.encode())
            QMessageBox.about(self, '문제 등록', '문제가 등록되었습니다')
            self.line_quiz_add_q.clear()
            self.line_quiz_add_a.clear()
            self.line_quiz_add_n.clear()

    def quiz_check(self):  # 전체 문제 보기 함수 (교사측)
        self.text_t_quiz.clear()
        self.s_skt.send('^quizcheck'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 문제가 없습니다')
        else:
            rcvquiz = rcv.decode()[:-2].split(' | ')
            for i in rcvquiz:
                quiz = i.split('^')
                self.text_t_quiz.append(f'문제 : {quiz[0]}')
                self.text_t_quiz.append(f'정답 : {quiz[1]}')

    def quiz_list(self):  # 문제 받기 함수 (학생측)
        self.list_s_quiz.clear()
        self.line_quiz_solve.clear()
        self.s_skt.send('^quizcheck'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 문제가 없습니다')
        else:
            rcvquiz = rcv.decode()[:-2].split(' | ')
            for i in rcvquiz:
                quiz = i.split('^')
                self.list_s_quiz.addItem(f'문제 : {quiz[0]}')

    def quiz_solve(self):  # 문제 답변 함수
        if not self.line_quiz_solve.text():
            QMessageBox.warning(self, '입력 누락', '정답을 입력해야 합니다')
        elif '^' in self.line_quiz_solve.text()\
                or '/' in self.line_quiz_solve.text() or '|' in self.line_quiz_solve.text():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
            self.line_quiz_solve.clear()
        else:
            self.s_skt.send(f'^quizstart/{self.list_s_quiz.currentItem().text()[5:]}/'
                            f'{self.line_quiz_solve.text()}'.encode())
            while True:
                rcv = self.s_skt.recv(1024)
                if sys.getsizeof(rcv) > 0:
                    break
            if rcv.decode() == '^OK':
                QMessageBox.about(self, '결과', '정답입니다')
                self.line_quiz_solve.clear()
            elif rcv.decode() == '^none':
                QMessageBox.about(self, '결과', '이미 풀었던 문제입니다')
                self.line_quiz_solve.clear()
            else:
                QMessageBox.warning(self, '결과', '오답입니다')
                self.line_quiz_solve.clear()

    def quiz_back_t(self):  # 문제 출제 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(2)

    def quiz_back_s(self):  # 문제 풀기 페이지 나가기 함수
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
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 Q&A가 없습니다')
        else:
            QMessageBox.about(self, 'Q&A 갱신', 'Q&A 목록이 갱신되었습니다')
            rcvqna = rcv.decode().split('/')
            for i in rcvqna:
                if i.split(',')[2] != '답변 대기중':
                    self.combo_t_qna.addItem(f'<해결됨> {i.split(",")[1]} | {i.split(",")[2]}')
                else:
                    self.combo_t_qna.addItem(f'<미해결> {i.split(",")[1]} | 답변 없음')

    def qna_check_s(self):  # Q&A 확인 함수 (학생측)
        self.combo_s_qna.clear()
        self.combo_s_qna.addItem('Q&A 질문|답변 목록')
        self.s_skt.send('^qnacheck'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        if rcv.decode() == '^none':
            QMessageBox.warning(self, '자료 없음', '등록된 Q&A가 없습니다')
        else:
            QMessageBox.about(self, 'Q&A 갱신', 'Q&A 목록이 갱신되었습니다')
            rcvqna = rcv.decode().split('/')
            for i in rcvqna:
                if i.split(',')[2] != '답변 대기중':
                    self.combo_s_qna.addItem(f'<해결됨> {i.split(",")[1]} | {i.split(",")[2]}')
                else:
                    self.combo_s_qna.addItem(f'<미해결> {i.split(",")[1]} | 답변 없음')

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
        elif '^' in self.text_t_qna_add.toPlainText() or '/' in self.text_t_qna_add.toPlainText()\
                or '|' in self.text_t_qna_add.toPlainText():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
        else:
            self.s_skt.send(f'^qnaaadd/{self.text_t_qna_check.toPlainText().replace("질문 / ", "")}'
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
        elif '^' in self.text_s_qna_add.toPlainText() or '/' in self.text_s_qna_add.toPlainText()\
                or '|' in self.text_s_qna_add.toPlainText():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
        else:
            self.s_skt.send(f'^qnaqadd/{self.text_s_qna_add.toPlainText()}'.encode())
            self.text_s_qna_add.clear()

    def qna_back_t(self):  # Q&A 페이지 나가기 함수 (교사측)
        self.stackedWidget.setCurrentIndex(2)

    def qna_back_s(self):  # Q&A 페이지 나가기 함수 (학생측)
        self.stackedWidget.setCurrentIndex(7)
    # Q&A 끝

    # 상담 받기/신청 시작
    def counsel_start_t(self):  # 상담 받기 페이지 진입 함수
        self.stackedWidget_t.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(5)

    def counsel_start_s(self):  # 상담 신청 페이지 진입 함수
        self.stackedWidget_s.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(10)

    def counsel_go_t(self):  # 상담 시작 함수 (교사측)
        self.s_skt.send('^counsel'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        if rcv.decode() == '^NO':
            QMessageBox.warning(self, '상담방', '다른 선생님이 상담하고 있습니다')
        else:
            self.stackedWidget_t.setCurrentIndex(1)
            self.text_t_counsel.clear()
            self.line_t_snd.clear()
            th_t = Thread(target=self.counsel_rcv_t, args=(self.s_skt,))
            self.flag_t = True
            th_t.start()

    def counsel_go_s(self):  # 상담 요청 함수 (학생측)
        self.s_skt.send('^counsel'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        if rcv.decode() == '^NO':
            QMessageBox.warning(self, '상담방', '다른 학생이 상담하고 있습니다')
        else:
            self.stackedWidget_s.setCurrentIndex(1)
            self.text_s_counsel.clear()
            self.line_s_snd.clear()
            th_s = Thread(target=self.counsel_rcv_s, args=(self.s_skt,))
            self.flag_s = True
            th_s.start()

    def counsel_rcv_t(self, s_skt):  # 상담 수신 스레드 (교사측)
        while self.flag_t:
            rcv_msg = s_skt.recv(1024)
            if not self.flag_t:
                break
            if not rcv_msg:
                break
            self.text_t_counsel.append(f'학생 : {rcv_msg.decode()}')

    def counsel_rcv_s(self, s_skt):  # 상담 수신 스레드 (학생측)
        while self.flag_s:
            rcv_msg = s_skt.recv(1024)
            if not self.flag_s:
                break
            if not rcv_msg:
                break
            self.text_s_counsel.append(f'교사 : {rcv_msg.decode()}')

    def counsel_snd_t(self):  # 상담 대화 전송 함수 (교사측)
        if not self.line_t_snd.text():
            QMessageBox.warning(self, '입력 누락', '상담 내용을 입력해야 합니다')
        elif '^' in self.line_t_snd.text() or '/' in self.line_t_snd.text()\
                or '|' in self.line_t_snd.text():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
        else:
            self.text_t_counsel.append(f'교사 : {self.line_t_snd.text()}')
            self.s_skt.send(self.line_t_snd.text().encode())
            self.line_t_snd.clear()

    def counsel_snd_s(self):  # 상담 대화 전송 함수 (학생측)
        if not self.line_s_snd.text():
            QMessageBox.warning(self, '입력 누락', '상담 내용을 입력해야 합니다')
        elif '^' in self.line_s_snd.text() or '/' in self.line_s_snd.text()\
                or '|' in self.line_s_snd.text():
            QMessageBox.warning(self, '금지어 포함', '/, |, ^는 사용할 수 없습니다')
        else:
            self.text_s_counsel.append(f'학생 : {self.line_s_snd.text()}')
            self.s_skt.send(self.line_s_snd.text().encode())
            self.line_s_snd.clear()

    def counsel_end_t(self):  # 상담 종료 함수 (교사측)
        self.s_skt.send('^counselend'.encode())
        self.flag_t = False
        self.stackedWidget_t.setCurrentIndex(0)

    def counsel_end_s(self):  # 상담 종료 함수 (학생측)
        self.s_skt.send('^counselend'.encode())
        self.flag_s = False
        self.stackedWidget_s.setCurrentIndex(0)

    def counsel_back_t(self):  # 상담 받기 페이지 나가기 함수
        if self.stackedWidget_t.currentIndex() == 1:
            self.s_skt.send('^counselend'.encode())
            self.flag_t = False
            self.stackedWidget_t.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(2)

    def counsel_back_s(self):  # 상담 신청 페이지 나가기 함수
        if self.stackedWidget_s.currentIndex() == 1:
            self.s_skt.send('^counselend'.encode())
            self.flag_s = False
            self.stackedWidget_s.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(7)
    # 상담 받기/신청 끝

    # 통계 보기 시작
    def info_start(self):  # 통계 보기 페이지 진입 함수
        self.ax.clear()
        self.stackedWidget.setCurrentIndex(6)

    def info_show_1(self):  # 학생별 득점 통계 보기 함수
        self.ax.clear()
        x = []
        y = []
        self.s_skt.send('^infostudy'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        for i in rcv.decode().split('/'):
            a = i.split('|')
            x.append(a[0])
            y.append(int(a[1]))
        self.ax.bar(x, y, color=self.nationColor, alpha=0.4)
        self.ax.set_ylabel("score", fontsize=10, rotation=0, loc='top')
        self.ax.set_xlabel("student_name", fontsize=10, loc='right')
        self.ax.set_title("Student score rate", fontsize=14)
        self.canvas.draw()

    def info_show_2(self):  # 문제별 정/오답 통계 보기 함수
        self.ax.clear()
        x = []
        x_num = 0
        y = []
        self.s_skt.send('^infoquiz/'.encode())
        while True:
            rcv = self.s_skt.recv(1024)
            if sys.getsizeof(rcv) > 0:
                break
        for i in rcv.decode().split('|'):
            x_num += 1
            a = i.split('^')
            x.append(f'Q. {x_num}')
            if int(a[1]) + int(a[2]) == 0:
                y.append(0)
            else:
                y.append((int(a[1]) / (int(a[1]) + int(a[2]))) * 100)
        self.ax.plot(x, y, color='red', marker='o')
        self.ax.set_xlabel("Exam_Question", fontsize=10, loc='right')
        self.ax.set_ylabel("%", fontsize=15, rotation=0, loc='top')
        self.ax.set_title("Correct answer rate", fontsize=14)
        self.canvas.draw()

    def info_myself(self):  # 학생측의 자기 통계 보기 함수
        self.s_skt.send('^infomyself'.encode())
        while True:
            rcv = self.s_skt.recv(32)
            if sys.getsizeof(rcv) > 0:
                break
        QMessageBox.about(self, '총점 확인', f'당신의 점수는 {rcv.decode()}입니다')

    def info_back(self):  # 통계 보기 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(2)
    # 통계 보기 끝

    # 학습하기 시작
    def study_start(self):  # 학습하기 페이지 진입 함수
        self.text_study_name.clear()
        self.text_study_info.clear()
        self.stackedWidget.setCurrentIndex(11)
        if len(self.birdcodelist) == 0:
            con = sqlite3.connect('bird.db')
            cur = con.cursor()
            cur.execute("select code from birdcode")
            for i in cur:
                self.birdcodelist.append(i[0])

    def study_on(self):  # 학습하기 함수
        key = '9cCN4TXQK/nLX/tkVrz9+4qnPHIyI5sjjCpkfO9kPAH8y6fDcWtxwsp7JM0bozPvZklvvCVKqnZOig81BIMjmw=='
        url = 'http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo'
        code = random.choice(self.birdcodelist)
        while code in self.study_list:
            code = random.choice(self.birdcodelist)
        params = {'serviceKey': key, 'q1': code}
        bird_data = fromstring(requests.get(url, params=params).content.decode())
        self.text_study_name.setPlainText(bird_data[1][0][6].text)
        self.text_study_info.setPlainText(bird_data[1][0][16].text)
        QMessageBox.about(self, '학습 내용 확인', f'이번 학습 대상은 "{bird_data[1][0][6].text}"입니다')
        self.s_skt.send(f'^studysave/{code}'.encode())

    def study_back(self):  # 학습하기 페이지 나가기 함수
        self.stackedWidget.setCurrentIndex(7)
    # 학습하기 끝


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Main()
    myWindow.show()
    app.exec_()
