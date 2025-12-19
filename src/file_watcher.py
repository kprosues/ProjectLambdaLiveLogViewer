"""
File watcher for monitoring CSV log files
Uses watchdog to detect file changes and efficiently tail new lines
"""
import os
import time
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CSVFileWatcher(FileSystemEventHandler):
    """File system event handler for CSV log files"""
    
    def __init__(self, file_path: str, new_line_signal: pyqtSignal):
        super().__init__()
        self.file_path = Path(file_path)
        self.new_line_signal = new_line_signal
        self.last_position = 0
        self._read_initial_position()
    
    def _read_initial_position(self):
        """Set initial position to end of file to only read new lines"""
        if self.file_path.exists():
            self.last_position = self.file_path.stat().st_size
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and Path(event.src_path) == self.file_path:
            self._read_new_lines()
    
    def on_created(self, event):
        """Handle file creation events (for file rotation)"""
        if not event.is_directory and Path(event.src_path) == self.file_path:
            self.last_position = 0
            self._read_new_lines()
    
    def _read_new_lines(self):
        """Read new lines from the file since last position"""
        try:
            if not self.file_path.exists():
                return
            
            current_size = self.file_path.stat().st_size
            
            # Handle file truncation/rotation
            if current_size < self.last_position:
                self.last_position = 0
            
            if current_size > self.last_position:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    
                    # Process each new line
                    for line in new_lines:
                        line = line.strip()
                        if line:  # Skip empty lines
                            self.new_line_signal.emit(line)
                    
                    self.last_position = f.tell()
        except Exception as e:
            print(f"Error reading file: {e}")


class FileWatcherThread(QThread):
    """Thread for watching file changes"""
    
    new_line = pyqtSignal(str)  # Signal emitted when a new line is read
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[CSVFileWatcher] = None
        self._running = True
    
    def run(self):
        """Start watching the file"""
        if not os.path.exists(self.file_path):
            return
        
        directory = os.path.dirname(os.path.abspath(self.file_path))
        
        self.event_handler = CSVFileWatcher(self.file_path, self.new_line)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, directory, recursive=False)
        self.observer.start()
        
        # Also poll periodically as a fallback (watchdog may miss some events)
        while self._running:
            if self.event_handler:
                self.event_handler._read_new_lines()
            self.msleep(100)  # Poll every 100ms
    
    def stop(self):
        """Stop watching the file"""
        self._running = False
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=1.0)
        self.wait(1000)  # Wait up to 1 second for thread to finish

