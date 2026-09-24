class HoldGesture:
    """Fires once a condition has been seen in `frames` frames within
    `window` seconds.

    Counting frames rather than measuring a continuous hold tolerates the
    occasional frame where the landmark detector misreads a closed eye.
    """

    def __init__(self, frames, window=5):
        self.frames = frames
        self.window = window
        self.count = 0
        self.started = None

    def reset(self):
        self.count = 0
        self.started = None

    def update(self, active, now):
        if not active:
            return False
        if self.started is None:
            self.started = now
        self.count += 1
        elapsed = now - self.started
        if self.count >= self.frames and elapsed <= self.window:
            self.reset()
            return True
        if elapsed > self.window:
            self.reset()
        return False
