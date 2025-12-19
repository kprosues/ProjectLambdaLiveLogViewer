# Project Lambda Live Log Viewer

A Windows-compatible desktop application for live-tailing CSV datalog files and displaying the latest row of data in real-time. Designed for automotive tuning applications that log engine parameters.

## Features

- **Live File Tailing**: Monitors CSV log files and displays new data as it's written
- **Configurable Display**: Show or hide any of the 27+ columns from your log files
- **Color-Coded Values**: Visual indicators for critical parameters (temperatures, AFR, knock, boost)
- **Persistent Settings**: Column visibility preferences are saved between sessions
- **Efficient Monitoring**: Uses file position tracking to only read new lines, even from large files

## Requirements

- Python 3.11 or higher
- Windows 10/11 (or compatible OS with PyQt6 support)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

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

1. Click "Select Log File..." to browse for a CSV log file
2. The application will automatically start monitoring the file
3. Use the left panel to check/uncheck columns you want to display
4. The right panel shows the latest row of data with all visible parameters
5. Click "Stop Watching" to stop monitoring and select a different file

### CSV File Format

The application expects CSV files with:
- Header row with column names and units in parentheses: `Column Name (unit)`
- Comma-separated values
- Example format: `Time (s),Engine Speed (rpm),Air/Fuel Sensor #1 (λ),...`

See `exampleFiles/tuner_log_25-12-18_1501.csv` for a sample file.

## Building a Portable Executable

To create a standalone portable `.exe` file that doesn't require Python or any dependencies:

### Option 1: Using the Build Script (Recommended)

1. Install PyInstaller (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python build.py
   ```

3. The portable executable will be created in the `dist/` directory as `ProjectLambdaLiveLogViewer.exe`

### Option 2: Using PyInstaller Directly

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller build.spec --clean --noconfirm
   ```

3. The executable will be in the `dist/` directory

### Distribution

The generated `ProjectLambdaLiveLogViewer.exe` is a **portable standalone executable** that:
- Requires no Python installation
- Requires no additional dependencies
- Can be copied to any Windows 10/11 machine and run directly
- All dependencies are bundled into the single .exe file

Simply distribute the `.exe` file - no installation required!

## Project Structure

```
ProjectLambdaLiveLogViewer/
├── src/
│   ├── main.py              # Application entry point
│   ├── main_window.py       # Main window and UI layout
│   ├── file_watcher.py      # File monitoring thread
│   ├── csv_parser.py        # CSV parsing and column detection
│   ├── data_display.py      # Live data display widget
│   └── column_config.py     # Column visibility configuration
├── requirements.txt         # Python dependencies
├── build.spec               # PyInstaller build configuration
└── exampleFiles/            # Sample log files
```

## License

See LICENSE file for details.
