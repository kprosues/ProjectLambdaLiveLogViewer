# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Get the directory containing this spec file
# Since build.py sets cwd to the project root, we can use that
# But also try to get it from SPECPATH or __file__ for robustness
spec_root = None

# Method 1: Try SPECPATH (PyInstaller variable)
try:
    if 'SPECPATH' in globals() and SPECPATH:
        spec_path = os.path.abspath(SPECPATH)
        # If SPECPATH is a file, get its directory; if it's a dir, use it
        if os.path.isfile(spec_path):
            spec_root = os.path.dirname(spec_path)
        else:
            spec_root = spec_path
except (NameError, TypeError):
    pass

# Method 2: Try __file__ (if available in spec context)
if spec_root is None:
    try:
        spec_root = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass

# Method 3: Use current working directory (build.py sets this to project root)
if spec_root is None:
    spec_root = os.getcwd()

# Method 4: Try to find build.spec in current directory or parent
if not os.path.exists(os.path.join(spec_root, 'build.spec')):
    # Try parent directory
    parent = os.path.dirname(spec_root)
    if os.path.exists(os.path.join(parent, 'build.spec')):
        spec_root = parent
    # Or use current directory if build.spec exists there
    elif os.path.exists('build.spec'):
        spec_root = os.getcwd()

# Import version information
import importlib.util
src_path = os.path.join(spec_root, 'src')
version_file = os.path.join(src_path, '__version__.py')

# Verify the version file exists
if not os.path.exists(version_file):
    raise FileNotFoundError(f"Version file not found at: {version_file}\nSpec root: {spec_root}")

spec = importlib.util.spec_from_file_location("__version__", version_file)
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)

VERSION_MAJOR = version_module.VERSION_MAJOR
VERSION_MINOR = version_module.VERSION_MINOR
VERSION_PATCH = version_module.VERSION_PATCH
VERSION_STRING = version_module.VERSION_STRING
APP_NAME = version_module.APP_NAME
APP_DESCRIPTION = version_module.APP_DESCRIPTION
COMPANY_NAME = version_module.COMPANY_NAME
COPYRIGHT = version_module.COPYRIGHT

# Generate version info file for Windows executable
version_info_path = os.path.join(spec_root, 'version_info.txt')
version_info_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({VERSION_MAJOR}, {VERSION_MINOR}, {VERSION_PATCH}, 0),
    prodvers=({VERSION_MAJOR}, {VERSION_MINOR}, {VERSION_PATCH}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{COMPANY_NAME}'),
        StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{VERSION_STRING}.0'),
        StringStruct(u'InternalName', u'ProjectLambdaLiveLogViewer'),
        StringStruct(u'LegalCopyright', u'{COPYRIGHT}'),
        StringStruct(u'OriginalFilename', u'ProjectLambdaLiveLogViewer.exe'),
        StringStruct(u'ProductName', u'{APP_NAME}'),
        StringStruct(u'ProductVersion', u'{VERSION_STRING}.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
with open(version_info_path, 'w', encoding='utf-8') as f:
    f.write(version_info_content)

a = Analysis(
    ['src/main.py'],
    pathex=[spec_root, os.path.join(spec_root, 'src')],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'csv',
        'collections',
        'collections.defaultdict',
        'theme',
        'main_window',
        'data_display',
        'column_config',
        'csv_parser',
        'file_watcher',
        '__version__',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL'],  # Exclude large unused packages
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ProjectLambdaLiveLogViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version=version_info_path,  # Path to version info file
    onefile=True,  # Create a single portable executable
)

