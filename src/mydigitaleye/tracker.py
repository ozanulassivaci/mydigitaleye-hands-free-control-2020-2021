"""Turns facial landmarks into cursor movement, clicks and shortcuts.

Two control modes are chosen with a wink after a 10-second countdown:

* Mode 1 (head): the nose tip leaving a "safe area" in the middle of the
  face moves the cursor in that direction. Winks inside the safe area click.
* Mode 2 (eyes): the pupils' offset from the eye centres moves the cursor;
  raising the eyebrows moves it down. Winks click.

Both modes share the hold-to-trigger shortcuts in Tracker._shortcuts.
"""
import math
import os
import shutil
import tempfile
import time
from enum import Enum

import cv2
import dlib

from . import vision
from .gestures import HoldGesture

RED = (0, 0, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)

COUNTDOWN_SECONDS = 10
DEFAULT_SPEEDS = {1: 2, 2: 6}
# Frames a wink must be seen in before it selects a mode.
MODE_SELECT_FRAMES = 2


class Mode(Enum):
    UNDECIDED = 0
    HEAD = 1
    EYES = 2


class PyAutoGuiActions:
    """Sends real mouse and keyboard input."""

    def __init__(self):
        import pyautogui
        # The fail-safe aborts when the cursor reaches a screen corner. The
        # target users cannot move a physical mouse away from the corner, so
        # it would lock them out; the pause gesture and Exit button remain.
        pyautogui.FAILSAFE = False
        self._gui = pyautogui

    def move(self, dx, dy):
        self._gui.moveRel(dx, dy)

    def click(self, button):
        self._gui.click(button=button)

    def hotkey(self, *keys):
        self._gui.hotkey(*keys)


class NoActions:
    """Used with --no-control to watch detection without moving the mouse."""

    def move(self, dx, dy):
        pass

    def click(self, button):
        pass

    def hotkey(self, *keys):
        pass


def _dlib_readable_path(path):
    """dlib opens files through narrow-character APIs on Windows and fails on
    non-ASCII paths, such as a Turkish "Masaüstü" (Desktop) folder. Return a
    path it can open."""
    path = str(path)
    if os.name != "nt" or path.isascii():
        return path
    import ctypes
    buffer = ctypes.create_unicode_buffer(1024)
    if ctypes.windll.kernel32.GetShortPathNameW(path, buffer, len(buffer)) and buffer.value.isascii():
        return buffer.value
    # 8.3 short names can be disabled on a volume; fall back to a copy.
    copy = os.path.join(tempfile.gettempdir(), os.path.basename(path))
    if not os.path.isfile(copy):
        shutil.copyfile(path, copy)
    return copy


