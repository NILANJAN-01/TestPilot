# TestAssistMAX v1.0.0

A professional-grade desktop tool for **Android Automotive OS (AAOS)** and standard Android device testing, monitoring, and automation.

## 🚀 Key Features

### 1. Device Monitoring & Management
- **Real-time Performance**: Track CPU (summary & per-process), Memory, and Thermal status.
- **Android Services Monitor**: Live view of all running system services.
- **Auto-Capture**: Intelligent monitoring for **Crashes (FATAL)** and **ANRs**. Automatic screenshot and log dump on failure detections.
- **Remote Control**: High-performance mirroring and control via integrated **scrcpy**.
- **ADB Root Toggle**: One-click root access for system-level debugging.

### 2. Test Automation (TMX Engine)
- **Robot Framework Integration**: Run TMX-standard suites directly from the UI.
- **System Health Checks**: 15+ automated checks for AAOS vitals (Vehicle HAL, Screen, Network, Vitals).
- **UI Automation**: Deep UI verification using custom **UIAutomator** logic.
- **Embedded Reports**: Automated capture of failure screenshots and log snapshots, embedded into professional HTML reports.
- **Report Archival**: One-click download of full execution reports as ZIP.

### 3. Capture & Control
- **Screenshot Tools**: Manual and burst mode (5x) captures.
- **Screen Recording**: Customizable bitrate and time-limits for video evidence.
- **Unified Controls**: Media, Connectivity (Wi-Fi/BT), Power, and App lifecycle management.

## 📁 Project Structure

- `automation/`: Contains Robot Framework tests and custom libraries (`AaosLibrary`).
- `components/`: Modular UI widgets (Sidebar, TitleBar, Toast).
- `core/`: Application backbone including `context` for service discovery and `config` for versioning.
- `services/`: Backend logic handling ADB interactions, monitoring threads, and automation workers.
- `styles/`: Custom QSS for a futuristic, high-contrast dark theme.
- `views/`: The main pages of the application (Monitoring, Controls, Automation).

## 🛠️ Requirements & Installation
- Python 3.8+
- PySide6
- Robot Framework
- [scrcpy](https://github.com/Genymobile/scrcpy) (Required for Remote Control)
- ADB (Android Debug Bridge)

## 💻 Cross-Platform Support
TestAssistMAX is designed to run seamlessly on:
- **Windows**
- **MacOS** (Requires `brew install scrcpy`)
- **Linux** (Requires `sudo apt install scrcpy`)

---
© 2025 Antigravity Engineering - Advanced Agentic Coding
