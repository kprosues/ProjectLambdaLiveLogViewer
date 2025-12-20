"""
Main window for the Live Log Viewer application
"""
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QStatusBar, QScrollArea, QGroupBox,
    QInputDialog, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QAction

from csv_parser import CSVParser
from file_watcher import FileWatcherThread
from data_display import DataDisplayWidget
from column_config import ColumnConfigDialog
from theme import get_theme
from __version__ import VERSION_STRING, APP_NAME


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_file: Optional[str] = None
        self.parser: Optional[CSVParser] = None
        self.watcher_thread: Optional[FileWatcherThread] = None
        # Font size defaults
        self.title_font_size = 40
        self.value_font_size = 70
        self.theme = get_theme()
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{APP_NAME} v{VERSION_STRING}")
        # Larger default window size for better visibility
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Top bar with file selection
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Column configuration dialog (created but not shown)
        self.column_config = ColumnConfigDialog(self)
        self.column_config.visibility_changed.connect(self._on_visibility_changed)
        
        # Data display panel - takes up all remaining space
        self.data_display = DataDisplayWidget()
        main_layout.addWidget(self.data_display, 1)  # Stretch factor of 1 to fill remaining space
        
        # Status bar
        self.statusBar().showMessage("Ready - No file selected")
        
        # Apply theme
        self._apply_theme()
    
    def _create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Open file action
        open_action = QAction("&Open Log File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._select_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Column visibility action
        self.column_visibility_action = QAction("Column &Visibility...", self)
        self.column_visibility_action.setShortcut("Ctrl+V")
        self.column_visibility_action.triggered.connect(self._show_column_visibility)
        self.column_visibility_action.setEnabled(False)  # Disabled until file is loaded
        file_menu.addAction(self.column_visibility_action)
        
        file_menu.addSeparator()
        
        # Font size submenu
        font_menu = file_menu.addMenu("Font &Size")
        
        # Title font size action
        title_font_action = QAction("&Title Font Size...", self)
        title_font_action.triggered.connect(self._adjust_title_font_size)
        font_menu.addAction(title_font_action)
        
        # Value font size action
        value_font_action = QAction("&Value Font Size...", self)
        value_font_action.triggered.connect(self._adjust_value_font_size)
        font_menu.addAction(value_font_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Dark mode toggle
        self.dark_mode_action = QAction("&Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.theme.is_dark_mode)
        self.dark_mode_action.triggered.connect(self._toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
    
    def _show_column_visibility(self):
        """Show the column visibility dialog"""
        self.column_config.exec()
    
    def _create_top_bar(self) -> QWidget:
        """Create the top bar with file selection controls"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # File selection button - made 3x bigger for easier touch interaction
        self.file_button = QPushButton("Select Log File...")
        self.file_button.setMinimumHeight(60)  # 3x larger (from ~20px default)
        self.file_button.setMinimumWidth(300)  # 3x larger (from ~100px default)
        self.file_button.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.file_button.clicked.connect(self._select_file)
        layout.addWidget(self.file_button)
        
        # Current file label
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label, 1)
        
        # Stop button
        self.stop_button = QPushButton("Stop Watching")
        self.stop_button.clicked.connect(self._stop_watching)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        return widget
    
    def _select_file(self):
        """Open file dialog to select a CSV log file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _load_file(self, file_path: str):
        """Load and start watching a CSV file"""
        try:
            # Stop existing watcher if any
            self._stop_watching()
            
            # Validate file exists
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Error", f"File not found: {file_path}")
                return
            
            # Initialize parser
            self.parser = CSVParser(file_path)
            column_info = self.parser.get_column_info()
            
            # Update UI with column info
            self.column_config.set_columns(column_info)
            self.data_display.set_column_info(column_info)
            
            # Apply current font sizes
            self.data_display.set_title_font_size(self.title_font_size)
            self.data_display.set_value_font_size(self.value_font_size)
            header_size = max(12, int(self.title_font_size * 0.85))
            self.data_display.set_header_font_size(header_size)
            
            # Update file label
            self.current_file = file_path
            file_name = os.path.basename(file_path)
            self.file_label.setText(f"Watching: {file_name}")
            success_color = self.theme.get_color('status_success')
            self.file_label.setStyleSheet(f"color: {success_color}; padding: 5px; font-weight: bold;")
            
            # Read existing data BEFORE starting watcher to ensure we display latest values
            # This must happen before watcher starts, as watcher will set position to end of file
            self._read_existing_data()
            
            # Start file watcher (will set position to end of file to only read new lines)
            self.watcher_thread = FileWatcherThread(file_path)
            self.watcher_thread.new_line.connect(self._on_new_line)
            self.watcher_thread.start()
            
            # Update UI state
            self.file_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.column_visibility_action.setEnabled(True)
            self.statusBar().showMessage(f"Watching: {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
            self._stop_watching()
    
    def _read_existing_data(self):
        """Read the last complete line of the file to display initial data (without tracking for averages)"""
        if not self.parser or not self.current_file:
            return
        
        try:
            with open(self.current_file, 'rb') as f:
                # Read file in binary mode to check if it ends with newline
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()
                if file_size == 0:
                    return
                
                # Check if file ends with newline
                f.seek(max(0, file_size - 1))
                last_char = f.read(1)
                ends_with_newline = (last_char == b'\n')
                
                # Read all lines
                f.seek(0)
                content = f.read().decode('utf-8', errors='ignore')
                lines = content.split('\n')
                
                if len(lines) > 1:  # Has header + at least one data row
                    # If file ends with newline, last line in split will be empty, so use second-to-last
                    # Otherwise, last line might be incomplete, so use second-to-last
                    line_index = len(lines) - 2 if ends_with_newline else len(lines) - 2
                    if line_index < 1:
                        line_index = len(lines) - 1  # Fallback to last line
                    
                    # Try lines from the end backwards until we find a valid one
                    for i in range(line_index, 0, -1):  # Start from candidate, go backwards to header
                        line = lines[i].strip()
                        if line:
                            data = self.parser.parse_row(line)
                            if data:
                                # Display the last complete row but don't track values for average calculation
                                # Only values observed while tailing will be used for averages
                                self.data_display.update_data(data, update_display=True, track_values=False)
                                break
        except Exception as e:
            print(f"Error reading existing data: {e}")
    
    @pyqtSlot(str)
    def _on_new_line(self, line: str):
        """Handle new line from file watcher"""
        if not self.parser:
            return
        
        data = self.parser.parse_row(line)
        if data:
            self.data_display.update_data(data)
            # Update status bar with timestamp
            self.statusBar().showMessage(f"Last update: {data.get('Time (s)', 'N/A')}s")
    
    @pyqtSlot(dict)
    def _on_visibility_changed(self, visibility: dict):
        """Handle column visibility changes"""
        self.data_display.set_visible_columns(visibility)
    
    def _adjust_title_font_size(self):
        """Show dialog to adjust title font size"""
        size, ok = QInputDialog.getInt(
            self,
            "Title Font Size",
            "Enter title font size (8-100):",
            self.title_font_size,
            8,
            100,
            1
        )
        if ok:
            self.title_font_size = size
            self.data_display.set_title_font_size(size)
            # Update header size proportionally (header is typically smaller)
            header_size = max(12, int(size * 0.85))
            self.data_display.set_header_font_size(header_size)
    
    def _adjust_value_font_size(self):
        """Show dialog to adjust value font size"""
        size, ok = QInputDialog.getInt(
            self,
            "Value Font Size",
            "Enter value font size (8-200):",
            self.value_font_size,
            8,
            200,
            1
        )
        if ok:
            self.value_font_size = size
            self.data_display.set_value_font_size(size)
    
    def _stop_watching(self):
        """Stop watching the current file"""
        if self.watcher_thread:
            self.watcher_thread.stop()
            self.watcher_thread = None
        
        self.parser = None
        self.current_file = None
        
        # Reset UI
        self.file_label.setText("No file selected")
        secondary_color = self.theme.get_color('label_secondary')
        self.file_label.setStyleSheet(f"color: {secondary_color}; padding: 5px;")
        self.file_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.column_visibility_action.setEnabled(False)
        self.statusBar().showMessage("Ready - No file selected")
        
        # Clear displays
        self.data_display.update_data({})
        self.column_config.set_columns([])
    
    def _apply_theme(self):
        """Apply theme to the window and all widgets"""
        # Apply theme to application
        self.theme.apply_to_app()
        
        # Apply stylesheet
        self.setStyleSheet(self.theme.get_stylesheet())
        
        # Update file label color if needed
        if self.current_file:
            success_color = self.theme.get_color('status_success')
            file_name = os.path.basename(self.current_file)
            self.file_label.setText(f"Watching: {file_name}")
            self.file_label.setStyleSheet(f"color: {success_color}; padding: 5px; font-weight: bold;")
        else:
            secondary_color = self.theme.get_color('label_secondary')
            self.file_label.setStyleSheet(f"color: {secondary_color}; padding: 5px;")
        
        # Update data display theme
        self.data_display.apply_theme(self.theme)
        
        # Update column config theme
        self.column_config.apply_theme(self.theme)
    
    def _toggle_dark_mode(self):
        """Toggle dark mode"""
        self.theme.toggle_dark_mode()
        self.dark_mode_action.setChecked(self.theme.is_dark_mode)
        self._apply_theme()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self._stop_watching()
        event.accept()

