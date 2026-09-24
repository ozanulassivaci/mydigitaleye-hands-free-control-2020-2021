import cv2
from gaze_tracking_right import GazeTrackingRight
from gaze_tracking_left import GazeTrackingLeft

gaze_right = GazeTrackingRight()
gaze_left = GazeTrackingLeft()
webcam = cv2.VideoCapture(0)

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)
    # We send this frame to GazeTracking to analyze it
    gaze_right.right_refresh(frame)

    frame = gaze_right.right_annotated_frame()
    text = ""

    gaze_left.left_refresh(frame)

    frame = gaze_left.left_annotated_frame()


    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze_left.left_pupil_left_coords()

    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)


    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    right_pupil = gaze_right.right_pupil_right_coords()
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break
