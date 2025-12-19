"""
Version information for Project Lambda Live Log Viewer
Uses semantic versioning: MAJOR.MINOR.PATCH
"""
__version__ = "1.0.0"
__version_info__ = tuple(map(int, __version__.split('.')))

# Version metadata for Windows executable
VERSION_MAJOR = __version_info__[0]
VERSION_MINOR = __version_info__[1]
VERSION_PATCH = __version_info__[2]
VERSION_STRING = __version__

# Additional metadata
APP_NAME = "Project Lambda Live Log Viewer"
APP_DESCRIPTION = "Live CSV log viewer for Project Lambda tuning data"
COMPANY_NAME = "Project Lambda"
COPYRIGHT = f"2025 Keith Proseus"

