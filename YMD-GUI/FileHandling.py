import os
import re
import shutil

def clean_windows_file_name(file_name):
    return re.sub(r'[\\/:"*?<>|]', '', file_name).strip()

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")

def move_file(src, dest):
    try:
        shutil.move(src, dest)
        print(f"File moved to {dest}")
    except Exception as e:
        print(f"Failed to move file: {e}")
