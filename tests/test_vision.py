import math
import unittest
from collections import namedtuple

import cv2
import numpy as np

from mydigitaleye import vision

Part = namedtuple("Part", "x y")


class FakeLandmarks:
    def __init__(self, points):
        self.points = points

    def part(self, index):
        return Part(*self.points[index])


def face(left_eye_open=True, right_eye_open=True, brow_y=40):
    """A symmetric synthetic face; eyelid gap is 10 px open, 1 px closed."""
    points = {i: (0, 0) for i in range(68)}
    points.update({0: (20, 60), 1: (22, 80), 15: (178, 80), 16: (180, 60), 27: (100, 55)})
    points.update({21: (90, brow_y), 22: (110, brow_y)})
    for eye, x0, is_open in ((vision.LEFT_EYE, 50, left_eye_open), (vision.RIGHT_EYE, 120, right_eye_open)):
        gap = 5 if is_open else 0.5
        top, bottom = 65 - gap, 65 + gap
        corners = [(x0, 65), (x0 + 10, top), (x0 + 20, top),
                   (x0 + 30, 65), (x0 + 20, bottom), (x0 + 10, bottom)]
        points.update(dict(zip(eye, corners)))
    return FakeLandmarks(points)


class VisionTest(unittest.TestCase):
    def test_blink_ratio_rises_when_eye_closes(self):
        open_ratio = vision.blink_ratio(face(), vision.LEFT_EYE)
        closed_ratio = vision.blink_ratio(face(left_eye_open=False), vision.LEFT_EYE)
        self.assertLess(open_ratio, vision.CLOSED_EYE_RATIO)
        self.assertGreater(closed_ratio, vision.CLOSED_EYE_RATIO)

    def test_blink_ratio_of_fully_shut_eye_is_infinite(self):
        landmarks = face()
        for i in vision.LEFT_EYE:
            x, _ = landmarks.points[i]
            landmarks.points[i] = (x, 65)
        self.assertEqual(vision.blink_ratio(landmarks, vision.LEFT_EYE), math.inf)

    def test_eye_center(self):
        self.assertEqual(vision.eye_center(face(), vision.LEFT_EYE), (65, 65))

    def test_eyebrow_raised(self):
        self.assertFalse(vision.eyebrow_raised(face(brow_y=40))[0])
        self.assertTrue(vision.eyebrow_raised(face(brow_y=30))[0])

    def test_find_pupil_detects_dark_disc(self):
        gray = np.full((120, 200), 200, np.uint8)
        cv2.circle(gray, (65, 65), 4, 20, -1)
        pupil = vision.find_pupil(gray, face(), vision.LEFT_EYE)
        self.assertIsNotNone(pupil)
        self.assertLessEqual(abs(pupil[0] - 65), 2)
        self.assertLessEqual(abs(pupil[1] - 65), 2)

    def test_find_pupil_returns_none_on_blank_eye(self):
        gray = np.full((120, 200), 200, np.uint8)
        self.assertIsNone(vision.find_pupil(gray, face(), vision.LEFT_EYE))


if __name__ == "__main__":
    unittest.main()
