import sys
import PySide6
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, Slot

from PIL import ImageQt, ImageGrab, Image
import cv2

from capture import CaptureThread


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setFixedSize(255, 162)
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_lay = QVBoxLayout()
        self.main_widget.setLayout(self.main_lay)

        self.setWindowTitle("Auto accept")
        self.main_lay.addWidget(QLabel("Автоматический клик при смене пикселей"))
        
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.main_lay.addWidget(self.image)
        
        self.timer_label = QLabel("Таймер старта")
        self.main_lay.addWidget(self.timer_label)

        self.start_bt = QPushButton("Старт")
        self.main_lay.addWidget(self.start_bt)

        self.exit_bt = QPushButton("Стоп")
        self.exit_bt.clicked.connect(self.close)
        self.main_lay.addWidget(self.exit_bt)
        
        self.capture_thread = CaptureThread(20, 0.05, color_threshold=60, max_click=10, parent=self)
        self.capture_thread.update_frame.connect(self.update_image)
        self.start_bt.clicked.connect(self.capture_thread.set_clicker)
        self.capture_thread.start_click.connect(self.start_click)
        self.capture_thread.start()
    
    @Slot(bool, int, int)
    def start_click(self, state, time, counter):
        # print("Нажата кнопка")
        # print(self.size())
        text = f"до старта: {(5 - time) if (5 - time) >= 0 else 0}; Кликов: {counter}"
        if state:
            self.timer_label.setText("Кликкер запущен; " + text)
        else:
            self.timer_label.setText("Кликкер остановлен; " + text)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.capture_thread.set_clicker()
        return super().keyPressEvent(event)
        
    def update_image(self, frame):
        image = ImageQt.ImageQt(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        pixmap = QPixmap.fromImage(image)
        self.image.setPixmap(pixmap)

    
    def closeEvent(self, event):
        self.capture_thread.terminate()
        self.capture_thread.wait()
        return super().closeEvent(event)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())