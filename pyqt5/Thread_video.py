import sys
import cv2
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout

class WebcamThread(QThread):
    update_frame = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(WebcamThread, self).__init__(parent)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # (기본웹캠, Use DirectShow(DirectShow 백엔드 사용))
        self.running = True # 스레드 실행 상태 나타내는 플래그 설정

    # 스레드 핵심 메서드
    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert the frame to QImage
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.update_frame.emit(qimg)

    def stop(self):
        self.running = False
        self.cap.release()
        self.quit()

class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Webcam Viewer')
        self.setGeometry(100, 100, 1200, 800)

        # Create labels to display the webcam feed
        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.label3 = QLabel(self)
        self.labels = [self.label1, self.label2, self.label3]

        # Create a button to start the webcam
        self.btn_start = QPushButton('Start Webcam', self)
        self.btn_start.clicked.connect(self.start_webcams)

        # Create a button to stop the webcam
        self.btn_stop = QPushButton('Stop Webcam', self)
        self.btn_stop.clicked.connect(self.stop_webcams)
        self.btn_stop.setEnabled(False)

        # Create layouts
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()

        layout1.addWidget(self.label1)
        layout2.addWidget(self.label2)
        layout3.addWidget(self.label3)

        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)

        self.setLayout(layout)

        # Create webcam threads
        self.threads = [WebcamThread() for _ in range(3)]
        for i, thread in enumerate(self.threads):
            thread.update_frame.connect(lambda qimg, lbl=self.labels[i]: lbl.setPixmap(QPixmap.fromImage(qimg)))

    def start_webcams(self):
        for thread in self.threads:
            thread.start()
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def stop_webcams(self):
        for thread in self.threads:
            thread.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def closeEvent(self, event):
        for thread in self.threads:
            thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebcamApp()
    ex.show()
    sys.exit(app.exec_())
