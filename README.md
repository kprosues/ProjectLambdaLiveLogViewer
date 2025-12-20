# Project Lambda Live Log Viewer

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

A Windows-compatible desktop application for live-tailing CSV datalog files and displaying the latest row of data in real-time. Designed for automotive tuning applications that log engine parameters.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Build](#build)
- [Project Structure](#project-structure)
- [License](#license)

## 🎯 Overview

Project Lambda Live Log Viewer is a real-time CSV log file monitoring application built with PyQt6. It's specifically designed for automotive tuning scenarios where you need to monitor engine parameters as they're being logged to a CSV file.

The application provides:
- **Real-time monitoring** of CSV log files as they're being written
- **Configurable column display** - show or hide any of the 27+ columns from your log files
- **Visual indicators** - color-coded values for critical parameters (temperatures, AFR, knock, boost)
- **Persistent settings** - your column visibility preferences are saved between sessions
- **Efficient file handling** - uses file position tracking to only read new lines, even from large files

Perfect for tuners who need to monitor engine parameters in real-time while making adjustments.

## ✨ Features

- **Live File Tailing**: Monitors CSV log files and displays new data as it's written
- **Configurable Display**: Show or hide any of the 27+ columns from your log files
- **Color-Coded Values**: Visual indicators for critical parameters (temperatures, AFR, knock, boost)
- **Persistent Settings**: Column visibility preferences are saved between sessions
- **Efficient Monitoring**: Uses file position tracking to only read new lines, even from large files

## 📦 Requirements

- **Python**: 3.11 or higher
- **Operating System**: Windows 10/11 (or compatible OS with PyQt6 support)
- **Dependencies**: See `requirements.txt`

## 🚀 Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/yourusername/ProjectLambdaLiveLogViewer.git
   cd ProjectLambdaLiveLogViewer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### Running the Application

From the project root directory:
```bash
python src/main.py
```

Or from the `src` directory:
```bash
cd src
python main.py
```

### Using the Application

1. Click **"Select Log File..."** to browse for a CSV log file
2. The application will automatically start monitoring the file
3. Use the left panel to check/uncheck columns you want to display
4. The right panel shows the latest row of data with all visible parameters
5. Click **"Stop Watching"** to stop monitoring and select a different file

### CSV File Format

The application expects CSV files with:
- Header row with column names and units in parentheses: `Column Name (unit)`
- Comma-separated values
- Example format: `Time (s),Engine Speed (rpm),Air/Fuel Sensor #1 (λ),...`

See `exampleFiles/tuner_log_25-12-18_1501.csv` for a sample file.

## 🔨 Build

This section covers how to build a portable standalone executable that doesn't require Python or any dependencies to be installed.

### Prerequisites

Before building, ensure you have:
- Python 3.11 or higher installed
- All dependencies installed: `pip install -r requirements.txt`
- PyInstaller (included in requirements.txt)

### Building the Executable

#### Option 1: Using the Build Script (Recommended)

The easiest way to build the executable is using the provided build script:

```bash
python build.py
```

This script will:
- Automatically read version information from `src/__version__.py`
- Generate Windows version info metadata
- Build a portable executable using PyInstaller
- Output the executable to `dist/ProjectLambdaLiveLogViewer-{VERSION}.exe`

**Example output:**
```
============================================================
Building Project Lambda Live Log Viewer
Version: 1.2.0
============================================================

Building portable executable...
This may take a few minutes...

============================================================
Build completed successfully!
============================================================

Executable location: dist/ProjectLambdaLiveLogViewer-1.2.0.exe

The executable is portable and can be run on any Windows machine
without requiring Python or any dependencies to be installed.
============================================================
```

#### Option 2: Using PyInstaller Directly

If you prefer to use PyInstaller directly:

```bash
pyinstaller build.spec --clean --noconfirm
```

The executable will be created in the `dist/` directory.

### Build Configuration

The build process uses `build.spec` which is configured to:
- Create a single-file executable (onefile mode)
- Bundle all dependencies into the executable
- Include Windows version information
- Exclude unnecessary packages to reduce size
- Generate a console-free GUI application

### Build Output

After a successful build, you'll find:
- **Executable**: `dist/ProjectLambdaLiveLogViewer-{VERSION}.exe`
- **Build artifacts**: `build/` directory (can be safely deleted)

### Distribution

The generated `ProjectLambdaLiveLogViewer-{VERSION}.exe` is a **portable standalone executable** that:
- ✅ Requires no Python installation
- ✅ Requires no additional dependencies
- ✅ Can be copied to any Windows 10/11 machine and run directly
- ✅ All dependencies are bundled into the single .exe file

Simply distribute the `.exe` file - no installation required!

### Troubleshooting Build Issues

**Issue**: `PyInstaller is not installed`
- **Solution**: Run `pip install pyinstaller` or `pip install -r requirements.txt`

**Issue**: `Version file not found`
- **Solution**: Ensure `src/__version__.py` exists and contains version information

**Issue**: Build fails with import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Executable is very large
- **Solution**: This is normal - PyQt6 and all dependencies are bundled. The executable is typically 50-100MB.

## 📁 Project Structure

```
ProjectLambdaLiveLogViewer/
├── src/
│   ├── main.py              # Application entry point
│   ├── main_window.py       # Main window and UI layout
│   ├── file_watcher.py      # File monitoring thread
│   ├── csv_parser.py        # CSV parsing and column detection
│   ├── data_display.py      # Live data display widget
│   ├── column_config.py     # Column visibility configuration
│   ├── theme.py             # Application theme and styling
│   └── __version__.py       # Version information
├── exampleFiles/            # Sample log files
├── build/                   # Build artifacts (generated)
├── dist/                    # Distribution executables (generated)
├── requirements.txt         # Python dependencies
├── build.spec               # PyInstaller build configuration
├── build.py                 # Build script
└── README.md                # This file
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Keith Proseus
