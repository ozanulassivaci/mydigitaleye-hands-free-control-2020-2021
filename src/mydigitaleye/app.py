from pathlib import Path

import cv2
from PyQt5.QtCore import QThread, QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QImage, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QTabWidget, QVBoxLayout, QWidget)

from .strings import STRINGS
from .tracker import DEFAULT_SPEEDS, Tracker

ASSETS = Path(__file__).parent / "assets"
FEED_SIZE = (640, 480)
SPEED_RANGE = (0, 100)


class CameraWorker(QThread):
    """Reads frames and runs the tracker off the GUI thread."""

    frame_ready = pyqtSignal(QImage)
    sound_requested = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, source, model_path, actions, speeds):
        super().__init__()
        self.source = source
        self.model_path = model_path
        self.actions = actions
        self.speeds = speeds
        self._running = True

    def stop(self):
        self._running = False
        self.wait()

    def run(self):
        # Loading the model here keeps the window responsive while the
        # "camera starting" image is shown. Sounds go through a queued signal,
        # so the GUI thread plays them and detection never stalls.
        tracker = Tracker(self.model_path, self.actions, self.sound_requested.emit, self.speeds)
        capture = cv2.VideoCapture(self.source)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, FEED_SIZE[0])
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FEED_SIZE[1])
        if not capture.isOpened():
            self.failed.emit(f"Cannot open video source: {self.source}")
            return
        try:
            while self._running:
                ok, frame = capture.read()
                if not ok:
                    break
                frame = tracker.process(cv2.flip(frame, 1))
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = rgb.shape
                image = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
                self.frame_ready.emit(image.scaled(*FEED_SIZE, Qt.KeepAspectRatio).copy())
        finally:
            capture.release()


class MainWindow(QMainWindow):
    def __init__(self, lang, source, model_path, actions):
        super().__init__()
        self.lang = lang
        self.text = STRINGS[lang]
        self.player = QMediaPlayer(self)
        self.speeds = dict(DEFAULT_SPEEDS)

        self.setWindowTitle(self.text["title"])
        self.setWindowIcon(QIcon(str(ASSETS / "icons" / "app.ico")))

        tabs = QTabWidget()
        tabs.addTab(self._camera_tab(), self.text["tab_camera"])
        tabs.addTab(self._settings_tab(), self.text["tab_settings"])
        tabs.addTab(self._image_tab("shortcuts"), self.text["tab_shortcuts"])
        tabs.addTab(self._image_tab("how_to_use"), self.text["tab_how_to_use"])
        self.setCentralWidget(tabs)

        self.worker = CameraWorker(source, model_path, actions, self.speeds)
        self.worker.frame_ready.connect(self.show_frame)
        self.worker.sound_requested.connect(self.play_sound)
        self.worker.failed.connect(self.feed.setText)
        self.worker.start()

    def asset(self, name):
        return str(next((ASSETS / self.lang).glob(name + ".*")))

    def image(self, name):
        label = QLabel()
        label.setPixmap(QPixmap(self.asset(name)))
        return label

    def _camera_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.feed = QLabel()
        self.feed.setPixmap(QPixmap(self.asset("camera_wait")))
        self.feed.setStyleSheet("border: 3px solid blue;")
        exit_button = QPushButton(self.text["exit"])
        exit_button.clicked.connect(self.close)
        layout.addWidget(self.image("header"))
        layout.addWidget(self.feed)
        layout.addWidget(exit_button)
        layout.addWidget(self.image("banner"))
        return tab

    def _settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(self.image("banner"))
        for mode in (1, 2):
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 40))
            label.setStyleSheet("QLabel { border: 2px solid black; background: white; }")
            minus, plus = QPushButton("-"), QPushButton("+")
            minus.clicked.connect(lambda _, m=mode, l=label: self.change_speed(m, l, -1))
            plus.clicked.connect(lambda _, m=mode, l=label: self.change_speed(m, l, +1))
            buttons = QHBoxLayout()
            buttons.addWidget(minus)
            buttons.addWidget(plus)
            layout.addWidget(label)
            layout.addLayout(buttons)
            self.change_speed(mode, label, 0)
        return tab

    def _image_tab(self, name):
        tab = QWidget()
        QVBoxLayout(tab).addWidget(self.image(name), alignment=Qt.AlignCenter)
        return tab

    def change_speed(self, mode, label, step):
        value = min(max(self.speeds[mode] + step, SPEED_RANGE[0]), SPEED_RANGE[1])
        self.speeds[mode] = value
        label.setText(self.text["speed"].format(mode=mode, value=value))

    def show_frame(self, image):
        self.feed.setPixmap(QPixmap.fromImage(image))

    def play_sound(self, name):
        path = next((ASSETS / "sounds" / self.lang).glob(name + ".*"))
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(str(path))))
        self.player.play()

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)
