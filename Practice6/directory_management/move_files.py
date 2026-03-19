import shutil
import os

os.makedirs("new_folder", exist_ok=True)

if os.path.exists("output.txt"):
    shutil.move("output.txt", "new_folder/output.txt")