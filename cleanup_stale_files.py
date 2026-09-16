"""
clears out the leftover empty dashboard/ folder (real dashboard is app.py + pages/)
and the old duplicate "border optics maps.pdf".
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
        print(f"skip (not found): {path}")
        continue
    if os.path.isdir(path):
        shutil.rmtree(path)
        print(f"removed folder: {path}")
    else:
        os.remove(path)
        print(f"removed file: {path}")

print("done.")
