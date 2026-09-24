# python ver 3.6.12

import sys
from PyQt5.QtGui import *     # pyqt 5 ver 5.15.2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2  # ver 4.4.0.42
import dlib  # ver 19.8.1
import numpy as np  # ver 1.19.2
from math import hypot
import pyautogui  # ver 0.9.50
import datetime
import time
from playsound import playsound  # ver 1.2.2

mod1X = 2
mod2X = 6

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.title = "Dijital Gözüm"
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("./tools/cam.ico"))

        self.tab_widget = MyTabWidget(self)
        self.setCentralWidget(self.tab_widget)


class MyTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tabs.addTab(self.tab1, "Kamera")
        self.tabs.addTab(self.tab2, "Ayarlar")
        self.tabs.addTab(self.tab3, "Kısa yollar")
        self.tabs.addTab(self.tab4, "Nasıl Kullanılır")

        self.tab1.layout = QVBoxLayout(self)

        self.label_top = QLabel(self)
        self.pixmap = QPixmap('./tools/toppng.png')
        self.label_top.setPixmap(self.pixmap)

        self.label_bottom = QLabel(self)
        self.pixmap_bottom = QPixmap('./tools/toplogo.png')
        self.label_bottom.setPixmap(self.pixmap_bottom)

        self.CancelBTN = QPushButton("Çıkış")
        self.CancelBTN.clicked.connect(self.CancelFeed)

        self.FeedLabel = QLabel()
        self.pixmap_wait = QPixmap("./tools/camwait1.png")
        self.FeedLabel.setPixmap(self.pixmap_wait)
        self.FeedLabel.setStyleSheet("border: 3px solid blue;")

        self.tab1.layout.addWidget(self.label_top)
        self.tab1.layout.addWidget(self.FeedLabel)
        self.tab1.layout.addWidget(self.CancelBTN)
        self.tab1.layout.addWidget(self.label_bottom)

        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QVBoxLayout(self)
        self.tab2.hlayout1 = QHBoxLayout(self)
        self.tab2.hlayout2 = QHBoxLayout(self)

        self.label_top2 = QLabel(self)
        self.pixmap2 = QPixmap('./tools/toplogo.png')
        self.label_top2.setPixmap(self.pixmap2)
        self.tab2.layout.addWidget(self.label_top2)

        self.margin_1 = QLabel(self)
        self.margin_1.setStyleSheet("QLabel"
                                 "{"
                                 "border : 2px solid black;"
                                 "background : white;"
                                 "}")

        self.margin_1.setAlignment(Qt.AlignCenter)

        self.margin_1.setFont(QFont('Arial', 40))
        self.margin_1.setText(f"Mod 1: {mod1X}")

        self.push_plus_1 = QPushButton("+")
        self.push_plus_1.clicked.connect(self.push_plus1_f)

        self.push_minus_1 = QPushButton("-")
        self.push_minus_1.clicked.connect(self.push_minus1_f)

        self.margin_2 = QLabel(self)
        self.margin_2.setStyleSheet("QLabel"
                                 "{"
                                 "border : 2px solid black;"
                                 "background : white;"
                                 "}")

        self.margin_2.setAlignment(Qt.AlignCenter)

        self.margin_2.setFont(QFont('Arial', 40))
        self.margin_2.setText(f"Mod 2: {mod2X}")

        self.push_plus_2 = QPushButton("+")
        self.push_plus_2.clicked.connect(self.push_plus2_f)

        self.push_minus_2 = QPushButton("-")
        self.push_minus_2.clicked.connect(self.push_minus2_f)

        self.tab2.hlayout1.addWidget(self.push_minus_1)
        self.tab2.hlayout1.addWidget(self.push_plus_1)

        self.tab2.hlayout2.addWidget(self.push_minus_2)
        self.tab2.hlayout2.addWidget(self.push_plus_2)

        self.tab2.layout.addWidget(self.margin_1)
        self.tab2.layout.addLayout(self.tab2.hlayout1)
        self.tab2.layout.addWidget(self.margin_2)
        self.tab2.layout.addLayout(self.tab2.hlayout2)

        self.tab2.setLayout(self.tab2.layout)

        self.tab3.layout = QVBoxLayout(self)

        self.label_top3 = QLabel(self)
        self.pixmap3 = QPixmap('./tools/shortcuts.png')
        self.label_top3.setPixmap(self.pixmap3)
        self.tab3.layout.addWidget(self.label_top3)

        self.tab3.setLayout(self.tab3.layout)

        self.tab4.layout = QVBoxLayout(self)

        self.label_bottom4 = QLabel(self)
        self.pixmap_bottom4 = QPixmap('./tools/bottompng.png')
        self.label_bottom4.setPixmap(self.pixmap_bottom4)

        self.label_top4 = QLabel(self)
        self.pixmap_top4 = QPixmap('./tools/use.png')
        self.label_top4.setPixmap(self.pixmap_top4)

        self.label_top41 = QLabel(self)
        self.pixmap_top41 = QPixmap('./tools/use1.png')
        self.label_top41.setPixmap(self.pixmap_top41)

        self.tab4.layout.addWidget(self.label_top4)
        self.tab4.layout.addWidget(self.label_top41)
        self.tab4.layout.addWidget(self.label_bottom4)

        self.tab4.setLayout(self.tab4.layout)

        self.Worker1 = Worker1()

        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()
        global a
        a += 1

    def push_plus1_f(self):
        global mod1X
        mod1X += 1
        if mod1X >= 100:
            mod1X = 100
            self.margin_1.setText(f"Mod 1: {mod1X}")
        self.margin_1.setText(f"Mod 1: {mod1X}")

    def push_minus1_f(self):
        global mod1X
        mod1X -= 1
        if mod1X <= 0:
            mod1X = 0
            self.margin_1.setText(f"Mod 1: {mod1X}")
        self.margin_1.setText(f"Mod 1: {mod1X}" )

    def push_plus2_f(self):
        global mod2X
        mod2X += 1
        if mod2X >= 100:
            mod2X = 100
            self.margin_2.setText(f"Mod 2: {mod2X}")
        self.margin_2.setText(f"Mod 2: {mod2X}")

    def push_minus2_f(self):
        global mod2X
        mod2X -= 1
        if mod2X <= 0:
            mod2X = 0
            self.margin_2.setText(f"Mod 2: {mod2X}")
        self.margin_2.setText(f"Mod 2: {mod2X}" )

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True

        webcam = cv2.VideoCapture(0)

        webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        detector = dlib.get_frontal_face_detector()  # dlib ön yüz bulma
        predictor = dlib.shape_predictor(
            "./tools/shape_predictor_68_face_landmarks.dat")  # dlib yüzdeki noktaları (0-67) birleştirmek için

        red = (0, 0, 255)
        blue = (255, 0, 0)
        green = (0, 255, 0)

        modChoiceEx = 0
        mod1Choice = 0
        mod2Choice = 0

        secondSet = set()
        second = 11
        secondPass = 0

        leftEyePupils = None
        rightEyePupils = None

        pause_time_list = list()
        pause_set = set()
        pause_blinking = 0

        continue_time_list = list()
        continue_blinking = 0

        desktop_time_list = list()
        desktop_blinking = 0

        keyboard_time_list = list()
        keyboard_blinking = 0

        file_time_list = list()
        file_blinking = 0

        second_now = datetime.datetime.now()
        now_seconds = time.mktime(second_now.timetuple())
        now_seconds = int(now_seconds)


        def midPoint(p1, p2):
            return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

        def hor(hor_points, facial_landmarks):
            left_left_point = (facial_landmarks.part(hor_points[0]).x, facial_landmarks.part(hor_points[0]).y)
            left_right_point = (facial_landmarks.part(hor_points[1]).x, facial_landmarks.part(hor_points[1]).y)

            right_left_point = (facial_landmarks.part(hor_points[2]).x, facial_landmarks.part(hor_points[2]).y)
            right_right_point = (facial_landmarks.part(hor_points[3]).x, facial_landmarks.part(hor_points[3]).y)

            left_hor_line_lenght = hypot((left_left_point[0] - left_right_point[0]),
                                         (left_left_point[1] - left_right_point[1]))
            right_hor_line_lenght = hypot((right_left_point[0] - right_right_point[0]),
                                          (right_left_point[1] - right_right_point[1]))

            hor_line_lenght = (left_hor_line_lenght + right_hor_line_lenght) / 2

            return hor_line_lenght

        def get_blinking_ratio(eye_points, facial_landmarks):
            center_top = midPoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
            center_bottom = midPoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

            hor_line_lenght = hor([36, 39, 42, 45], facial_landmarks)
            ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

            ratio = round(hor_line_lenght / ver_line_lenght, 1)
            return ratio

        def eyeMidCenter(eye_points,facial_landmarks):
            # [37,38,40,41]
            eyeXTop = midPoint(facial_landmarks.part(eye_points[0]),facial_landmarks.part(eye_points[1]))
            eyeXBottom = midPoint(facial_landmarks.part(eye_points[2]),facial_landmarks.part(eye_points[3]))

            eyeX = int((eyeXTop[0] + eyeXBottom[0]) / 2)

            eyeYLeft = midPoint(facial_landmarks.part(eye_points[0]),facial_landmarks.part(eye_points[3]))
            eyeYRight = midPoint(facial_landmarks.part(eye_points[1]),facial_landmarks.part(eye_points[2]))

            eyeY = int((eyeYLeft[1] + eyeYRight[1]) / 2)

            eyeMidCoordinate = (eyeX,eyeY)

            return eyeMidCoordinate

        def eyebrow(eye_points,landmarks):
            # [21,22,27,0,1,16,15]

            mid = midPoint(landmarks.part(eye_points[0]),landmarks.part(eye_points[1]))
            cv2.circle(frame,mid,1,blue,1)
            margin = int(0.9*(((landmarks.part(eye_points[3]).y - landmarks.part(eye_points[4]).y) +
                               (landmarks.part(eye_points[5]).y - landmarks.part(eye_points[6]).y)) // 2 ))

            cv2.circle(frame,( mid[0],landmarks.part(eye_points[2]).y + margin),1,red,1)

            if (landmarks.part(eye_points[2]).y + margin) > (mid[1]):
                eye_brow_up = 1
                return eye_brow_up
            else:
                eye_brow_up = 0
                return eye_brow_up

        def isolate_eye(frame, landmarks, points):

            region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points])
            region = region.astype(np.int32)

            margin = 4

            min_x = np.min(region[:, 0]) - margin
            max_x = np.max(region[:, 0]) + margin
            min_y = np.min(region[:, 1]) - margin
            max_y = np.max(region[:, 1]) + margin

            eye_frame = frame[min_y:max_y, min_x:max_x]

            return eye_frame, min_x, min_y

        while self.ThreadActive:
            ret, frame = webcam.read()
            while True:
                _, frame = webcam.read()
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)


                if len(secondSet) < second:
                    now = datetime.datetime.now()
                    nowSecond = now.strftime("%S")
                    secondSet.add(nowSecond)
                    secondFrame = second - len(secondSet)
                    cv2.putText(frame, f"{secondFrame}", (550, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, blue)

                    if len(secondSet) == 11:
                        secondPass += 1

                try:
                    # ekrana anlık olarak bir yüz daha girmesi gibi durumlarda
                    # hata verip programın çökmesini önlemek için

                    for face in faces:

                        landmarks = predictor(gray, face)

                        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
                        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
                        blinking_ratio = round((left_eye_ratio + right_eye_ratio) / 2, 2)

                        eye_brow = eyebrow([21, 22, 27, 0, 1, 16, 15], landmarks)

                        while modChoiceEx == 0 and secondPass > 0:

                            if (left_eye_ratio > blinking_ratio and left_eye_ratio > 5.7 and np.all(leftEyePupils == None)
                                    and np.all(rightEyePupils != None)):
                                mod1Choice += 1
                            elif (right_eye_ratio > blinking_ratio and right_eye_ratio > 5.7 and np.all(rightEyePupils == None)
                                  and np.all(leftEyePupils != None)):
                                mod2Choice += 1
                            break

                        if mod1Choice > 1 or mod2Choice > 1:
                            modChoiceEx += 1

                        if mod1Choice >= 2 and (mod2Choice == 1 or mod2Choice == 0):

                            noiseAreaX = int((landmarks.part(16).x - landmarks.part(0).x) // 10)
                            noiseAreaY = int((landmarks.part(12).y - landmarks.part(0).y) // 2)

                            noiseAreaStart = (landmarks.part(0).x - noiseAreaX, landmarks.part(0).y - noiseAreaY)
                            noiseAreaEnd = (landmarks.part(16).x + noiseAreaX, landmarks.part(12).y + noiseAreaY)

                            zeroPointX = ((noiseAreaEnd[0] + noiseAreaStart[0]) // 2)
                            zeroPointY = ((noiseAreaStart[1] + noiseAreaEnd[1]) // 2)

                            cv2.rectangle(frame, noiseAreaStart, noiseAreaEnd, red, 2)

                            noise = (landmarks.part(30).x, landmarks.part(30).y)

                            cv2.circle(frame, noise, 2, blue, -1)
                            cv2.circle(frame, (zeroPointX, zeroPointY), 2, red, -1)

                            safeAreaX = int((noiseAreaEnd[0] - noiseAreaStart[0]) // 8)
                            safeAreStart = (zeroPointX - safeAreaX, zeroPointY - safeAreaX)
                            safeAreEnd = (zeroPointX + safeAreaX, zeroPointY + safeAreaX)

                            cv2.rectangle(frame, safeAreStart, safeAreEnd, blue, 2)

                            if np.all((leftEyePupils == None)) and np.all(
                                    (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                    pause_set) == 0 and eye_brow == 0:
                                pause_blinking += 1
                                pause_now = datetime.datetime.now()
                                pause_seconds = time.mktime(pause_now.timetuple())
                                pause_seconds = int(pause_seconds)
                                pause_time_list.append(pause_seconds)
                                if pause_blinking >= 50 and (int(pause_time_list[-1]) - int(pause_time_list[0])) <= 5:
                                    pause_set.add(1)
                                    pause_blinking = 0
                                    pause_time_list.clear()
                                    playsound("./tools/stop.mp3")
                                elif pause_blinking < 50 and (int(pause_time_list[-1]) - pause_time_list[0]) > 5:
                                    pause_blinking = 0
                                    pause_time_list.clear()

                            if np.all((leftEyePupils == None)) and np.all(
                                    (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                    pause_set) == 1 and eye_brow == 0:
                                continue_blinking += 1
                                continue_now = datetime.datetime.now()
                                continue_seconds = time.mktime(continue_now.timetuple())
                                continue_seconds = int(continue_seconds)
                                continue_time_list.append(continue_seconds)
                                if continue_blinking >= 50 and (int(continue_time_list[-1]) - int(continue_time_list[0])) <= 5:
                                    pause_set.clear()
                                    continue_time_list.clear()
                                    continue_blinking = 0
                                    playsound("./tools/start.mp3")
                                elif continue_blinking < 50 and (int(continue_time_list[-1]) - int(continue_time_list[0])) > 5:
                                    continue_blinking = 0
                                    continue_time_list.clear()

                            if len(pause_set) == 0:

                                if (left_eye_ratio > blinking_ratio and left_eye_ratio > 5.7 and np.all(leftEyePupils == None)
                                        and np.all(rightEyePupils != None) and eye_brow == 0):
                                    desktop_blinking += 1
                                    desktop_now = datetime.datetime.now()
                                    desktop_seconds = time.mktime(desktop_now.timetuple())
                                    desktop_seconds = int(desktop_seconds)
                                    desktop_time_list.append(desktop_seconds)
                                    if desktop_blinking >= 25 and (int(desktop_time_list[-1]) - int(desktop_time_list[0])) <= 5:
                                        desktop_time_list.clear()
                                        desktop_blinking = 0
                                        pyautogui.hotkey("win", "d")
                                        playsound("./tools/desktop.mp3")
                                    elif desktop_blinking < 25 and (int(desktop_time_list[-1]) - int(desktop_time_list[0])) > 5:
                                        desktop_blinking = 0
                                        desktop_time_list.clear()

                                if (right_eye_ratio > blinking_ratio and right_eye_ratio > 5.7 and np.all(rightEyePupils == None)
                                        and np.all(leftEyePupils != None) and eye_brow == 0):
                                    keyboard_blinking += 1
                                    keyboard_now = datetime.datetime.now()
                                    keyboard_seconds = time.mktime(keyboard_now.timetuple())
                                    keyboard_seconds = int(keyboard_seconds)
                                    keyboard_time_list.append(keyboard_seconds)
                                    if keyboard_blinking >= 25 and (int(keyboard_time_list[-1]) - int(keyboard_time_list[0])) <= 5:
                                        keyboard_time_list.clear()
                                        keyboard_blinking = 0
                                        pyautogui.hotkey("win", "ctrl", "o")
                                        playsound("./tools/keyboard.mp3")
                                    elif keyboard_blinking < 25 and (int(keyboard_time_list[-1]) - int(keyboard_time_list[0])) > 5:
                                        keyboard_blinking = 0
                                        keyboard_time_list.clear()

                                if np.all((leftEyePupils == None)) and np.all(
                                        (rightEyePupils == None)) and blinking_ratio > 5.7 and eye_brow == 1:
                                    file_blinking += 1
                                    file_now = datetime.datetime.now()
                                    file_seconds = time.mktime(file_now.timetuple())
                                    file_seconds = int(file_seconds)
                                    file_time_list.append(file_seconds)
                                    if file_blinking >= 30 and (int(file_time_list[-1]) - int(file_time_list[0])) <= 5:
                                        file_time_list.clear()
                                        file_blinking = 0
                                        pyautogui.hotkey("win", "e")
                                        playsound("./tools/file.mp3")
                                    elif file_blinking < 30 and (int(file_time_list[-1])- int(file_time_list[0])) > 5:
                                        file_blinking = 0
                                        file_time_list.clear()

                                if (zeroPointY - safeAreaX > noise[1]):
                                    cursorMod1 = noise[1] - (zeroPointY - safeAreaX)
                                    position = pyautogui.position()
                                    pyautogui.moveTo(position[0], position[1] + (mod1X * cursorMod1))
                                elif (noise[1] > zeroPointY + safeAreaX):
                                    cursorMod1 = (zeroPointY + safeAreaX) - noise[1]
                                    position = pyautogui.position()
                                    pyautogui.moveTo(position[0], position[1] - (mod1X * cursorMod1))
                                elif (noise[0] > zeroPointX + safeAreaX):
                                    cursorMod1 = noise[0] - (zeroPointX + safeAreaX)
                                    position = pyautogui.position()
                                    pyautogui.moveTo(position[0] + (mod1X * cursorMod1), position[1])
                                elif (zeroPointX - safeAreaX > noise[0]):
                                    cursorMod1 = (zeroPointX - safeAreaX) - noise[0]
                                    position = pyautogui.position()
                                    pyautogui.moveTo(position[0] - (mod1X * cursorMod1), position[1])

                                mod1a = (left_eye_ratio > blinking_ratio and left_eye_ratio > 5.7 and np.all(leftEyePupils == None)
                                         and np.all(rightEyePupils != None))
                                mod1b = (right_eye_ratio > blinking_ratio and right_eye_ratio > 5.7 and np.all(rightEyePupils == None)
                                         and np.all(leftEyePupils != None))

                                if mod1a and (noise[0] > safeAreStart[0] and noise[0] < safeAreEnd[0]) and (
                                        noise[1] > safeAreStart[1] and noise[1] < safeAreEnd[1]):
                                    pyautogui.click(button="left")
                                if mod1b and (noise[0] > safeAreStart[0] and noise[0] < safeAreEnd[0]) and (
                                        noise[1] > safeAreStart[1] and noise[1] < safeAreEnd[1]):
                                    pyautogui.click(button="right")

                        try:

                            isolate_left = isolate_eye(frame, landmarks, [36, 37, 38, 39, 40, 41])[0]
                            isolate_right = isolate_eye(frame, landmarks, [42, 43, 44, 45, 46, 47])[0]

                            isolate_left_gray = cv2.cvtColor(isolate_left, cv2.COLOR_BGR2GRAY)
                            isolate_right_gray = cv2.cvtColor(isolate_right, cv2.COLOR_BGR2GRAY)

                            isolate_left_blur = cv2.medianBlur(isolate_left_gray, 5)
                            isolate_right_blur = cv2.medianBlur(isolate_right_gray, 5)

                            leftEyeCenterCoordinate = eyeMidCenter([37,38,40,41],landmarks)

                            leftEyeCenterCoordinate = (
                            leftEyeCenterCoordinate[0] - isolate_eye(frame, landmarks, [36, 37, 38, 39, 40, 41])[1],
                            leftEyeCenterCoordinate[1] - isolate_eye(frame, landmarks, [36, 37, 38, 39, 40, 41])[2])

                            rightEyeCenterCoordinate = eyeMidCenter([43,44,46,47], landmarks)
                            rightEyeCenterCoordinate = (
                            rightEyeCenterCoordinate[0] - isolate_eye(frame, landmarks, [42, 43, 44, 45, 46, 47])[1],
                            rightEyeCenterCoordinate[1] - isolate_eye(frame, landmarks, [42, 43, 44, 45, 46, 47])[2])


                        except:
                            pass

                        try:

                            # yüze bakan ışık olmalı çalışması için

                            param_1 = 200
                            param_2 = 5
                            maxradius = 8
                            minradius = 1

                            leftEyePupils = cv2.HoughCircles(isolate_left_blur, cv2.HOUGH_GRADIENT, 1, 999, param1=param_1,
                                                             param2=param_2, maxRadius=maxradius, minRadius=minradius)

                            leftEyePupils = np.uint16(np.around(leftEyePupils))

                            for i in leftEyePupils[0, :]:
                                # dış daire çizimi
                                cv2.circle(isolate_left, (i[0], i[1]), i[2], green, 1)
                                # iç daire çizimi
                                cv2.circle(isolate_left, (i[0], i[1]), 2, red, 1)

                                leftEyePupilX = (i[0])
                                leftEyePupilY = (i[1])

                                leftEyePupilCoordinate = (leftEyePupilX, leftEyePupilY)


                        except:
                            pass

                        try:

                            param_1 = 200
                            param_2 = 5
                            maxradius = 8
                            minradius = 1

                            # aynı işlemler sağ göz için
                            rightEyePupils = cv2.HoughCircles(isolate_right_blur, cv2.HOUGH_GRADIENT, 1, 999,
                                                              param1=param_1,
                                                              param2=param_2, maxRadius=maxradius, minRadius=minradius)

                            rightEyePupils = np.uint16(np.around(rightEyePupils))

                            for a in rightEyePupils[0, :]:
                                # dış daire çizimi
                                cv2.circle(isolate_right, (a[0], a[1]), a[2], green, 1)
                                # iç daire çizimi
                                cv2.circle(isolate_right, (a[0], a[1]), 2, red, 1)

                                rightEyePupilX = (a[0])
                                rightEyePupilY = (a[1])

                                rightEyePupilCoordinate = (rightEyePupilX, rightEyePupilY)


                        except:
                            pass

                        try:

                            rightlookX = int(((leftEyePupilCoordinate[0] - leftEyeCenterCoordinate[0]) + (
                                        rightEyePupilCoordinate[0] - rightEyeCenterCoordinate[0])) // 2)
                            leftlookX = int(((leftEyeCenterCoordinate[0] - leftEyePupilCoordinate[0]) + (
                                        rightEyeCenterCoordinate[0] - rightEyePupilCoordinate[0])) // 2)
                            uplookX = int(((leftEyeCenterCoordinate[1] - leftEyePupilCoordinate[1]) + (
                                        rightEyeCenterCoordinate[1] - rightEyePupilCoordinate[1])) // 2)


                            eye_pupil_x = int((rightEyePupilCoordinate[0] + leftEyePupilCoordinate[0]) // 2)
                            eye_center_x = int((rightEyeCenterCoordinate[0] + leftEyeCenterCoordinate[0]) // 2)
                            eye_pupil_y = int((rightEyePupilCoordinate[1] + leftEyePupilCoordinate[1]) // 2)
                            eye_center_y = int((rightEyeCenterCoordinate[1] + leftEyeCenterCoordinate[1]) // 2)

                            hor_line_lenght = int(hor([36, 39, 42, 45], landmarks) // 8)

                            safeEyeAreaStart = (eye_center_x - hor_line_lenght, eye_center_y - hor_line_lenght)
                            safeEyeAreaEnd = (eye_center_x + hor_line_lenght, eye_center_y + hor_line_lenght)


                            if mod2Choice >= 2 and (mod1Choice == 1 or mod1Choice == 0):

                                noiseAreaX = int((landmarks.part(16).x - landmarks.part(0).x) // 10)
                                noiseAreaY = int((landmarks.part(12).y - landmarks.part(0).y) // 2)

                                noiseAreaStart = (landmarks.part(0).x - noiseAreaX, landmarks.part(0).y - noiseAreaY)
                                noiseAreaEnd = (landmarks.part(16).x + noiseAreaX, landmarks.part(12).y + noiseAreaY)

                                zeroPointX = ((noiseAreaEnd[0] + noiseAreaStart[0]) // 2)
                                zeroPointY = ((noiseAreaStart[1] + noiseAreaEnd[1]) // 2)

                                cv2.rectangle(frame, noiseAreaStart, noiseAreaEnd, red, 2)

                                noise = (landmarks.part(30).x, landmarks.part(30).y)

                                cv2.circle(frame, noise, 2, blue, -1)
                                cv2.circle(frame, (zeroPointX, zeroPointY), 2, red, -1)

                                if np.all((leftEyePupils == None)) and np.all(
                                        (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                    pause_set) == 0 and eye_brow == 0:
                                    pause_blinking += 1
                                    pause_now = datetime.datetime.now()
                                    pause_seconds = time.mktime(pause_now.timetuple())
                                    pause_seconds = int(pause_seconds)
                                    pause_time_list.append(pause_seconds)
                                    if pause_blinking >= 50 and (int(pause_time_list[-1])- int(pause_time_list[0])) <= 5:
                                        pause_set.add(1)
                                        pause_blinking = 0
                                        pause_time_list.clear()
                                        playsound("./tools/stop.mp3")
                                    elif pause_blinking < 50 and (int(pause_time_list[-1]) - int(pause_time_list[0])) > 5:
                                        pause_blinking = 0
                                        pause_time_list.clear()


                                if np.all((leftEyePupils == None)) and np.all(
                                        (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                    pause_set) == 1 and eye_brow == 0:
                                    continue_blinking += 1
                                    continue_now = datetime.datetime.now()
                                    continue_seconds = time.mktime(continue_now.timetuple())
                                    continue_seconds = int(continue_seconds)
                                    continue_time_list.append(continue_seconds)
                                    if continue_blinking >= 50 and (int(continue_time_list[-1]) - int(continue_time_list[0])) <= 5:
                                        pause_set.clear()
                                        continue_time_list.clear()
                                        continue_blinking = 0
                                        playsound("./tools/start.mp3")
                                    elif continue_blinking < 50 and (int(continue_time_list[-1]) - int(continue_time_list[0])) > 5:
                                        continue_blinking = 0
                                        continue_time_list.clear()

                                if len(pause_set) == 0:

                                    if (left_eye_ratio > blinking_ratio and left_eye_ratio > 5.7 and np.all(leftEyePupils == None)
                                            and np.all(rightEyePupils != None) and eye_brow == 0):
                                        desktop_blinking += 1
                                        desktop_now = datetime.datetime.now()
                                        desktop_seconds = time.mktime(desktop_now.timetuple())
                                        desktop_seconds = int(desktop_seconds)
                                        desktop_time_list.append(desktop_seconds)
                                        if desktop_blinking >= 50 and (int(desktop_time_list[-1]) - int(desktop_time_list[0])) <= 5:
                                            desktop_time_list.clear()
                                            desktop_blinking = 0
                                            pyautogui.hotkey("win", "d")
                                            playsound("./tools/desktop.mp3")
                                        elif desktop_blinking < 50 and (int(desktop_time_list[-1]) - int(desktop_time_list[0])) > 5:
                                            desktop_blinking = 0
                                            desktop_time_list.clear()

                                    if (right_eye_ratio > blinking_ratio and right_eye_ratio > 5.7 and np.all(rightEyePupils == None)
                                            and np.all(leftEyePupils != None) and eye_brow == 0):
                                        keyboard_blinking += 1
                                        keyboard_now = datetime.datetime.now()
                                        keyboard_seconds = time.mktime(keyboard_now.timetuple())
                                        keyboard_seconds = int(keyboard_seconds)
                                        keyboard_time_list.append(keyboard_seconds)
                                        if keyboard_blinking >= 25 and (int(keyboard_time_list[-1]) - int(keyboard_time_list[0])) <= 5:
                                            keyboard_time_list.clear()
                                            keyboard_blinking = 0
                                            pyautogui.hotkey("win", "ctrl", "o")
                                            playsound("./tools/keyboard.mp3")
                                        elif keyboard_blinking < 25 and (int(keyboard_time_list[-1]) - int(keyboard_time_list[0])) > 5:
                                            keyboard_blinking = 0
                                            keyboard_time_list.clear()

                                    if np.all((leftEyePupils == None)) and np.all(
                                            (rightEyePupils == None)) and blinking_ratio > 5.7 and eye_brow == 1:
                                        file_blinking += 1
                                        file_now = datetime.datetime.now()
                                        file_seconds = time.mktime(file_now.timetuple())
                                        file_seconds = int(file_seconds)
                                        file_time_list.append(file_seconds)
                                        if file_blinking >= 30 and (int(file_time_list[-1]) - int(file_time_list[0])) <= 5:
                                            file_time_list.clear()
                                            file_blinking = 0
                                            pyautogui.hotkey("win", "e")
                                            playsound("./tools/file.mp3")
                                        elif file_blinking < 30 and (int(file_time_list[-1]) - int(file_time_list[0])) > 5:
                                            file_blinking = 0
                                            file_time_list.clear()

                                    if np.all((leftEyePupils != None)) and np.all((rightEyePupils != None)) and len(
                                            pause_set) == 0:
                                        if (eye_pupil_y < safeEyeAreaStart[1]):
                                            cursorMod2 = mod2X * uplookX
                                            position = pyautogui.position()
                                            pyautogui.moveTo(position[0], position[1] - cursorMod2)
                                        elif (eye_brow == 1):
                                            cursorMod2 = 2 * mod2X
                                            position = pyautogui.position()
                                            pyautogui.moveTo(position[0], position[1] + cursorMod2)
                                        elif (eye_pupil_x < safeEyeAreaStart[0]):
                                            cursorMod2 = mod2X * leftlookX
                                            position = pyautogui.position()
                                            pyautogui.moveTo(position[0] - cursorMod2, position[1])
                                        elif (eye_pupil_x > safeEyeAreaEnd[0]):
                                            cursorMod2 = mod2X * rightlookX
                                            position = pyautogui.position()
                                            pyautogui.moveTo(position[0] + cursorMod2, position[1])

                                    if np.all((leftEyePupils == None)) or np.all((rightEyePupils == None)):
                                        if (left_eye_ratio > blinking_ratio and left_eye_ratio > 5.7 and np.all(leftEyePupils == None)
                                                and np.all(rightEyePupils != None)):
                                            pyautogui.click(button="left")
                                        elif (right_eye_ratio > blinking_ratio and right_eye_ratio > 5.7 and np.all(rightEyePupils == None)
                                              and np.all(leftEyePupils != None)):
                                            pyautogui.click(button="right")

                        except:
                            pass

                    if ret:
                        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                        Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                        self.ImageUpdate.emit(Pic)
                except:
                    pass


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec_())

