"""
Launcher script for Project Lambda Live Log Viewer
Run this from the project root directory
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    main()

