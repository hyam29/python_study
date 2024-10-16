import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

class Worker(QThread):
    # 작업 완료 시 신호를 보낼 수 있도록 pyqtSignal을 사용 (사용자 정의 시그널)
    finished = pyqtSignal(str)

    def run(self):
        # 시간이 오래 걸리는 작업을 수행
        time.sleep(5)
        result = "작업 완료!"
        self.finished.emit(result)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.label = QLabel('작업 대기 중', self)
        self.btn = QPushButton('작업 시작', self)
        self.btn.clicked.connect(self.startWorker)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.btn)

        self.setLayout(vbox)

        self.setWindowTitle('QThread 예제')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def startWorker(self):
        # Worker 스레드 생성 및 시작
        self.worker = Worker()
        self.worker.finished.connect(self.onFinished)
        self.worker.start()
        self.label.setText('작업 진행 중...')

    def onFinished(self, result):
        self.label.setText(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
