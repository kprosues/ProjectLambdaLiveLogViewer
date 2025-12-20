"""
File watcher for monitoring CSV log files
Uses watchdog to detect file changes and efficiently tail new lines
"""
import os
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
        self.last_known_size = 0  # Cache file size to avoid unnecessary stat() calls
        self._read_initial_position()
    
    def _read_initial_position(self):
        """Set initial position to end of file to only read new lines"""
        if self.file_path.exists():
            # Read to the last complete line, not just the end of file
            # This ensures we don't miss data if a line is being written
            try:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read to find the last complete line
                    f.seek(0, 2)  # Seek to end
                    file_size = f.tell()
                    self.last_known_size = file_size  # Cache file size
                    if file_size == 0:
                        self.last_position = 0
                        return
                    
                    # Read backwards to find the last newline
                    chunk_size = min(1024, file_size)
                    f.seek(max(0, file_size - chunk_size))
                    chunk = f.read(chunk_size)
                    last_newline = chunk.rfind('\n')
                    
                    if last_newline >= 0:
                        # Found a newline, position is after it
                        self.last_position = file_size - chunk_size + last_newline + 1
                    else:
                        # No newline found in chunk, check if file ends with newline
                        f.seek(max(0, file_size - 1))
                        last_char = f.read(1)
                        if last_char == '\n':
                            self.last_position = file_size
                        else:
                            # Incomplete line, start from beginning of chunk
                            self.last_position = max(0, file_size - chunk_size)
            except Exception:
                # Fallback to simple size if there's an error
                file_size = self.file_path.stat().st_size
                self.last_known_size = file_size
                self.last_position = file_size
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and Path(event.src_path) == self.file_path:
            self._read_new_lines()
    
    def on_created(self, event):
        """Handle file creation events (for file rotation)"""
        if not event.is_directory and Path(event.src_path) == self.file_path:
            self.last_position = 0
            self.last_known_size = 0  # Reset cached size for new file
            self._read_new_lines()
    
    def _read_new_lines(self):
        """Read new lines from the file since last position"""
        try:
            if not self.file_path.exists():
                return
            
            # Check file size first - avoid opening file if nothing changed
            current_size = self.file_path.stat().st_size
            
            # Skip if file size hasn't changed (optimization for polling)
            if current_size == self.last_known_size:
                return
            
            self.last_known_size = current_size
            
            # Handle file truncation/rotation
            if current_size < self.last_position:
                self.last_position = 0
            
            if current_size > self.last_position:
                with open(self.file_path, 'rb') as f:  # Open in binary mode for accurate position tracking
                    f.seek(self.last_position)
                    # Read all new data as bytes
                    new_data_bytes = f.read(current_size - self.last_position)
                    
                    if new_data_bytes:
                        # Process bytes directly to find line boundaries
                        # This avoids decode/rejoin/re-encode overhead
                        start_idx = 0
                        bytes_processed = 0
                        
                        while True:
                            # Find next newline in bytes
                            newline_idx = new_data_bytes.find(b'\n', start_idx)
                            
                            if newline_idx == -1:
                                # No more complete lines, partial line remains
                                break
                            
                            # Extract line bytes (from start_idx to newline_idx, inclusive)
                            line_bytes = new_data_bytes[start_idx:newline_idx]
                            
                            # Decode only this line
                            try:
                                line = line_bytes.decode('utf-8', errors='ignore').strip()
                                if line:  # Skip empty lines
                                    self.new_line_signal.emit(line)
                            except Exception:
                                pass  # Skip lines that can't be decoded
                            
                            # Update position: line bytes + newline byte
                            bytes_processed += len(line_bytes) + 1
                            start_idx = newline_idx + 1
                        
                        # Update last_position with bytes we've processed
                        self.last_position += bytes_processed
                        # If there's a partial last line, position stays at start of that line
                        # It will be read when the line is completed (next time file grows)
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

