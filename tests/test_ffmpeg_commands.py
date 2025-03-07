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

def test_audio_concat():
    """Test audio concatenation with crossfade"""
    logger.info("Testing audio concatenation...")
    
    cmd = Config.get_ffmpeg_base_command() + [
        '-i', str(Config.MUSIC_DIR / '01-Cherry Neon Blossoms.mp3'),
        '-i', str(Config.MUSIC_DIR / '02-Neon Dreamscape.mp3'),
        '-filter_complex',
        '[0:a][1:a]acrossfade=d=2:c1=tri:c2=tri[out]',
        '-map', '[out]',
        str(test_dir / 'output_concat.mp3')
    ]
    
    success = _run_ffmpeg(cmd)
    if success:
        logger.info("Audio concatenation test completed")
        _analyze_output('output_concat.mp3')
    assert success

def test_video_encoding():
    """Test libx264 encoding settings"""
    logger.info("Testing video encoding...")
    
    cmd = Config.get_ffmpeg_base_command() + [
        '-i', str(Config.CLIPS_DIR / 'girls1.mp4'),  # Using existing clip
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-tune', 'film',
        '-movflags', '+faststart',
        str(test_dir / 'output_encoded.mp4')
    ]
    
    success = _run_ffmpeg(cmd)
    if success:
        logger.info("Video encoding test completed")
        _analyze_output('output_encoded.mp4')
    assert success

def test_text_overlay():
    """Test text overlay with fade effect"""
    logger.info("Testing text overlay...")
    
    cmd = Config.get_ffmpeg_base_command() + [
        '-i', str(Config.CLIPS_DIR / 'girls1.mp4'),  # Using existing clip
        '-vf', "drawtext=text='Test Track':fontcolor=white:fontsize=24:"
              "x=(w-text_w)/2:y=h-th-10:"
              "alpha='if(lt(t,1),t,if(lt(t,3),1,if(lt(t,4),4-t,0)))'",
        str(test_dir / 'output_overlay.mp4')
    ]
    
    success = _run_ffmpeg(cmd)
    if success:
        logger.info("Text overlay test completed")
        _analyze_output('output_overlay.mp4')
    assert success

def test_concat_protocol():
    """Test FFmpeg concat protocol for efficient joining"""
    logger.info("Testing concat protocol...")

    # Create concat file
    with open(Config.CLIPS_DIR / 'concat.txt', 'w') as f:
        f.write(f"file \'girls1.mp4\'\n")
        f.write(f"file \'girls1.mp4\'\n")

    cmd = Config.get_ffmpeg_base_command() + [
        '-f', 'concat',
        '-safe', '0',
        '-i', str(Config.CLIPS_DIR / 'concat.txt'),
        '-c', 'copy',
        str(test_dir / 'output_concat.mp4')
    ]

    success = _run_ffmpeg(cmd)
    if success:
        logger.info("Concat protocol test completed")
        _analyze_output('output_concat.mp4')
    assert success
