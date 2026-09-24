import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2  # ver 4.4.0.42
import dlib  # ver 19.8.1
import numpy as np  # ver 1.19.2
from math import hypot
import pyautogui
import datetime
import time
from playsound import playsound
a = 0


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        title = "Face Cursor"
        self.setWindowTitle(title)

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        #self.CancelBTN = QPushButton("Exit")
        #self.CancelBTN.clicked.connect(self.CancelFeed)
        #self.VBL.addWidget(self.CancelBTN)

        self.Worker1 = Worker1()

        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()
        global a
        a += 1


class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        #Capture = cv2.VideoCapture(0)

        webcam = cv2.VideoCapture(0)

        detector = dlib.get_frontal_face_detector()  # dlib ön yüz bulma
        predictor = dlib.shape_predictor(
            "./shape_predictor_68_face_landmarks.dat")  # dlib yüzdeki noktaları (0-67) birleştirmek için

        red = (0, 0, 255)
        blue = (255, 0, 0)  # renk kodları ve font
        green = (0, 255, 0)
        font = cv2.FONT_HERSHEY_DUPLEX

        leftEyeCoordinate = (" ")
        rightEyeCoordinate = (" ")
        eyeCoordinate = (" ")
        strBlinkingRatio = (" ")

        modChoiceEx = 0
        mod1Choice = 0
        mod2Choice = 0
        # mod3Choice = 0

        first = datetime.datetime.now()
        firstSecond = first.strftime("%S")

        secondSet = set()
        second = 11
        secondPass = 0

        leftEyePupils = None
        rightEyePupils = None

        pause_time_list = list()
        pause_set = set()
        pause_blinking = 0
        pause_now = datetime.datetime.now()
        pause_seconds = time.mktime(pause_now.timetuple())
        pause_seconds = int(pause_seconds)

        continue_time_list = list()
        continue_set = set()
        continue_blinking = 0
        continue_now = datetime.datetime.now()
        continue_seconds = time.mktime(continue_now.timetuple())
        continue_seconds = int(continue_seconds)

        desktop_time_list = list()
        desktop_set = set()
        desktop_blinking = 0
        desktop_now = datetime.datetime.now()
        desktop_seconds = time.mktime(desktop_now.timetuple())
        desktop_seconds = int(desktop_seconds)

        keyboard_time_list = list()
        keyboard_set = set()
        keyboard_blinking = 0
        keyboard_now = datetime.datetime.now()
        keyboard_seconds = time.mktime(keyboard_now.timetuple())
        keyboard_seconds = int(keyboard_seconds)

        file_time_list = list()
        file_set = set()
        file_blinking = 0
        file_now = datetime.datetime.now()
        file_seconds = time.mktime(file_now.timetuple())
        file_seconds = int(file_seconds)

        second_now = datetime.datetime.now()
        now_seconds = time.mktime(second_now.timetuple())
        now_seconds = int(now_seconds)

        def midPoint(p1, p2):
            return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)
            # girilen iki noktanın ortasını bulma gerekli değil fakat sayısal işlemler gözüme batsın istemedim

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
            # left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
            # right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
            center_top = midPoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
            center_bottom = midPoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

            # hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 1)
            # ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 1)

            hor_line_lenght = hor([36, 39, 42, 45], facial_landmarks)
            # hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
            ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

            ratio = round(hor_line_lenght / ver_line_lenght, 1)
            return ratio

        def eyeCenter(eye_points, facial_landmarks):
            # göz oratsı bulma fonksiyonu
            # göz nokaları sırası ile girildiği zaman [36, 37, 38, 39, 40, 41] gibi göz ortasını bulur
            eyeXTop = ((facial_landmarks.part(eye_points[2]).x - facial_landmarks.part(
                eye_points[1]).x) / 2 + facial_landmarks.part(eye_points[1]).x)
            eyeXBottom = ((facial_landmarks.part(eye_points[4]).x - facial_landmarks.part(
                eye_points[5]).x) / 2 + facial_landmarks.part(eye_points[5]).x)
            eyeX = int((eyeXTop + eyeXBottom) // 2)

            center_top = midPoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
            center_bottom = midPoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

            ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

            eye_y = int(ver_line_lenght // 3)

            # göz ortasının x değerini bulmak için gözdeki en üst ([37-38]gibi) veya en alttaki ([41-40]gibi) iki noktanın ortasını bulmak gerekir
            # yüksek doğruluk için toplayıp ikiye böldüm
            eyeY1 = (int((facial_landmarks.part(eye_points[5]).y - facial_landmarks.part(
                eye_points[1]).y) // 2) + facial_landmarks.part(eye_points[1]).y)
            eyeY2 = (int((facial_landmarks.part(eye_points[4]).y - facial_landmarks.part(
                eye_points[2]).y) // 2) + facial_landmarks.part(eye_points[2]).y)
            eyeY = int((eyeY1 + eyeY2) // 2)
            eyeCoordinate = (eyeX, eyeY)
            # göz ortasının y değerini bulmak için gözdeki en sol nokta ([36]gibi) veya en sağ nokta ([39]gibi) nın y sini bulmak gerekir yüksek doğruluk için toplayıp iki ye böldüm
            # çıkan değerler float olacaktır sonradan değiştirilebilir
            return eyeCoordinate

        def down_look(eye_points, facial_landmarks):
            # [19,41,24,46]
            hor4 = hor([36, 39, 42, 45], landmarks)
            ver4 = (((facial_landmarks.part(eye_points[1]).y - facial_landmarks.part(eye_points[0]).y) + (
                        facial_landmarks.part(eye_points[3]).y - facial_landmarks.part(eye_points[2]).y)) // 2)
            rat = round(ver4 / hor4, 2)
            return rat

        def isolate_eye(frame, landmarks, points):
            region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points])
            region = region.astype(np.int32)

            # Applying a mask to get only the eye
            height, width = frame.shape[:2]
            black_frame = np.zeros((height, width), np.uint8)
            mask = np.full((height, width), 255, np.uint8)
            cv2.fillPoly(mask, [region], (0, 0, 0))
            eye = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)

            # Cropping on the eye
            margin = 5
            min_x = np.min(region[:, 0]) - margin
            max_x = np.max(region[:, 0]) + margin
            min_y = np.min(region[:, 1]) - margin
            max_y = np.max(region[:, 1]) + margin

            eye_frame = frame[min_y:max_y, min_x:max_x]
            new_frame = eye[min_y:max_y, min_x:max_x]
            origin = (min_x, min_y)

            height, width = frame.shape[:2]
            center = (width / 2, height / 2)

            return eye_frame, min_x, max_x, min_y, max_y

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
                    cv2.putText(frame, f"Mod Secmenin Baslamasina {secondFrame}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0))
                    cv2.putText(frame, "Mod 1 Sol gozunuzu kirpin", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, green)
                    cv2.putText(frame, "Mod 2 Sag gozunuzu kirpin", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, green)
                    # cv2.putText(frame, "Mod 3 Iki gozunuzu kirpin", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, green)

                    if len(secondSet) == 11:
                        secondPass += 1
                        # print(secondPass)

                for face in faces:

                    # göz alanı bulma göz bebeği bulma vs gibi yüz içindeki şeyleri yüz dışında aramaya gerek yok

                    landmarks = predictor(gray, face)  # artık yüzdeki noktalar ile işlem yapabileceğiz

                    left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
                    right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
                    blinking_ratio = round((left_eye_ratio + right_eye_ratio) / 2, 2)

                    down_ratio = down_look([19, 41, 24, 46], landmarks)
                    # print(blinking_ratio)
                    # print("sol goz: " + str(left_eye_ratio) + " sag goz: " + str(right_eye_ratio) + " average: " + str(blinking_ratio))
                    # sol ve sağ gözün kırpma oranını bulup toplayıp ikiye böldük yüksek doğruluk için

                    while modChoiceEx == 0 and secondPass > 0:

                        cv2.putText(frame, "Mod 1 Sol gozunuzu kirpin", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, green)
                        cv2.putText(frame, "Mod 2 Sag gozunuzu kirpin", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, green)
                        # cv2.putText(frame,"Mod 3 Iki gozunuzu kirpin",(10,150),cv2.FONT_HERSHEY_SIMPLEX,1,green)

                        a = np.all((left_eye_ratio > 4) and (right_eye_ratio < 4.5) and (
                                    left_eye_ratio > right_eye_ratio) and (leftEyePupils == None))
                        b = np.all(
                            (right_eye_ratio > 4) and (left_eye_ratio < 5) and (right_eye_ratio > left_eye_ratio) and (
                                        rightEyePupils == None))

                        if a:
                            mod1Choice += 1
                        elif b:
                            mod2Choice += 1
                        break

                    if mod1Choice > 1 or mod2Choice > 1:
                        modChoiceEx += 1
                        # cv2.destroyWindow("modChoice")

                    if mod1Choice >= 2 and (mod2Choice == 1 or mod2Choice == 0):

                        noiseAreaX = int((landmarks.part(16).x - landmarks.part(0).x) // 10)
                        noiseAreaY = int((landmarks.part(12).y - landmarks.part(0).y) // 5)

                        noiseAreaStart = (landmarks.part(0).x - noiseAreaX, landmarks.part(0).y - noiseAreaY)
                        noiseAreaEnd = (landmarks.part(16).x + noiseAreaX, landmarks.part(12).y + noiseAreaY)

                        zeroPointX = ((noiseAreaEnd[0] + noiseAreaStart[0]) // 2)
                        zeroPointY = ((noiseAreaStart[1] + noiseAreaEnd[1]) // 2)

                        cv2.rectangle(frame, noiseAreaStart, noiseAreaEnd, red, 2)

                        noise = (landmarks.part(30).x, landmarks.part(30).y)

                        cv2.circle(frame, noise, 2, blue, -1)
                        cv2.circle(frame, (zeroPointX, zeroPointY), 2, red, -1)

                        safeAreaX = int((noiseAreaEnd[0] - noiseAreaStart[0]) // 8)
                        safeAreStart = (zeroPointX - safeAreaX, zeroPointY - int(safeAreaX // 2))
                        safeAreEnd = (zeroPointX + safeAreaX, zeroPointY + safeAreaX)

                        cv2.rectangle(frame, safeAreStart, safeAreEnd, blue, 2)

                        if np.all((leftEyePupils == None)) and np.all(
                                (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                pause_set) == 0 and down_ratio < 1.10:
                            pause_blinking += 1
                            pause_now = datetime.datetime.now()
                            pause_seconds = time.mktime(pause_now.timetuple())
                            pause_seconds = int(pause_seconds)
                            pause_time_list.append(pause_seconds)
                            if pause_blinking >= 25 and (now_seconds - int(pause_time_list[0])) <= 5:
                                pause_set.add(1)
                                pause_blinking = 0
                                pause_time_list.clear()
                                playsound("./stop.mp3")
                                # print("durdu")
                            elif pause_blinking < 25 and (now_seconds - pause_time_list[0]) > 5:
                                pause_blinking = 0
                                pause_time_list.clear()

                        if np.all((leftEyePupils == None)) and np.all(
                                (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                pause_set) == 1 and down_ratio < 1.10:
                            continue_blinking += 1
                            continue_now = datetime.datetime.now()
                            continue_seconds = time.mktime(continue_now.timetuple())
                            continue_seconds = int(continue_seconds)
                            continue_time_list.append(continue_seconds)
                            if continue_blinking >= 25 and (now_seconds - int(continue_time_list[0])) <= 5:
                                pause_set.clear()
                                continue_time_list.clear()
                                continue_blinking = 0
                                playsound("./start.mp3")
                                # print("dewamke")
                            elif continue_blinking < 25 and (now_seconds - int(continue_time_list[0])) > 5:
                                continue_blinking = 0
                                continue_time_list.clear()

                        if len(pause_set) == 0:

                            desktop_left = (left_eye_ratio > 4) and (right_eye_ratio < 4.5) and (
                                    left_eye_ratio > right_eye_ratio) and np.all(leftEyePupils == None) and np.all(
                                rightEyePupils != None)

                            if desktop_left:
                                desktop_blinking += 1
                                desktop_now = datetime.datetime.now()
                                desktop_seconds = time.mktime(desktop_now.timetuple())
                                desktop_seconds = int(desktop_seconds)
                                desktop_time_list.append(desktop_seconds)
                                if desktop_blinking >= 15 and (now_seconds - int(desktop_time_list[0])) <= 5:
                                    desktop_time_list.clear()
                                    desktop_blinking = 0
                                    pyautogui.hotkey("win", "d")
                                    playsound("./desktop.mp3")
                                elif desktop_blinking < 25 and (now_seconds - int(desktop_time_list[0])) > 5:
                                    desktop_blinking = 0
                                    desktop_time_list.clear()

                            keyboard_right = (right_eye_ratio > 4) and (left_eye_ratio < 5) and (
                                    right_eye_ratio > left_eye_ratio) and np.all((rightEyePupils == None)) and np.all(
                                (leftEyePupils != None))

                            if keyboard_right:
                                keyboard_blinking += 1
                                keyboard_now = datetime.datetime.now()
                                keyboard_seconds = time.mktime(keyboard_now.timetuple())
                                keyboard_seconds = int(keyboard_seconds)
                                keyboard_time_list.append(keyboard_seconds)
                                if keyboard_blinking >= 15 and (now_seconds - int(keyboard_time_list[0])) <= 5:
                                    keyboard_time_list.clear()
                                    keyboard_blinking = 0
                                    pyautogui.hotkey("win", "ctrl", "o")
                                    playsound("./keyboard.mp3")
                                elif keyboard_blinking < 25 and (now_seconds - int(keyboard_time_list[0])) > 5:
                                    keyboard_blinking = 0
                                    keyboard_time_list.clear()

                            if np.all((leftEyePupils == None)) and np.all(
                                    (rightEyePupils == None)) and blinking_ratio > 5.7 and down_ratio > 1.15:
                                file_blinking += 1
                                file_now = datetime.datetime.now()
                                file_seconds = time.mktime(file_now.timetuple())
                                file_seconds = int(file_seconds)
                                file_time_list.append(file_seconds)
                                if file_blinking >= 25 and (now_seconds - int(file_time_list[0])) <= 5:
                                    file_time_list.clear()
                                    file_blinking = 0
                                    pyautogui.hotkey("win", "e")
                                    playsound("./file.mp3")
                                elif file_blinking < 25 and (now_seconds - int(file_time_list[0])) > 5:
                                    file_blinking = 0
                                    file_time_list.clear()

                            if (zeroPointY - int(safeAreaX // 2) > noise[1]):
                                cursorMod1 = noise[1] - (zeroPointY - int(safeAreaX // 2))
                                position = pyautogui.position()
                                pyautogui.moveTo(position[0], position[1] + (2 * cursorMod1))
                            elif (noise[1] > zeroPointY + safeAreaX):
                                cursorMod1 = (zeroPointY + safeAreaX) - noise[1]
                                position = pyautogui.position()
                                pyautogui.moveTo(position[0], position[1] - (2 * cursorMod1))
                            elif (noise[0] > zeroPointX + safeAreaX):
                                cursorMod1 = noise[0] - (zeroPointX + safeAreaX)
                                position = pyautogui.position()
                                pyautogui.moveTo(position[0] + (2 * cursorMod1), position[1])
                            elif (zeroPointX - safeAreaX > noise[0]):
                                cursorMod1 = (zeroPointX - safeAreaX) - noise[0]
                                position = pyautogui.position()
                                pyautogui.moveTo(position[0] - (2 * cursorMod1), position[1])

                            mod1a = np.all((left_eye_ratio > 4) and (right_eye_ratio < 4.5) and (
                                        left_eye_ratio > right_eye_ratio) and (leftEyePupils == None))
                            mod1b = np.all((right_eye_ratio > 4) and (left_eye_ratio < 5) and (
                                        right_eye_ratio > left_eye_ratio) and (rightEyePupils == None))

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

                        leftEyeCenterCoordinate = eyeCenter([36, 37, 38, 39, 40, 41], landmarks)
                        leftEyeCenterCoordinate = (
                        leftEyeCenterCoordinate[0] - isolate_eye(frame, landmarks, [36, 37, 38, 39, 40, 41])[1],
                        leftEyeCenterCoordinate[1] - isolate_eye(frame, landmarks, [36, 37, 38, 39, 40, 41])[3])

                        rightEyeCenterCoordinate = eyeCenter([42, 43, 44, 45, 46, 47], landmarks)
                        rightEyeCenterCoordinate = (
                        rightEyeCenterCoordinate[0] - isolate_eye(frame, landmarks, [42, 43, 44, 45, 46, 47])[1],
                        rightEyeCenterCoordinate[1] - isolate_eye(frame, landmarks, [42, 43, 44, 45, 46, 47])[3])

                        #strBlinkingRatio = ("Blinking Ratio: " + str(blinking_ratio))

                        #eyeCoordinate = ("Left Eye Center Cor: " + str(
                        #    leftEyeCenterCoordinate) + " --- " + "Right Eye Center Cor: " + str(
                        #    rightEyeCenterCoordinate))

                    except:
                        pass

                    try:

                        # yüze bakan ışık olmalı çalışması için

                        param_1 = 300
                        param_2 = 5
                        maxradius = 10
                        minradius = 1

                        leftEyePupils = cv2.HoughCircles(isolate_left_blur, cv2.HOUGH_GRADIENT, 1, 999, param1=param_1,
                                                         param2=param_2, maxRadius=maxradius, minRadius=minradius)
                        # gözü sığdırabileceğimiz en küçük alanda göz bebeği bulup daire içine alıyoruz
                        # param 1 değeri ne kadar azalırsa o kadar çok daire bulur
                        # param 2 değeri ne kadar artarsa o kadar az daire bulur
                        # maxRadius en fazla çap minRadius en az çap
                        # bu değerlerle oynayıp doğruluk oranı değiştirilebilir

                        leftEyePupils = np.uint16(np.around(leftEyePupils))

                        for i in leftEyePupils[0, :]:
                            # dış daire çizimi
                            leftEyeCircle = cv2.circle(isolate_left, (i[0], i[1]), i[2], green, 1)
                            # iç daire çizimi
                            leftEyeCircleIn = cv2.circle(isolate_left, (i[0], i[1]), 2, red, 1)

                            # göz bebeğinin koordinatını bulmak için iç veya dış dairenin konumunu yazmak yeterlidir

                            leftEyePupilX = (i[0])
                            leftEyePupilY = (i[1])

                            leftEyePupilCoordinate = (leftEyePupilX, leftEyePupilY)

                            leftEyeFrameResize = cv2.resize(isolate_left, None, fx=10, fy=10)

                            #cv2.imshow("leftEyePupil", leftEyeFrameResize)

                            leftEyeCoordinate = ("Left Eye Pupil Cor: " + str(leftEyePupilCoordinate))

                    except:
                        pass

                    try:

                        param_1 = 300
                        param_2 = 5
                        maxradius = 10
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

                            rightEyeFrameResize = cv2.resize(isolate_right, None, fx=10, fy=10)

                            #cv2.imshow("rightEyePupil", rightEyeFrameResize)

                            rightEyeCoordinate = ("Right Eye Pupil Cor: " + str(rightEyePupilCoordinate))
                    except:
                        pass

                    try:

                        rightlookX = int(((leftEyePupilCoordinate[0] - leftEyeCenterCoordinate[0]) + (
                                    rightEyePupilCoordinate[0] - rightEyeCenterCoordinate[0])) // 2)
                        leftlookX = int(((leftEyeCenterCoordinate[0] - leftEyePupilCoordinate[0]) + (
                                    rightEyeCenterCoordinate[0] - rightEyePupilCoordinate[0])) // 2)
                        uplookX = int(((leftEyeCenterCoordinate[1] - leftEyePupilCoordinate[1]) + (
                                    rightEyeCenterCoordinate[1] - rightEyePupilCoordinate[1])) // 2)
                        bottomarrow = int(((leftEyePupilCoordinate[1] - leftEyeCenterCoordinate[1]) + (
                                    rightEyePupilCoordinate[1] - rightEyeCenterCoordinate[1])) // 2)

                        eye_pupil_x = int((rightEyePupilCoordinate[0] + leftEyePupilCoordinate[0]) // 2)
                        eye_center_x = int((rightEyeCenterCoordinate[0] + leftEyeCenterCoordinate[0]) // 2)
                        eye_pupil_y = int((rightEyePupilCoordinate[1] + leftEyePupilCoordinate[1]) // 2)
                        eye_center_y = int((rightEyeCenterCoordinate[1] + leftEyeCenterCoordinate[1]) // 2)

                        hor_line_lenght = int(hor([36, 39, 42, 45], landmarks) // 8)

                        safeEyeAreaStart = (eye_center_x - hor_line_lenght, eye_center_y - hor_line_lenght)
                        safeEyeAreaEnd = (eye_center_x + hor_line_lenght, eye_center_y + hor_line_lenght)

                        # cv2.rectangle(leftEyeFrame,safeEyeAreaStart,safeEyeAreaEnd,blue,1)

                        asd = ("eye_pupil_x: " + str(eye_pupil_x) + " eye_pupil_y: " + str(
                            eye_pupil_y) + " eye_center_x: " + str(eye_center_x) + " eye_cemter_y: " + str(
                            eye_center_y))
                        # print(asd)

                        if mod2Choice >= 2 and (mod1Choice == 1 or mod1Choice == 0):

                            if np.all((leftEyePupils == None)) and np.all(
                                    (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                pause_set) == 0 and down_ratio < 1.10:
                                pause_blinking += 1
                                pause_now = datetime.datetime.now()
                                pause_seconds = time.mktime(pause_now.timetuple())
                                pause_seconds = int(pause_seconds)
                                pause_time_list.append(pause_seconds)
                                if pause_blinking >= 25 and (now_seconds - int(pause_time_list[0])) <= 5:
                                    pause_set.add(1)
                                    pause_blinking = 0
                                    pause_time_list.clear()
                                    playsound("./stop.mp3")
                                    # print("durdu")
                                elif pause_blinking < 25 and (now_seconds - pause_time_list[0]) > 5:
                                    pause_blinking = 0
                                    pause_time_list.clear()

                            if np.all((leftEyePupils == None)) and np.all(
                                    (rightEyePupils == None)) and blinking_ratio > 5.7 and len(
                                pause_set) == 1 and down_ratio < 1.10:
                                continue_blinking += 1
                                continue_now = datetime.datetime.now()
                                continue_seconds = time.mktime(continue_now.timetuple())
                                continue_seconds = int(continue_seconds)
                                continue_time_list.append(continue_seconds)
                                if continue_blinking >= 25 and (now_seconds - int(continue_time_list[0])) <= 5:
                                    pause_set.clear()
                                    continue_time_list.clear()
                                    continue_blinking = 0
                                    playsound("./start.mp3")
                                    # print("dewamke")
                                elif continue_blinking < 25 and (now_seconds - int(continue_time_list[0])) > 5:
                                    continue_blinking = 0
                                    continue_time_list.clear()

                            if len(pause_set) == 0:

                                desktop_left = (left_eye_ratio > 4) and (right_eye_ratio < 4.5) and (
                                        left_eye_ratio > right_eye_ratio) and np.all(leftEyePupils == None) and np.all(
                                    rightEyePupils != None)

                                desktop_left = (left_eye_ratio > 4) and (right_eye_ratio < 4.5) and (
                                        left_eye_ratio > right_eye_ratio) and np.all(leftEyePupils == None) and np.all(
                                    rightEyePupils != None)

                                if desktop_left:
                                    desktop_blinking += 1
                                    desktop_now = datetime.datetime.now()
                                    desktop_seconds = time.mktime(desktop_now.timetuple())
                                    desktop_seconds = int(desktop_seconds)
                                    desktop_time_list.append(desktop_seconds)
                                    if desktop_blinking >= 15 and (now_seconds - int(desktop_time_list[0])) <= 5:
                                        desktop_time_list.clear()
                                        desktop_blinking = 0
                                        pyautogui.hotkey("win", "d")
                                        playsound("./desktop.mp3")
                                    elif desktop_blinking < 15 and (now_seconds - int(desktop_time_list[0])) > 5:
                                        desktop_blinking = 0
                                        desktop_time_list.clear()

                                keyboard_right = (right_eye_ratio > 4) and (left_eye_ratio < 5) and (
                                        right_eye_ratio > left_eye_ratio) and np.all(
                                    (rightEyePupils == None)) and np.all(
                                    (leftEyePupils != None))

                                if keyboard_right:
                                    keyboard_blinking += 1
                                    keyboard_now = datetime.datetime.now()
                                    keyboard_seconds = time.mktime(keyboard_now.timetuple())
                                    keyboard_seconds = int(keyboard_seconds)
                                    keyboard_time_list.append(keyboard_seconds)
                                    if keyboard_blinking >= 15 and (now_seconds - int(keyboard_time_list[0])) <= 5:
                                        keyboard_time_list.clear()
                                        keyboard_blinking = 0
                                        pyautogui.hotkey("win", "ctrl", "o")
                                        playsound("./keyboard.mp3")
                                    elif keyboard_blinking < 15 and (now_seconds - int(keyboard_time_list[0])) > 5:
                                        keyboard_blinking = 0
                                        keyboard_time_list.clear()

                                if np.all((leftEyePupils == None)) and np.all(
                                        (rightEyePupils == None)) and blinking_ratio > 5.7 and down_ratio > 1.15:
                                    file_blinking += 1
                                    file_now = datetime.datetime.now()
                                    file_seconds = time.mktime(file_now.timetuple())
                                    file_seconds = int(file_seconds)
                                    file_time_list.append(file_seconds)
                                    if file_blinking >= 25 and (now_seconds - int(file_time_list[0])) <= 5:
                                        file_time_list.clear()
                                        file_blinking = 0
                                        pyautogui.hotkey("win", "e")
                                        playsound("./file.mp3")
                                    elif file_blinking < 25 and (now_seconds - int(file_time_list[0])) > 5:
                                        file_blinking = 0
                                        file_time_list.clear()

                                if np.all((leftEyePupils != None)) and np.all((rightEyePupils != None)) and len(
                                        pause_set) == 0:
                                    if (eye_pupil_y < safeEyeAreaStart[1]):
                                        cursorMod2 = 6 * uplookX
                                        position = pyautogui.position()
                                        pyautogui.moveTo(position[0], position[1] - cursorMod2)
                                    elif (down_ratio > 1.20):
                                        cursorMod2 = 15
                                        position = pyautogui.position()
                                        pyautogui.moveTo(position[0], position[1] + cursorMod2)
                                    elif (eye_pupil_x < safeEyeAreaStart[0]):
                                        cursorMod2 = 6 * leftlookX
                                        position = pyautogui.position()
                                        pyautogui.moveTo(position[0] - cursorMod2, position[1])
                                    elif (eye_pupil_x > safeEyeAreaEnd[0]):
                                        cursorMod2 = 6 * rightlookX
                                        position = pyautogui.position()
                                        pyautogui.moveTo(position[0] + cursorMod2, position[1])

                                if np.all((leftEyePupils == None)) or np.all((rightEyePupils == None)):
                                    if (left_eye_ratio > 4) and (right_eye_ratio < 4.5) and (
                                            left_eye_ratio > right_eye_ratio) and (
                                            leftEyePupils == None):
                                        pyautogui.click(button="left")
                                    elif (right_eye_ratio > 4) and (left_eye_ratio < 5) and (
                                            right_eye_ratio > left_eye_ratio) and (
                                            rightEyePupils == None):
                                        pyautogui.click(button="right")

                    except:
                        pass

                    # göz bebeği bulmayı göz kırpmanın else ine aldım çünkü göz kapalı iken  göz bebeği bulamazsın
                    # bu işlem de gecikmeler olabilir mesela göz kapandığı zaman kapandığını geç algılayabilir bu
                    # süre zarfında kapalı gözde göz bebeği bulamayacağı için kod hata verir bunun önüne geçmek için
                    # try except içine aldım

                if ret:
                    Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # FlippedImage = cv2.flip(Image, 1)
                    ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                    Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.ImageUpdate.emit(Pic)


    def stop(self):
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())
