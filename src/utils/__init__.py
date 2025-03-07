"""
Utility functions for YouTube Video Generator

This module provides:
- FFmpeg process management
- File handling helpers
- Progress monitoring
- Error handling
- Logging setup
"""

__version__ = '0.1.0'

# Common logging setup
import logging

def setup_logging(level=logging.INFO):
    """Configure logging with standard format"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)
