# TestPilot v1.0.0

A professional-grade desktop tool for **Android Automotive OS (AAOS)** and standard Android device testing, monitoring, and automation.

## 🚀 Key Features

### 1. System Stability Check (New)
- **App Stress Loop**: Multi-select apps and run them in high-frequency launch loops.
- **Fail Detection**: Auto-monitors for **Crashes (FATAL)** and **ANRs**. 
- **Focus Verification**: Ensures apps reach the foreground successfully.

### 2. Remote Control
- **High-Performance Mirroring**: Integrated **scrcpy** support with 4M bitrate optimization.
- **Zero-Config Installation**: Automatic cross-platform installation of scrcpy dependencies.
- **Mouse & Keyboard Injection**: Direct interaction with the device UI.

### 3. Test Automation (TMX Engine)
- **Robot Framework Integration**: Run TMX-standard suites directly from the UI.
- **System Health Checks**: 15+ automated checks for AAOS vitals.
- **Embedded Reports**: Automated capture of failure screenshots and logs.

### 4. Device Monitoring & Management
- **Deep Info Discovery**: Extract build props, manufacturer data, and VHAL states.
- **Unified Controls**: Media, Connectivity (Wi-Fi/BT), Power, and App lifecycle management.
- **ADB Root Toggle**: One-click root access for system-level debugging.

## 📁 Project Structure
- `services/`: Robust backend handling ADB, Mirroring, and Stability Loops.
- `views/`: Premium UI pages (Info, Controls, Remote, Stability, Automation).
- `docs/`: Comprehensive **HLD** and **User Guide**.

## 🛠️ Build & Installation
- **Windows**: Use `python build_executable.py` to generate a portable EXE.
- **Linux**: Distributed as a binary (requires `android-tools`).

---
Developed by NILANJAN-01
