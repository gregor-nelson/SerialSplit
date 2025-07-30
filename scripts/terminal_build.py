#!/usr/bin/env python3
"""
Simple build script for Serial Terminal application using PyInstaller
"""

import subprocess
import sys
import os

def build_terminal():
    """Build the Serial Terminal executable using PyInstaller"""
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # PyInstaller command with relative paths from project root
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "Serial Terminal",
        "--icon", os.path.join(project_root, "assets", "terminal_icon.ico"),
        os.path.join(project_root, "terminal_main.py")
    ]
    
    print("Building Serial Terminal...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created in: {os.path.join(project_root, 'dist', 'Serial Terminal.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    build_terminal()