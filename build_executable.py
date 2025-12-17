import os
import sys
import subprocess
import shutil

def build():
    print("Starting TestPilot Build Process...")
    
    # 1. Ensure PyInstaller is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "qtawesome", "PySide6"])

    # 2. Define standard args
    # --onefile: single executable
    # --windowed: no console on launch
    # --add-data: include assets/styles
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "TestPilot",
        "--add-data", f"styles{os.pathsep}styles",
        "--add-data", f"core{os.pathsep}core",
        "main.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

    print("\nBuild Completed! Check the 'dist' folder.")

if __name__ == "__main__":
    build()
