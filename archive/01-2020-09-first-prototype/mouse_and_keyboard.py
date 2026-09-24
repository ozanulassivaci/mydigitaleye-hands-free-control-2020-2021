import cv2
import numpy as np
from math import hypot
import time
import pyglet
import dlib
import pyautogui

cam = cv2.VideoCapture(0)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

font = cv2.FONT_HERSHEY_SIMPLEX



while True:
    ret,frame = cam.read()
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    for face in faces:

        x, y = face.left() , face.top()
        x1, y1 = face.right() , face.bottom()
        cv2.rectangle(frame,(x, y), (x1, y1), (0,0,255),1)

        landmarks = predictor(gray,face)

        left_eye_region = np.array([(landmarks.part(36).x,landmarks.part(36).y),
                                   (landmarks.part(37).x, landmarks.part(37).y),
                                   (landmarks.part(38).x, landmarks.part(38).y),
                                   (landmarks.part(39).x, landmarks.part(39).y),
                                   (landmarks.part(40).x, landmarks.part(40).y),
                                   (landmarks.part(41).x, landmarks.part(41).y)],np.int32)
        #cv2.polylines(frame,[left_eye_region],True,(0,51,255),1)

        lp1 = (landmarks.part(36).x,landmarks.part(36).y)
        lp2 = (landmarks.part(37).x,landmarks.part(37).y)
        lp3 = (landmarks.part(38).x,landmarks.part(38).y)
        lp4 = (landmarks.part(39).x,landmarks.part(39).y)
        lp5 = (landmarks.part(40).x,landmarks.part(40).y)
        lp6 = (landmarks.part(41).x,landmarks.part(41).y)

        min_x = np.min(left_eye_region[:,0])
        min_y = np.min(left_eye_region[:,1])
        max_x = np.max(left_eye_region[:,0])
        max_y = np.max(left_eye_region[:,1])

        eye = frame[min_y:max_y,min_x:max_x]
        eye = cv2.resize(eye,None,fx=5,fy=5)

        height, width , _ = frame.shape
        mask = np.zeros((height,width),np.uint8)
        cv2.fillPoly(mask,[left_eye_region],255)
        left_eye = cv2.bitwise_and(gray,gray,mask = mask)
        gray_eye = left_eye[min_y:max_y,min_x: max_x]
        _,threshold_eye = cv2.threshold(gray_eye,20,255,cv2.THRESH_BINARY)
        threshold_eye = cv2.resize(threshold_eye,None,fx=5,fy=5)
        gray_eye = cv2.cvtColor(eye,cv2.COLOR_BGR2GRAY)

        gray_blurred = cv2.blur(gray_eye, (3, 3))

        # Apply Hough transform on the blurred image.
        detected_circles = cv2.HoughCircles(gray_blurred,
                                            cv2.HOUGH_GRADIENT, 1, 999, param1=11,
                                            param2=9, minRadius=30, maxRadius=45)
        # Draw circles that are detected.
        if detected_circles is not None:

            # Convert the circle parameters a, b and r to integers.
            detected_circles = np.uint16(np.around(detected_circles))

            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]


                cv2.circle(eye, (a, b), r, (0, 255, 0), 2)

                cv2.circle(eye, (a, b), 1, (0, 0, 255), 3)



        cv2.imshow("gray",gray_eye)
        a = abs(lp2[1]-lp6[1])
        b = abs(lp3[1]-lp5[1])
        c = 2*abs(lp1[0]-lp4[0])
        

        ear = (a+b)/c

        print(ear)

        cv2.imshow("threshold",threshold_eye)
        cv2.imshow("Frame",frame)
        cv2.imshow("eye",eye)

    key = cv2.waitKey(1)
    if key & 0xFF == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()