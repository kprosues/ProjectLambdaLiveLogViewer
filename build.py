"""
Build script for creating a portable executable
Run this script to build the application as a standalone .exe file
"""
import subprocess
import sys
import os

def build_exe():
    """Build the executable using PyInstaller"""
    print("Building portable executable...")
    print("This may take a few minutes...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller is not installed.")
        print("Please install it by running: pip install pyinstaller")
        sys.exit(1)
    
    # Run PyInstaller with the spec file
    try:
        result = subprocess.run(
            ['pyinstaller', 'build.spec', '--clean', '--noconfirm'],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("\n" + "="*60)
        print("Build completed successfully!")
        print("="*60)
        print(f"\nExecutable location: dist/ProjectLambdaLiveLogViewer.exe")
        print("\nThe executable is portable and can be run on any Windows machine")
        print("without requiring Python or any dependencies to be installed.")
        print("="*60)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Build failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: PyInstaller command not found.")
        print("Please ensure PyInstaller is installed and in your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()

