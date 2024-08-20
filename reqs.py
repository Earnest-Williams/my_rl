import os
import chardet
import subprocess
import sys

def check_and_convert_encoding(file_path, target_encoding='utf-8'):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        current_encoding = result['encoding']

    if current_encoding != target_encoding:
        print(f"Converting {file_path} from {current_encoding} to {target_encoding}")
        try:
            with open(file_path, 'r', encoding=current_encoding) as f:
                content = f.read()
            with open(file_path, 'w', encoding=target_encoding) as f:
                f.write(content)
            print(f"Converted {file_path} to {target_encoding}")
        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")

def scan_and_convert_files(root_folder, exclude_folder):
    for root, dirs, files in os.walk(root_folder):
        if exclude_folder in root:
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                check_and_convert_encoding(file_path)

def create_requirements_txt(root_folder, exclude_folder):
    try:
        subprocess.run(['pipreqs', root_folder, '--force', '--ignore', exclude_folder], check=True)
        print(f"'requirements.txt' has been successfully created in {root_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create 'requirements.txt': {e}")

if __name__ == "__main__":
    project_folder = './'  # Adjust this path if your project folder is different
    venv_folder = '.direnv'  # Name of the virtual environment folder to ignore
    scan_and_convert_files(project_folder, venv_folder)
    create_requirements_txt(project_folder, venv_folder)
