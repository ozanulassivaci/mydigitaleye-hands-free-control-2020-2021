import argparse
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from mydigitaleye.app import MainWindow
from mydigitaleye.tracker import NoActions, PyAutoGuiActions

DEFAULT_MODEL = Path(__file__).resolve().parent.parent / "models" / "shape_predictor_68_face_landmarks.dat"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Control the mouse with eye and head movements through a webcam.")
    parser.add_argument("--lang", choices=("en", "tr"), default="en",
                        help="interface language (default: en)")
    parser.add_argument("--camera", type=int, default=0,
                        help="webcam index (default: 0)")
    parser.add_argument("--video", type=Path,
                        help="read frames from a video file instead of the webcam")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL,
                        help="path to dlib's shape_predictor_68_face_landmarks.dat")
    parser.add_argument("--no-control", action="store_true",
                        help="show detection only; do not move the mouse or press keys")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.model.is_file():
        sys.exit(f"Landmark model not found: {args.model}\n"
                 "Download it with: python scripts/download_model.py")
    if args.video is not None and not args.video.is_file():
        sys.exit(f"Video file not found: {args.video}")

    source = str(args.video) if args.video else args.camera
    actions = NoActions() if args.no_control else PyAutoGuiActions()

    app = QApplication(sys.argv)
    window = MainWindow(args.lang, source, args.model, actions)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
