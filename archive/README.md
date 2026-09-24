# Development history

The original code from September 2020 to March 2021, in chronological order.
The files are kept as they were written, including their Turkish comments and
hard-coded paths, so they show how the project evolved. Only the file names
were translated. They are not maintained and several need files that are not
in this repository (for example, the dlib model next to the script).

The maintained version is in [`src/`](../src). It is based on stage 06.

| Stage | Date | What changed |
| --- | --- | --- |
| [01-2020-09-first-prototype](01-2020-09-first-prototype) | Sep–Oct 2020 | First experiments: blink detection from the eye aspect ratio, pupil detection with a Hough circle transform, and cursor movement driven by the open-source [GazeTracking](https://github.com/antoinelame/GazeTracking) library. Release note from that time: "The idea works and is proven feasible; cursor movement from gaze tracking works but is unreliable with the left eye." |
| [02-2020-11-eye-analysis](02-2020-11-eye-analysis) | Nov 2020 | Own landmark code replaces the library: blink ratio, eye centre, and separate left and right pupil detection with tuned Hough parameters. The comments list the lighting and distance conditions it needs. |
| [03-2020-12-pyqt-interface-experiment](03-2020-12-pyqt-interface-experiment) | Dec 2020 | First PyQt5 window, designed in Qt Designer. |
| [04-2021-01-face-cursor](04-2021-01-face-cursor) | Jan 2021 | "Face Cursor": head control through a face box from the jaw landmarks, a safe area in its centre and nose-tip tracking (later Mode 1); camera processing in a QThread inside a PyQt5 window; blink-triggered shortcuts (pause, resume, desktop, on-screen keyboard, file explorer) with audio prompts. v1.1 to v1.3 retune the detection thresholds and asset paths. |
| [05-2021-02-dijital-gozum](05-2021-02-dijital-gozum) | Feb 2021 | Renamed to Dijital Gözüm. Tabbed interface (Camera, Settings, Shortcuts, How to Use), two control modes chosen by a wink after a 10-second countdown, eye-controlled Mode 2 and adjustable cursor speed. |
| [06-2021-03-final-snapshot](06-2021-03-final-snapshot) | Mar 2021 | Last source snapshot before the regional round. Differs from stage 05 by one crop margin. |
| [07-2021-03-pupil-tracking-experiment](07-2021-03-pupil-tracking-experiment) | Mar 2021 | Separate left and right pupil trackers adapted from GazeTracking (MIT licence, see `LICENSE-GazeTracking`), with a demo script. The build that combined them with stage 06 was only kept as an executable, so its source is not available. |
