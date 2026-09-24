"""Download dlib's 68-point facial landmark model into models/."""
import bz2
import shutil
import sys
import urllib.request
from pathlib import Path

URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
TARGET = Path(__file__).resolve().parent.parent / "models" / "shape_predictor_68_face_landmarks.dat"


def main():
    if TARGET.is_file():
        print(f"Already present: {TARGET}")
        return
    TARGET.parent.mkdir(exist_ok=True)
    print(f"Downloading {URL} (about 64 MB) ...")
    partial = TARGET.with_suffix(".part")
    with urllib.request.urlopen(URL) as response, bz2.open(response) as source, \
            open(partial, "wb") as target:
        shutil.copyfileobj(source, target)
    partial.replace(TARGET)
    print(f"Saved to {TARGET}")


if __name__ == "__main__":
    sys.exit(main())
