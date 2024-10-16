import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget

class MyApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Application Title')
            #창의 제목표시줄에 나타날 제목
        self.move(300, 300)
            #스크린 상에서 위젯이 나타날 위치(x방향[px], y방향[px])
        self.resize(400, 200)
            #위젯의 크기 (너비[px], 높이[px])
        self.show()
            #위젯을 화면에 띄움

    def center(self):
        window_info = self.frameGeometry() #창의 위치와 크기 정보 받음
        center_loc = QDesktopWidget().availableGeometry().center()
        #사용자의 모니터 가운데 위치 파악
        window_info.moveCenter(center_loc) #중심 위치를 지정한 곳으로 이동
        self.move(window_info.topLeft()) #현재 창의 위치를 지정한 곳으로 이동

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApplication()
    sys.exit(app.exec_())