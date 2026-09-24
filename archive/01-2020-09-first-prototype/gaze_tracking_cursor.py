"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
import numpy as np
from math import hypot
import time
import pyglet
import dlib
import pyautogui

detector = dlib.get_frontal_face_detector()
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

screen_center = (pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
pyautogui.moveTo(screen_center)

def midPoint(p1,p2):
    return int((p1.x + p2.x)/2),int((p1.y + p2.y)/2)

while True:
    _, frame1 = webcam.read()
    frame1 = cv2.flip(frame1,1)
    gray =cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    # We get a new frame from the webcam
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)

    # We send this frame to GazeTracking to analyze it dddd
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking_v1.0"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    #cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 2)
    #cv2.putText(frame, "Right pupil: " + str(right_pupil), (10, 65), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 2)

    for face in faces:
        landmarks = predictor(gray, face)
        left_point = (landmarks.part(36).x,landmarks.part(36).y)
        right_point = (landmarks.part(39).x, landmarks.part(39).y)
        center_top = midPoint(landmarks.part(37),landmarks.part(38))
        center_bottom = midPoint(landmarks.part(40), landmarks.part(41))

        #hor_line = cv2.line(frame1, left_point, right_point, (0, 255, 0), 2)
        #ver_line = cv2.line(frame1, center_top, center_bottom, (0, 255, 0), 2)

        eye_ver=((landmarks.part(36).x + landmarks.part(39).x)//2)
        eye_hor=((landmarks.part(41).y - landmarks.part(37).y) // 2 + landmarks.part(37).y)
        eye_center = (eye_ver,eye_hor)
        cv2.circle(frame1,eye_center,1,(0,0,255),2)
        cv2.putText(frame,"Eye center: "+str(eye_center),(10,100),cv2.FONT_HERSHEY_DUPLEX,0.9,(147,58,31),2)


        #left_pupil[0]-eye_ver,eye_hor-left_pupil[1]

        if eye_center[0]<=left_pupil[0] and eye_center[1]>left_pupil[1]:
            print("1")
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(pyautogui.position()[0]+25*(left_pupil[0]-eye_center[0]),pyautogui.position()[1]-25*(eye_center[1]-left_pupil[1]))
        elif eye_center[0]>=left_pupil[0] and eye_center[1]-1>left_pupil[1]:
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(pyautogui.position()[0]-25*(eye_center[0]-left_pupil[0]),pyautogui.position()[1]-25*(eye_center[1]-left_pupil[1]))
            print("2")
        elif eye_center[0]>=left_pupil[0] and eye_center[1]-3<=left_pupil[1]:
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(pyautogui.position()[0]-25*(eye_center[0]-left_pupil[0]),pyautogui.position()[1]+25*((left_pupil[1]+3)-eye_center[1]-1))
            print("3")
        elif eye_center[0]<=left_pupil[0] and eye_center[1]-1<=left_pupil[1]:
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(pyautogui.position()[0]+25*(left_pupil[0]-eye_center[0]),pyautogui.position()[1]+25*((left_pupil[1]+3)-eye_center[1]-1))
            print("4")

        else:
            pass





    cv2.imshow("frame",frame1)


    cv2.imshow("Demo", frame)
    key = cv2.waitKey(1)
    if key & 0xFF == ord("q"):
        break
"""
while True:
    _, frame1 = webcam.read()
    gray =cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        left_point = (landmarks.part(36).x,landmarks.part(36).y)
        right_point = (landmarks.part(39).x, landmarks.part(39).y)
        center_top = midPoint(landmarks.part(37),landmarks.part(38))
        center_bottom = midPoint(landmarks.part(40), landmarks.part(41))

        hor_line = cv2.line(frame1, left_point, right_point, (0, 255, 0), 2)
        ver_line = cv2.line(frame1, center_top, center_bottom, (0, 255, 0), 2)
    cv2.imshow("frame",frame1)
    key = cv2.waitKey(1)
    if key & 0xFF == ord("q"):
        break
"""


webcam.release()
cv2.destroyAllWindows()