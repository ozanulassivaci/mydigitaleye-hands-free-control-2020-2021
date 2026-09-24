from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration

red = (0, 0, 255)
green = (0, 255, 0)

class GazeTrackingRight(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame = None
        self.eye_right = None
        self.calibration = Calibration()

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def right_pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def right_analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_right = None

    def right_refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self.right_analyze()


    def right_pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.right_pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)


    def right_annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        if self.right_pupils_located:
            color = (0, 255, 0)
            x_right, y_right = self.right_pupil_right_coords()
            #cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
            #cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)
            cv2.circle(frame,( x_right, y_right),8,green,1)
            cv2.circle(frame,( x_right, y_right),2,red,1)

        return frame
