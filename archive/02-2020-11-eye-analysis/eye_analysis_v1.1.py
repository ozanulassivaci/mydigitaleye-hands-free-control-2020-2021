#kodun doğru çalışması için
#1) arkanızda yüksek ışık kaynağı olmamalı
#2) yüzünüz aydınlatılmış olmalı
#3) kafanız düz bir şekilde ekrana bakmalı
#4) bilgisayar ekranınana yakınlık 40cm - 100cm

#python                ver 3.6.12

import cv2            #ver 4.4.0.42
import dlib           #ver 19.8.1
import numpy as np    #ver 1.19.2
from math import hypot

#kodları anlamak için dlib yüz noktalarına bakınız (0-67)

webcam = cv2.VideoCapture(0)

detector = dlib.get_frontal_face_detector() #dlib ön yüz bulma
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat") #dlib yüzdeki noktaları (0-67) birleştirmek için

red = 	(0,0,255)
blue = (255,0,0)  # renk kodları ve font
green = (0,255,0)
font = cv2.FONT_HERSHEY_DUPLEX

leftEyeCoordinate = (" ")
rightEyeCoordinate = (" ")
eyeCoordinate = (" ")
strBlinkingRatio = (" ")

def midPoint(p1,p2):
    return int((p1.x + p2.x)/2),int((p1.y + p2.y)/2)
    #girilen iki noktanın ortasını bulma gerekli değil fakat sayısal işlemler gözüme batsın istemedim

def get_blinking_ratio(eye_points, facial_landmarks):
    #göz  kırpma oranı bulma fonksiyonu fare işlemleri için gerekir
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midPoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midPoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))
    #göz noktaları sırası ile girildiği zaman [36, 37, 38, 39, 40, 41] gibi sol sağ üst ve alt noktalarını bulma

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    #bir gözümüzün solundan mesela sol gözün solundan (36) noktası sağıyla (39) noktası tamamen paralel konumda olmayabilir
    #birisinin y sinin farlı olduğu durumda soldan sağa uzunluğu ölçmek için pisagor bağıntısı gerekir
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    #burda da aynı durumun gözün üstünden altına olan uzaklıktada geçerli olacaktır

    ratio = hor_line_lenght / ver_line_lenght
    #bunları oranlıyoruz ki çıkan değerleri test ederek hangi durumda göz kırpılmış anlayabilelim
    return ratio

def eyeCenter(eye_points, facial_landmarks):
    #göz oratsı bulma fonksiyonu
    #göz nokaları sırası ile girildiği zaman [36, 37, 38, 39, 40, 41] gibi göz ortasını bulur
    eyeXTop = ((facial_landmarks.part(eye_points[2]).x - facial_landmarks.part(eye_points[1]).x)/2 + facial_landmarks.part(eye_points[1]).x)
    eyeXBottom = ((facial_landmarks.part(eye_points[4]).x - facial_landmarks.part(eye_points[5]).x)/2 + facial_landmarks.part(eye_points[5]).x)
    eyeX = ((eyeXTop + eyeXBottom)/2)
    #göz ortasının x değerini bulmak için gözdeki en üst ([37-38]gibi) veya en alttaki ([41-40]gibi) iki noktanın ortasını bulmak gerekir
    #yüksek doğruluk için toplayıp ikiye böldüm
    eyeY = ((facial_landmarks.part(eye_points[3]).y + facial_landmarks.part(eye_points[0]).y) / 2)
    eyeCoordinate = (eyeX,eyeY)
    #göz ortasının y değerini bulmak için gözdeki en sol nokta ([36]gibi) veya en sağ nokta ([39]gibi) nın y sini bulmak gerekir yüksek doğruluk için toplayıp iki ye böldüm
    #çıkan değerler float olacaktır sonradan değiştirilebilir
    return eyeCoordinate

