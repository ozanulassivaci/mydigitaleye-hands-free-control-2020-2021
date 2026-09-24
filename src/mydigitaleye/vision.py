"""Measurements on dlib's 68-point facial landmarks.

Index layout (iBUG 300-W): 0-16 jaw line, 17-26 eyebrows, 27-35 nose,
36-41 left eye, 42-47 right eye, 48-67 mouth. "Left" and "right" refer to
the mirrored webcam image, which matches the user's own left and right.
"""
import math

import cv2
import numpy as np

LEFT_EYE = (36, 37, 38, 39, 40, 41)
RIGHT_EYE = (42, 43, 44, 45, 46, 47)
NOSE_TIP = 30

# An eye counts as closed when its width/height ratio exceeds this value.
CLOSED_EYE_RATIO = 5.7

# Hough transform settings for finding the pupil in a blurred eye crop.
# They assume the face is lit from the front; a strong light behind the
# user washes out the dark pupil.
PUPIL_HOUGH_PARAM1 = 200
PUPIL_HOUGH_PARAM2 = 5
PUPIL_MIN_RADIUS = 1
PUPIL_MAX_RADIUS = 8
EYE_CROP_MARGIN = 5


def point(landmarks, index):
    part = landmarks.part(index)
    return part.x, part.y


def mid_point(landmarks, a, b):
    (ax, ay), (bx, by) = point(landmarks, a), point(landmarks, b)
    return int((ax + bx) / 2), int((ay + by) / 2)


def distance(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def eye_width(landmarks):
    """Average corner-to-corner width of both eyes.

    Both eye ratios share this width so that head rotation, which narrows
    one eye and widens the other, does not skew the comparison.
    """
    left = distance(point(landmarks, 36), point(landmarks, 39))
    right = distance(point(landmarks, 42), point(landmarks, 45))
    return (left + right) / 2


def blink_ratio(landmarks, eye):
    """Eye width divided by eyelid opening; grows as the eye closes."""
    top = mid_point(landmarks, eye[1], eye[2])
    bottom = mid_point(landmarks, eye[5], eye[4])
    height = distance(top, bottom)
    if height == 0:
        return math.inf
    return round(eye_width(landmarks) / height, 1)


def eye_center(landmarks, eye):
    """Centre of the square formed by the four inner eyelid points."""
    top_x = mid_point(landmarks, eye[1], eye[2])[0]
    bottom_x = mid_point(landmarks, eye[5], eye[4])[0]
    left_y = mid_point(landmarks, eye[1], eye[5])[1]
    right_y = mid_point(landmarks, eye[2], eye[4])[1]
    return int((top_x + bottom_x) / 2), int((left_y + right_y) / 2)


def eyebrow_raised(landmarks):
    """Return (raised, brow_mid, threshold_point).

    The threshold sits above the top of the nose bridge (27) by 90% of the
    average height of the upper jaw segments (0-1 and 16-15). Scaling by a
    face measurement keeps the test independent of distance to the camera.
    """
    brow_mid = mid_point(landmarks, 21, 22)
    jaw_step = ((point(landmarks, 0)[1] - point(landmarks, 1)[1])
                + (point(landmarks, 16)[1] - point(landmarks, 15)[1])) // 2
    margin = int(0.9 * jaw_step)
    threshold = (brow_mid[0], point(landmarks, 27)[1] + margin)
    return threshold[1] > brow_mid[1], brow_mid, threshold


def eye_crop(gray, landmarks, eye):
    """Crop the eye's bounding box plus a small margin; return (crop, origin)."""
    region = np.array([point(landmarks, i) for i in eye], dtype=np.int32)
    min_x = max(int(region[:, 0].min()) - EYE_CROP_MARGIN, 0)
    min_y = max(int(region[:, 1].min()) - EYE_CROP_MARGIN, 0)
    max_x = int(region[:, 0].max()) + EYE_CROP_MARGIN
    max_y = int(region[:, 1].max()) + EYE_CROP_MARGIN
    return gray[min_y:max_y, min_x:max_x], (min_x, min_y)


def find_pupil(gray, landmarks, eye):
    """Locate the pupil as a small dark circle; return (x, y, r) in frame
    coordinates, or None when no pupil is visible (the eye is closed)."""
    crop, (ox, oy) = eye_crop(gray, landmarks, eye)
    if crop.size == 0:
        return None
    blurred = cv2.medianBlur(crop, 5)
    # minDist is larger than any eye crop, so at most one circle is returned.
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 999,
                               param1=PUPIL_HOUGH_PARAM1, param2=PUPIL_HOUGH_PARAM2,
                               minRadius=PUPIL_MIN_RADIUS, maxRadius=PUPIL_MAX_RADIUS)
    if circles is None:
        return None
    x, y, r = np.around(circles[0, -1]).astype(int)
    return ox + x, oy + y, r
