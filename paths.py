# paths.py
# Path handling that works both when running "python main.py" normally AND
# when packaged into a PyInstaller .exe. Without this, a packaged exe would
# fail to find its images/sounds, or worse, reset the database every launch.

import sys
import os


def resource_path(relative_path):
    """For READ-ONLY bundled files: images, sounds, fonts.
    In a PyInstaller --onefile exe, these are extracted to a temp folder
    (sys._MEIPASS) at startup. When just running the .py files normally,
    sys._MEIPASS doesn't exist, so we just use the relative path as-is."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path


def writable_path(relative_path):
    """For files that must PERSIST across runs: the SQLite database.
    Must live next to the actual .exe file (not the temp extraction folder,
    which gets deleted when the program closes)."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)
