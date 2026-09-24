import unittest

from mydigitaleye.gestures import HoldGesture


class HoldGestureTest(unittest.TestCase):
    def test_fires_after_enough_frames_within_window(self):
        gesture = HoldGesture(frames=3, window=5)
        self.assertFalse(gesture.update(True, now=0))
        self.assertFalse(gesture.update(True, now=1))
        self.assertTrue(gesture.update(True, now=2))

    def test_inactive_frames_are_ignored(self):
        gesture = HoldGesture(frames=2, window=5)
        gesture.update(True, now=0)
        self.assertFalse(gesture.update(False, now=1))
        self.assertTrue(gesture.update(True, now=2))

    def test_resets_after_firing(self):
        gesture = HoldGesture(frames=2, window=5)
        gesture.update(True, now=0)
        gesture.update(True, now=0)
        self.assertFalse(gesture.update(True, now=1))

    def test_window_expiry_restarts_counting(self):
        gesture = HoldGesture(frames=3, window=5)
        gesture.update(True, now=0)
        gesture.update(True, now=1)
        self.assertFalse(gesture.update(True, now=7))
        self.assertEqual(gesture.count, 0)
        gesture.update(True, now=8)
        gesture.update(True, now=8)
        self.assertTrue(gesture.update(True, now=9))

    def test_count_reached_after_window_does_not_lock_up(self):
        # Regression: the 2021 code stopped resetting once the frame count
        # was reached outside the window, so the shortcut never fired again.
        gesture = HoldGesture(frames=2, window=5)
        gesture.update(True, now=0)
        self.assertFalse(gesture.update(True, now=6))
        gesture.update(True, now=7)
        self.assertTrue(gesture.update(True, now=7))


if __name__ == "__main__":
    unittest.main()
