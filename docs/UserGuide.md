# TestPilot User Guide

## Getting Started
1. **Enable ADB**: Ensure "Developer Options" and "USB Debugging" are enabled on your Android/AAOS device.
2. **Connect**: Plug in the device via USB or connect via `adb connect <ip>`.
3. **Launch**: Open TestPilot.

## Features

### 1. Device Info
Displays deep metadata about your device, including ABI, Kernel version, and Automotive-specific characteristics (VHAL state).

### 2. Device Controls
- **Media**: Control music playback and volume.
- **Connectivity**: Toggle WiFi and Bluetooth.
- **Power**: Simulation of hardware buttons and system reboots.

### 3. Remote Control
- Click "Launch Remote Session" to mirror your device screen.
- **Auto-Installation**: If `scrcpy` is missing, TestPilot will attempt to install it for you (using Winget on Windows or Brew on Mac).
- Use your mouse/keyboard to interact with the device.

### 4. System Stability Check
- **App Stress**: Select multiple apps and run them in a loop.
- **Crash Detection**: The tool automatically monitors logs for ANRs and Fatal Crashes during the run.
- **Verification**: Verifies if the app actually reached the foreground after launch.

### 5. Test Automation Hub
- Execute pre-defined TMX suites (Health Checks, Media, Connectivity).
- Generate HTML reports and download them as ZIP archives.

## Future Roadmap
- **Logcat Explorer**: Advanced live log filtering and export.
- **App Manager**: Drag-and-drop APK installation.
- **Macro Recorder**: Record and playback touch sequences.
- **Cloud Testing**: Integration with remote device farms.
