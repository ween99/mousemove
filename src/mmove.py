import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QGridLayout, QStatusBar
from PyQt5.QtGui import QCursor, QPixmap, QMovie
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSettings
import pyautogui
import time
import ctypes

def resource_path(relative_path):
    """Get absolute path to resource. This works for development and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MouseMoverThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, size=100, delay=5):
        super().__init__()
        self.size = size
        self.delay = delay
        self.active = False

    def run(self):
        self.active = True
        while self.active:
            for movement in [(self.size, 0), (0, self.size), (-self.size, 0), (0, -self.size)]:
                if not self.active:
                    break
                pyautogui.moveRel(*movement, duration=1)
                time.sleep(self.delay)
        self.update_signal.emit("Mouse movement stopped.")

    def stop(self):
        self.active = False
        self.update_signal.emit("Mouse movement stopped.")


class AnimatedGifLabel(QLabel):
    def __init__(self, gif_path, static_image_path, parent=None):
        super().__init__(parent)
        self.movie = QMovie(resource_path(gif_path))
        self.static_image = QPixmap(resource_path(static_image_path))
        self.setPixmap(self.static_image)
        self.setCursor(QCursor(Qt.OpenHandCursor))

        self.dragging = False
        self.dragPosition = None

    def start_animation(self):
        self.setMovie(self.movie)
        self.movie.start()

    def stop_animation(self):
        self.movie.stop()
        self.setPixmap(self.static_image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragPosition = event.globalPos() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.parent().move(event.globalPos() - self.dragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.prevent_sleep()

    def initUI(self):
        self.setWindowTitle("Work, work, work")
        self.setFixedWidth(350)
        self.move(470, 270)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background: transparent;")

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        # Layout and widgets setup
        grid = QGridLayout(self)

        self.logo = AnimatedGifLabel(
            'assets/2310385203c488124b7eafd79947cc48.gif',
            'assets/frame_0_delay-0.11s.gif',
            parent=self
        )
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("margin-top: 20px;")

        self.process_button = QPushButton("Start")
        self.exit_button = QPushButton("Exit")
        self.setupWidgets(grid)

        self.mouse_mover_thread = MouseMoverThread()
        self.mouse_mover_thread.update_signal.connect(self.updateStatus)

        self.settings = QSettings("MyCompany", "MyApp")
        self.load_settings()

    def setupWidgets(self, grid):
        # Setup buttons
        for button in (self.process_button, self.exit_button):
            button.setCursor(QCursor(Qt.OpenHandCursor))
            button.setStyleSheet('''
                *{
                    border: 4px solid '#333';
                    border-radius: 35px;
                    font-size: 16px;
                    color: 'white';
                    padding: 25px 85px;
                    margin: 1px 8px;
                    background: #121519;
                }
                *:hover{
                    background: '#0057b7';
                }
            ''')

        self.process_button.clicked.connect(self.toggle_mouse_movement)
        self.exit_button.clicked.connect(self.closeApplication)

        grid.addWidget(self.logo, 0, 0, 1, 2)  # Span the logo for alignment
        grid.addWidget(self.process_button, 1, 0)
        grid.addWidget(self.exit_button, 1, 1)
        grid.addWidget(self.status_bar, 2, 0, 1, 2)

    def toggle_mouse_movement(self):
        if not self.mouse_mover_thread.isRunning():
            self.process_button.setText("Stop")
            self.mouse_mover_thread.start()
            self.logo.start_animation()
            self.status_bar.showMessage("Mouse movement started.")
        elif self.process_button.text() == "Stop":  # Ensures only the "Stop" button press stops the loop
            self.process_button.setText("Start")
            self.mouse_mover_thread.stop()
            self.logo.stop_animation()
            self.status_bar.showMessage("Mouse movement stopped.")

    def updateStatus(self, message):
        self.status_bar.showMessage(message)

    def load_settings(self):
        # This function can be expanded to load additional settings
        pass

    def save_settings(self):
        # This function can be expanded to save additional settings
        pass

    def prevent_sleep(self):
        # Prevent system from sleeping
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED

    def release_sleep(self):
        # Release system sleep prevention
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # Release ES_SYSTEM_REQUIRED

    def closeEvent(self, event):
        self.release_sleep()  # Release sleep prevention
        self.save_settings()
        event.accept()

    def closeApplication(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())