while True:
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        #göz alanı bulma göz bebeği bulma vs gibi yüz içindeki şeyleri yüz dışında aramaya gerek yok

        landmarks = predictor(gray, face) #artık yüzdeki noktalar ile işlem yapabileceğiz

        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
        # sol ve sağ gözün kırpma oranını bulup toplayıp ikiye böldük yüksek doğruluk için

        leftEyeStartPoint = (landmarks.part(36).x,landmarks.part(17).y-5)
        leftEyeEndPoint = (landmarks.part(39).x,landmarks.part(28).y+5)
        #sol göz bebeğini doğru bulma oranını yüksetlmek için dlib yüz noktalarına göre sol gözün sığdığı en küçük alanı buluyoruz
        #bu işlemi eye haarcascade ile de yapabiliriz fakat ben dlib in performansını daha çok verimli buldum daha sonra gerekirse değiştirilebilir

        leftEyeFrame = frame[leftEyeStartPoint[1]:leftEyeEndPoint[1],leftEyeStartPoint[0]:leftEyeEndPoint[0]]
        #bulup yeni pencereye taşıdık
        leftEyeFrameGray = cv2.cvtColor(leftEyeFrame, cv2.COLOR_BGR2GRAY)
        leftFrameGrayBlur = cv2.medianBlur(leftEyeFrameGray, 5)

        leftEyeCenterCoordinate = eyeCenter([36, 37, 38, 39, 40, 41], landmarks)

        rightEyeStartPoint = (landmarks.part(42).x,landmarks.part(17).y-5) #aynı işlemler sağ göz içinde geçerli
        rightEyeEndPoint = (landmarks.part(45).x,landmarks.part(28).y+5)

        rightEyeFrame = frame[rightEyeStartPoint[1]:rightEyeEndPoint[1],rightEyeStartPoint[0]:rightEyeEndPoint[0]]
        rightEyeFrameGray = cv2.cvtColor(rightEyeFrame, cv2.COLOR_BGR2GRAY)
        rightFrameGrayBlur = cv2.medianBlur(rightEyeFrameGray, 5)

        rightEyeCenterCoordinate = eyeCenter([42, 43, 44, 45, 46, 47], landmarks)

        strBlinkingRatio = ("Blinking Ratio: " + str(blinking_ratio))

        eyeCoordinate = ("Left Eye Center Cor: " + str(leftEyeCenterCoordinate)  + " --- " + "Right Eye Center Cor: " +str(rightEyeCenterCoordinate))

        try:

            if blinking_ratio > 5.5:
                cv2.putText(frame, "BLINKING", (10,50), font , 2, green)
                #göz kırpma tespiti

            else:

                #yüze bakan ışık olmalı çalışması için

                param_1 = 300
                param_2 = 5
                maxradius = 8
                minradius = 4

                leftEyePupils = cv2.HoughCircles(leftFrameGrayBlur,cv2.HOUGH_GRADIENT,1,999,param1=param_1,param2=param_2,maxRadius=maxradius,minRadius=minradius)
                #gözü sığdırabileceğimiz en küçük alanda göz bebeği bulup daire içine alıyoruz
                #param 1 değeri ne kadar azalırsa o kadar çok daire bulur
                #param 2 değeri ne kadar artarsa o kadar az daire bulur
                #maxRadius en fazla çap minRadius en az çap
                #bu değerlerle oynayıp doğruluk oranı değiştirilebilir

                leftEyePupils = np.uint16(np.around(leftEyePupils))

                for i in leftEyePupils[0, :]:

                    # dış daire çizimi
                    leftEyeCircle = cv2.circle(leftEyeFrame, (i[0], i[1]), i[2], green, 1)
                    # iç daire çizimi
                    leftEyeCircleIn = cv2.circle(leftEyeFrame, (i[0], i[1]), 2, red , 1)

                    #göz bebeğinin koordinatını bulmak için iç veya dış dairenin konumunu yazmak yeterlidir

                    leftEyePupilX = (i[0])
                    leftEyePupilY = (i[1])

                    leftEyePupilCoordinate = (leftEyePupilX,leftEyePupilY)

                    leftEyeFrameResize = cv2.resize(leftEyeFrame,None,fx=10,fy=10)

                    cv2.imshow("leftEyePupil",leftEyeFrameResize)

                    leftEyeCoordinate = ("Left Eye Pupil Cor: " + str(leftEyePupilCoordinate))

                #aynı işlemler sağ göz için
                rightEyePupils = cv2.HoughCircles(rightFrameGrayBlur,cv2.HOUGH_GRADIENT,1,999,param1=param_1,param2=param_2,maxRadius=maxradius,minRadius=minradius)

                rightEyePupils = np.uint16(np.around(rightEyePupils))

                for a in rightEyePupils[0, :]:

                    # dış daire çizimi
                    cv2.circle(rightEyeFrame, (a[0], a[1]), a[2], green, 1)
                    # iç daire çizimi
                    cv2.circle(rightEyeFrame, (a[0], a[1]), 2, red, 1)

                    rightEyePupilX = (a[0])
                    rightEyePupilY = (a[1])

                    rightEyePupilCoordinate = (rightEyePupilX,rightEyePupilY)

                    rightEyeFrameResize = cv2.resize(rightEyeFrame,None,fx=10,fy=10)

                    cv2.imshow("rightEyePupil",rightEyeFrameResize)

                    rightEyeCoordinate = ("Right Eye Pupil Cor: " + str(rightEyePupilCoordinate))

        except:
            pass
        # göz bebeği bulmayı göz kırpmanın else ine aldım çünkü göz kapalı iken  göz bebeği bulamazsın
        # bu işlem de gecikmeler olabilir mesela göz kapandığı zaman kapandığını geç algılayabilir bu
        # süre zarfında kapalı gözde göz bebeği bulamayacağı için kod hata verir bunun önüne geçmek için
        # try except içine aldım

    cv2.imshow("frame",frame)

    print(eyeCoordinate + leftEyeCoordinate + rightEyeCoordinate + strBlinkingRatio )

    key = cv2.waitKey(1)
    if key & 0xFF == ord("q") or key & 0xFF ==  ord("Q") : #Q veya q basıldığında kapama
        break

webcam.release()
cv2.destroyAllWindows()

#yeni algoritma için hazırlanmış şuanlık sade :D ortam alıntı kod yok