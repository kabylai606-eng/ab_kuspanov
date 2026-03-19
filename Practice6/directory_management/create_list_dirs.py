import os

# Create folder
os.makedirs("my_folder", exist_ok=True)

# List directory contents
for item in os.listdir("."):
    print(item)