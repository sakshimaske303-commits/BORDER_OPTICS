"""
BORDER_OPTICS — cleanup script for two stale/duplicate artifacts found during
the documentation audit. Run this yourself from inside the BORDER_OPTICS folder:

    python cleanup_stale_files.py

What it removes:
  1. dashboard/  — an empty legacy folder (only contains an empty "pages"
     subfolder, no files). The real dashboard lives at the project root
     (app.py + pages/), so this leftover folder does nothing.
  2. "border optics maps.pdf" — an older, stray duplicate of
     BORDER_OPTICS_Maps_and_Plots.pdf, which is the file actually in use.

The script only touches these two specific paths and prints what it did.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

targets = [
    os.path.join(HERE, "dashboard"),
    os.path.join(HERE, "border optics maps.pdf"),
]

for path in targets:
    if not os.path.exists(path):
        print(f"skip (not found): {path}")
        continue
    if os.path.isdir(path):
        shutil.rmtree(path)
        print(f"removed folder: {path}")
    else:
        os.remove(path)
        print(f"removed file: {path}")

print("done.")
