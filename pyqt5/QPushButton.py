## Ex 5-1. QPushButton.

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        btn1 = QPushButton('&Button1', self) # ('(& 단축키 지정시 붙임 : alt+b)버튼text', 버튼이 속할 부모 클래스 지정)
        btn1.setCheckable(True) # checked
        btn1.toggle() # 메서드 호출시 버튼 상태 변경

        btn2 = QPushButton(self)
        btn2.setText('Button&2') # &2: alt+2

        btn3 = QPushButton('Button3', self)
        btn3.setEnabled(False) # 버튼 사용 불가

        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)
        vbox.addWidget(btn3)

        self.setLayout(vbox)
        self.setWindowTitle('QPushButton')
        self.setGeometry(300, 300, 300, 200)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
