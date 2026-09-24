from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration

red = (0, 0, 255)
green = (0, 255, 0)


class GazeTrackingLeft(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.calibration = Calibration()

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def left_pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            return True
        except Exception:
            return False


    def left_analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)

        except IndexError:
            self.eye_left = None

    def left_refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self.left_analyze()

    def left_pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.left_pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)


    def left_annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        if self.left_pupils_located:
            color = (0, 255, 0)
            x_left, y_left = self.left_pupil_left_coords()
            #cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            #cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
            cv2.circle(frame,( x_left, y_left),8,green,1)
            cv2.circle(frame,( x_left, y_left),2,red,1)

        return frame
