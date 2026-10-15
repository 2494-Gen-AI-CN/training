"""Standard exercise conftest. Puts the module under test first on sys.path.

Trainees run `python -m pytest -q` from the exercise dir: tests import from ./starter.
The trainer (and the harness critic) runs with EXERCISE_SRC pointing at the private
solutions folder, so the same tests prove the reference solution passes.
"""
import os
import pathlib
import sys

_SRC = os.environ.get("EXERCISE_SRC") or str(pathlib.Path(__file__).resolve().parents[1] / "starter")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
