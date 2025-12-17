# TestPilot High-Level Design (HLD)

## 1. Introduction
TestPilot is a futuristic, cross-platform desktop application designed for testing and controlling Android Automotive OS (AAOS) and standard Android devices. It provides a premium UI experience and robust automation features.

## 2. Architecture Overview
The application follows a **Service-Oriented-UI (SOUI)** pattern, ensuring strict separation between logic and presentation.

### 2.1 Core Layers
1. **Core (State & Context)**:
   - `AppContext`: Global singleton managing service registration and thread pools.
   - `EventBus`: Pub/Sub mechanism for decoupled cross-module communication.
   - `WindowManager`: Handles high-DPI scaling and window lifecycle.

2. **Services (Logic & IO)**:
   - `AdbWrapper`: Low-level CLI bridge for ADB commands.
   - `DeviceManager`: Hardware lifecycle (Polling, Connection events).
   - `RemoteControlService`: Manages `scrcpy` sessions and auto-installations.
   - `StabilityService`: Orchestrates stress tests and crash monitoring.
   - `AutomationService`: Interfaces with external test suites (TMX).

3. **Views (UI Pages)**:
   - Functional pages (Device Info, Controls, Remote, Stability, Automation).
   - All views inherit from `BaseView` for consistent styling.

4. **Components (Reusable UI)**:
   - Sidebar, TitleBar, Toast system.

## 3. Data Flow
- **Hardware -> UI**: 
  `DeviceManager` (Timer) -> `AdbWrapper` -> `EventBus` -> `MainWindow` (Toast/Update).
- **User -> Action**: 
  `View` -> `Service` (Background Thread) -> `AdbWrapper` -> Device.

## 4. Threading Strategy
TestPilot employs a strict **Non-Blocking UI** policy:
- **Fast Commands**: Run on the Main Thread (e.g., simple `getprop`).
- **Persistent Sessions**: Run in dedicated `threading.Thread` instances (e.g., `scrcpy`, App Loops).
- **Transient Async Ops**: Utilize `QThreadPool` with `Worker` classes (e.g., Property Gathering, Reboots).

## 5. Deployment
- **Windows**: Bundled as a single executable via PyInstaller.
- **Linux**: Distributed as a binary with shell scripts to verify `android-tools` and `scrcpy` dependencies.
