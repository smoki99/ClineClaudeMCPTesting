#!/usr/bin/env python3

"""
Pre-commit hook to check file sizes and prevent large files from being committed.
Excludes designated media directories (clips/, music/).
"""

import os
import sys
from pathlib import Path

# Configuration
MAX_SIZE_MB = 100  # Maximum file size in MB
EXCLUDED_DIRS = ['clips', 'music']  # Directories to exclude
EXCLUDED_EXTENSIONS = ['.mp4', '.mp3', '.wav']  # File extensions to exclude

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    return os.path.getsize(file_path) / (1024 * 1024)

def should_check_file(file_path: Path) -> bool:
    """Determine if file should be checked based on path and extension."""
    # Check if file is in excluded directory
    for excluded_dir in EXCLUDED_DIRS:
        if excluded_dir in file_path.parts:
            return False
    
    # Check if file has excluded extension
    if file_path.suffix.lower() in EXCLUDED_EXTENSIONS:
        return False
    
    return True

def main(files):
    """Check each file's size."""
    exit_code = 0
    
    for file_path in files:
        path = Path(file_path)
        
        if not path.exists():
            continue
            
        if not should_check_file(path):
            continue
            
        size_mb = get_file_size_mb(path)
        if size_mb > MAX_SIZE_MB:
            print(f"Error: {file_path} is too large ({size_mb:.1f}MB > {MAX_SIZE_MB}MB)")
            exit_code = 1
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
