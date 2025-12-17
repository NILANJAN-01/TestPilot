#!/bin/bash

# TestPilot Linux Dependency & Build Script
# This script prepares a Linux environment for running or building TestPilot.

echo "🚀 Initializing TestPilot Linux Setup..."

# 1. Update & Install System Dependencies
echo "📦 Installing System Dependencies (ADB & scrcpy)..."
sudo apt-get update
sudo apt-get install -y android-tools-adb scrcpy python3-pip python3-venv

# 2. Setup Virtual Environment
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Python Requirements
echo "📂 Installing Python Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller qtawesome PySide6

# 4. Build the Executable
echo "🛠️ Building TestPilot Linux Binary..."
python3 build_executable.py

echo "✅ Linux Build Complete! Binary available at: ./dist/TestPilot"
echo "💡 To run TestPilot now, use: ./dist/TestPilot"
