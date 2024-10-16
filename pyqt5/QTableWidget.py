## Ex 5-21. QTableWidget.

import sys
from PyQt5.QtWidgets import *


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(20) # 행 개수
        self.tableWidget.setColumnCount(4) # 열 개수

        # setEditTriggers : 테이블의 항목 편집가능하도록 액션 지정
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers) # 편집 불가
        # self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked) # 더블클릭시 수정
        # self.tableWidget.setEditTriggers(QAbstractItemView.AllEditTriggers) # 클릭, 더블클릭 등 모든 액션에 대해 편집 가능

        # horizontalHeader : 수평 헤더 반환
        # setSectionResizeMode : 헤더의 크기 조절 방식 지정 메서드
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 헤더의 폭이 위젯의 폭에 맞춰지도록
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 헤더의 폭이 항목 값의 폭에 맞춰지도록 함

        # 항목 값 지정 setItem(행(row), 열(column), 값(value))
        for i in range(20):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(i+j)))

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.setWindowTitle('QTableWidget')
        self.setGeometry(300, 100, 600, 400)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
