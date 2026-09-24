import sys
from pathlib import Path

# The application runs as `python src/main.py`, so src/ is not installed as a
# package; make it importable for `python -m unittest` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
