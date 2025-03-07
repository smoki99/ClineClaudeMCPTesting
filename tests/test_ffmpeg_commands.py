#!/usr/bin/env python3

import os
import subprocess
import logging
from pathlib import Path
import json
import pytest
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import Config

# Initialize configuration
Config.setup()
if not Config.validate():
    raise RuntimeError("Configuration validation failed")
    
test_dir = Config.TEST_DIR
results_dir = Config.TEST_RESULTS_DIR
    
def _run_ffmpeg(cmd):
    """Execute FFmpeg command and log output"""
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
        return True
    except Exception as e:
        logger.error(f"Execution error: {e}")
        return False

def _analyze_output(filename):
    """Analyze output file properties"""
    cmd = Config.get_ffprobe_base_command() + [
        '-v', 'error',
        '-show_entries',
        'format=duration,size:stream=codec_type,codec_name',
        '-of', 'json',
        str(test_dir / filename)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Output analysis for {filename}:")
            logger.info(result.stdout)
    except Exception as e:
        logger.error(f"Analysis error: {e}")

def cleanup():
    """Clean up test files"""
    logger.info("Cleaning up test files...")
    for file in test_dir.glob('output_*'):
        file.unlink()
    if (test_dir / 'concat.txt').exists():
        (test_dir / 'concat.txt').unlink()

# Initialize configuration
Config.setup()
if not Config.validate():
    raise RuntimeError("Configuration validation failed")
    
test_dir = Config.TEST_DIR
results_dir = Config.TEST_RESULTS_DIR
    
# Clean up
cleanup()
