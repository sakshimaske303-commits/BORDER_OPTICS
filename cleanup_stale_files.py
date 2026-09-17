"""
Historical cleanup script. Its original two targets (an empty leftover
"dashboard/" folder and the duplicate "border optics maps.pdf" at repo root)
were resolved on 2026-09-17: "dashboard/" no longer exists, and
"border optics maps.pdf" was moved (not deleted) into archive/root/, along
with several other unreferenced/superseded files -- see archive/README.md
for the full list and the reasoning for each.

This script is kept for its history, but running it now is a no-op, since
neither original target exists at these paths any more.

run: python cleanup_stale_files.py
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
        print(f"skip (not found -- already resolved, see archive/README.md): {path}")
        continue
    if os.path.isdir(path):
        shutil.rmtree(path)
        print(f"removed folder: {path}")
    else:
        os.remove(path)
        print(f"removed file: {path}")

print("done.")
