import cv2
import dlib
import numpy as np
from math import hypot

webcam = cv2.VideoCapture(0)


detector = dlib.get_frontal_face_detector() #dlib ön yüz bulma
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat") #dlib yüzdeki noktaları (0-67) birleştirmek için

red = 	(0,0,255)
blue = (255,0,0)  # renk kodları ve font
green = (0,255,0)
font = cv2.FONT_HERSHEY_DUPLEX

def midPoint(p1,p2):
    return int((p1.x + p2.x)/2),int((p1.y + p2.y)/2)
    #girilen iki noktanın ortasını bulma

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midPoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midPoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))
    #göz noktaları sırası ile girildiği zaman [36, 37, 38, 39, 40, 41] gibi sol sağ üst ve alt noktalarını bulma

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    #bir gözümüzün solundan mesela sol gözün solundan (36) noktası sağıyla (39) noktası tamamen paralel konumda olmayabilir
    #birisinin y sinin farlı olduğu durumda soldan sağa uzunluğu ölçmek için pisagor bağıntısı gerekir
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    #burdada aynı durumun gözün üstünden altına olan uzaklıktada geçerli olacaktır

    ratio = hor_line_lenght / ver_line_lenght
    #bunları oranlıyoruz ki çıkan değerleri test ederek hangi durumda göz kırpılmış anlayabilelim
    return ratio


while True:
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #yükü azaltmak içi siyah beyaza çevirdik
    faces = detector(gray)

    for face in faces:
        #göz alanı bulma göz bebeği bulma vs gibi yüz içindeki şeyleri yüz dışında aramaya gerek yok

        landmarks = predictor(gray, face) #artık yüzdeki noktalar ile işlem yapabileceğiz

        startPoint = (landmarks.part(18).x,landmarks.part(17).y)
        endPoint = (landmarks.part(25).x,landmarks.part(28).y)
        #göz bebeğini bulmayı kolaylaştırmak için iki gözü sığdırabileceğimiz en küçük alanı buluyoruz

        eyes = cv2.rectangle(frame,startPoint,endPoint,blue,2)
        #bulduk ve alanı çerçeveledik

        eyesFrame = frame[landmarks.part(17).y:landmarks.part(28).y,landmarks.part(18).x:landmarks.part(25).x]
        #bulduğumuz alanı yeni bir pencereye taşıyoruz

        eyesFrameGray = cv2.cvtColor(eyesFrame,cv2.COLOR_BGR2GRAY) # işlem kolaylığı için siyah beyaza çevirdik
        eyesFrameGrayBlur = cv2.medianBlur(eyesFrameGray,5) # resmi yumşattık

        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
        # sol ve sağ gözün kırpma oranını bulup toplayıp ikiye böldük yüksek doğruluk için


        try:

            pupilsMinFar = (landmarks.part(42).x - landmarks.part(39).x) / 2
            #çizilecek dairelerin arasındaki minumum uzaklık sol gözün sağ noktası (39) sağ gözün sol noktası (42) olacaktır

            if blinking_ratio > 5.5:
                cv2.putText(frame, "BLINKING", (10,50), font , 2, green)
                #göz kırpma tespiti

            else:

                pupils = cv2.HoughCircles(eyesFrameGrayBlur,cv2.HOUGH_GRADIENT,1,pupilsMinFar,param1=100,param2=10,maxRadius=7,minRadius=4)
                #iki gözü sığdırabileceğimiz en küçük alanda göz bebeği bulup daire içine alıyoruz
                #param 1 değeri ne kadar azalırsa o kadar çok daire bulur
                #param 2 değeri ne kadar artarsa o kadar az daire bulur
                #maxRadius en fazla çap minRadius en az çap
                #bu değerlerle oynayıp doğruluk oranı değiştirilebilir


                pupils = np.uint16(np.around(pupils))

                for i in pupils[0, :]:
                    # dış daire çizimi
                    cv2.circle(eyesFrame, (i[0], i[1]), i[2], (0, 255, 0), 1)
                    # iç daire çizimi
                    cv2.circle(eyesFrame, (i[0], i[1]), 2, (0, 0, 255), 1)

                    eyesFrameResize = cv2.resize(eyesFrame,None,fx=10,fy=10)

                    cv2.imshow("eyesFrame",eyesFrameResize)
                #göz bebeği bulmayı göz kırpmanın else ine aldım çünkü göz kapalı iken  göz bebeği bulamazsın
                #bu işlem de gecikmeler olabilir mesela göz kapandığı zaman kapandığını geç algılayabilir bu
                #süre zarfında kapalı gözde göz bebeği bulamayacağı için kod hata verir bunun önüne geçmek için
                #try except içine aldım

        except:
            pass

    cv2.imshow("frame",frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord("q") or key & 0xFF ==  ord("Q") : #Q veya q basıldığında kapama
        break

webcam.release()
cv2.destroyAllWindows()

#yeni algoritma için hazırlanmış şuanlık sade :D ortam