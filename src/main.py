"""
Project Lambda Live Log Viewer
Main entry point for the application
"""
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from theme import get_theme


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Project Lambda Live Log Viewer")
    
    # Initialize and apply theme
    theme = get_theme()
    theme.apply_to_app()
    
    window = MainWindow()
    window.showMaximized()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