class Tracker:
    def __init__(self, model_path, actions, play_sound, speeds=None, clock=time.time):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(_dlib_readable_path(model_path))
        self.actions = actions
        self.play_sound = play_sound
        self.clock = clock

        # Cursor speed multiplier per mode number. The Settings tab edits this
        # dict from the GUI thread while the tracker reads it.
        self.speeds = speeds if speeds is not None else dict(DEFAULT_SPEEDS)

        self.mode = Mode.UNDECIDED
        self.mode_votes = {Mode.HEAD: 0, Mode.EYES: 0}
        self.paused = False
        self.started_at = clock()

        self.pause_gesture = HoldGesture(frames=50)
        self.resume_gesture = HoldGesture(frames=50)
        self.desktop_gesture = HoldGesture(frames=25)
        self.keyboard_gesture = HoldGesture(frames=25)
        self.explorer_gesture = HoldGesture(frames=30)

    def process(self, frame):
        """Analyse one mirrored BGR frame, act on it and draw overlays."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        remaining = COUNTDOWN_SECONDS - (self.clock() - self.started_at)
        if remaining > 0:
            cv2.putText(frame, str(math.ceil(remaining)), (550, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, BLUE)

        if len(faces) > 0:
            # Another person walking behind the user must not take over.
            face = max(faces, key=lambda f: f.area())
            self._process_face(frame, gray, self.predictor(gray, face), remaining <= 0)
        return frame

    def _process_face(self, frame, gray, landmarks, countdown_done):
        left_ratio = vision.blink_ratio(landmarks, vision.LEFT_EYE)
        right_ratio = vision.blink_ratio(landmarks, vision.RIGHT_EYE)
        ratio = round((left_ratio + right_ratio) / 2, 2)

        brow_up, brow_mid, brow_threshold = vision.eyebrow_raised(landmarks)
        cv2.circle(frame, brow_mid, 1, BLUE, 1)
        cv2.circle(frame, brow_threshold, 1, RED, 1)

        left_pupil = vision.find_pupil(gray, landmarks, vision.LEFT_EYE)
        right_pupil = vision.find_pupil(gray, landmarks, vision.RIGHT_EYE)
        for pupil in (left_pupil, right_pupil):
            if pupil is not None:
                x, y, r = pupil
                cv2.circle(frame, (x, y), r, GREEN, 1)
                cv2.circle(frame, (x, y), 2, RED, 1)

        # A wink needs both the landmark ratio and the missing pupil to agree;
        # either signal alone gives false positives when looking down.
        left_wink = (left_ratio > ratio and left_ratio > vision.CLOSED_EYE_RATIO
                     and left_pupil is None and right_pupil is not None)
        right_wink = (right_ratio > ratio and right_ratio > vision.CLOSED_EYE_RATIO
                      and right_pupil is None and left_pupil is not None)
        both_closed = (left_pupil is None and right_pupil is None
                       and ratio > vision.CLOSED_EYE_RATIO)

        if self.mode is Mode.UNDECIDED:
            if countdown_done:
                self._vote_for_mode(left_wink, right_wink)
            return

        nose, safe_start, safe_end = self._draw_face_area(frame, landmarks)
        self._shortcuts(left_wink, right_wink, both_closed, brow_up)
        if self.paused:
            return

        if self.mode is Mode.HEAD:
            self._head_control(nose, safe_start, safe_end, left_wink, right_wink)
        else:
            self._eye_control(landmarks, left_pupil, right_pupil,
                              left_wink, right_wink, brow_up)

    def _vote_for_mode(self, left_wink, right_wink):
        if left_wink:
            self.mode_votes[Mode.HEAD] += 1
        elif right_wink:
            self.mode_votes[Mode.EYES] += 1
        for mode, votes in self.mode_votes.items():
            if votes >= MODE_SELECT_FRAMES:
                self.mode = mode
                # Eye mode was tuned with a longer hold for this shortcut.
                if mode is Mode.EYES:
                    self.desktop_gesture.frames = 50
                return

    def _draw_face_area(self, frame, landmarks):
        """Draw the face box, its centre and (in head mode) the safe area.

        Returns the nose tip and the safe area corners.
        """
        jaw_left = vision.point(landmarks, 0)
        jaw_right = vision.point(landmarks, 16)
        chin_side = vision.point(landmarks, 12)
        pad_x = (jaw_right[0] - jaw_left[0]) // 10
        pad_y = (chin_side[1] - jaw_left[1]) // 2
        box_start = (jaw_left[0] - pad_x, jaw_left[1] - pad_y)
        box_end = (jaw_right[0] + pad_x, chin_side[1] + pad_y)
        center = ((box_start[0] + box_end[0]) // 2, (box_start[1] + box_end[1]) // 2)
        nose = vision.point(landmarks, vision.NOSE_TIP)

        cv2.rectangle(frame, box_start, box_end, RED, 2)
        cv2.circle(frame, nose, 2, BLUE, -1)
        cv2.circle(frame, center, 2, RED, -1)

        half = (box_end[0] - box_start[0]) // 8
        safe_start = (center[0] - half, center[1] - half)
        safe_end = (center[0] + half, center[1] + half)
        if self.mode is Mode.HEAD:
            cv2.rectangle(frame, safe_start, safe_end, BLUE, 2)
        return nose, safe_start, safe_end

    def _shortcuts(self, left_wink, right_wink, both_closed, brow_up):
        now = int(self.clock())
        if not self.paused:
            if self.pause_gesture.update(both_closed and not brow_up, now):
                self.paused = True
                self.play_sound("stop")
                return
            if self.desktop_gesture.update(left_wink and not brow_up, now):
                self.actions.hotkey("win", "d")
                self.play_sound("desktop")
            if self.keyboard_gesture.update(right_wink and not brow_up, now):
                self.actions.hotkey("win", "ctrl", "o")
                self.play_sound("keyboard")
            if self.explorer_gesture.update(both_closed and brow_up, now):
                self.actions.hotkey("win", "e")
                self.play_sound("file")
        elif self.resume_gesture.update(both_closed and not brow_up, now):
            self.paused = False
            self.play_sound("start")

    def _head_control(self, nose, safe_start, safe_end, left_wink, right_wink):
        (x, y), speed = nose, self.speeds[1]
        # The cursor speed grows with how far the nose is outside the area.
        if y < safe_start[1]:
            self.actions.move(0, speed * (y - safe_start[1]))
        elif y > safe_end[1]:
            self.actions.move(0, speed * (y - safe_end[1]))
        elif x > safe_end[0]:
            self.actions.move(speed * (x - safe_end[0]), 0)
        elif x < safe_start[0]:
            self.actions.move(speed * (x - safe_start[0]), 0)

        # Clicking only inside the safe area keeps the cursor still while
        # the wink is registered.
        inside = safe_start[0] < x < safe_end[0] and safe_start[1] < y < safe_end[1]
        if inside and left_wink:
            self.actions.click("left")
        if inside and right_wink:
            self.actions.click("right")

    def _eye_control(self, landmarks, left_pupil, right_pupil,
                     left_wink, right_wink, brow_up):
        if left_pupil is not None and right_pupil is not None:
            left_center = vision.eye_center(landmarks, vision.LEFT_EYE)
            right_center = vision.eye_center(landmarks, vision.RIGHT_EYE)
            # Average offset of both pupils from their eye centres.
            dx = ((left_pupil[0] - left_center[0]) + (right_pupil[0] - right_center[0])) // 2
            dy = ((left_pupil[1] - left_center[1]) + (right_pupil[1] - right_center[1])) // 2
            dead_zone = int(vision.eye_width(landmarks) // 8)
            speed = self.speeds[2]

            # Looking down is barely visible in a webcam image because the
            # eyelid follows the pupil, so raised eyebrows stand in for it.
            if dy < -dead_zone:
                self.actions.move(0, speed * dy)
            elif brow_up:
                self.actions.move(0, 2 * speed)
            elif dx < -dead_zone:
                self.actions.move(speed * dx, 0)
            elif dx > dead_zone:
                self.actions.move(speed * dx, 0)
        elif left_wink:
            self.actions.click("left")
        elif right_wink:
            self.actions.click("right")
