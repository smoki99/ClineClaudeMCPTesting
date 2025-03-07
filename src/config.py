#!/usr/bin/env python3

from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Central configuration for the video generator project"""
    
    # Base paths
    BASE_DIR = Path('D:/dev/ClineClaudeMCPTesting')
    
    # FFmpeg configuration
    FFMPEG_DIR = BASE_DIR / 'ffmpeg-7.1-full_build-shared/bin'
    FFMPEG_PATH = FFMPEG_DIR / 'ffmpeg.exe'
    FFPROBE_PATH = FFMPEG_DIR / 'ffprobe.exe'
    
    # Input directories (read-only)
    CLIPS_DIR = BASE_DIR / 'clips'
    MUSIC_DIR = BASE_DIR / 'music'
    
    # Working directories (can be modified)
    OUTPUT_DIR = BASE_DIR / 'output'
    TEMP_DIR = BASE_DIR / 'temp'
    TEST_DIR = BASE_DIR / 'test_files'
    TEST_RESULTS_DIR = BASE_DIR / 'test_results'
    
    # Video configuration
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    VIDEO_QUALITY_CRF = 23  # Lower is better quality (18-28 is typical)
    VIDEO_PRESET = 'medium'  # Encoding speed preset
    
    # Audio configuration
    AUDIO_FADE_DURATION = 2.0  # Crossfade duration in seconds
    
    @classmethod
    def setup(cls):
        """Create necessary directories but not read-only ones"""
        try:
            # Create working directories
            cls.OUTPUT_DIR.mkdir(exist_ok=True)
            cls.TEMP_DIR.mkdir(exist_ok=True)
            cls.TEST_DIR.mkdir(exist_ok=True)
            cls.TEST_RESULTS_DIR.mkdir(exist_ok=True)
            
            # Add FFmpeg to PATH if not already there
            if cls.FFMPEG_DIR and str(cls.FFMPEG_DIR) not in os.environ['PATH']:
                os.environ['PATH'] = f"{str(cls.FFMPEG_DIR)};{os.environ['PATH']}"
                logger.info(f"Added FFmpeg directory to PATH: {cls.FFMPEG_DIR}")
                
            logger.info("Configuration setup completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Configuration setup failed: {e}")
            return False
    
    @classmethod
    def validate(cls):
        """Validate required paths and permissions"""
        try:
            # Check read-only directories exist
            if not cls.CLIPS_DIR.exists():
                raise RuntimeError(f"Clips directory not found: {cls.CLIPS_DIR}")
            if not cls.MUSIC_DIR.exists():
                raise RuntimeError(f"Music directory not found: {cls.MUSIC_DIR}")
                
            # Check FFmpeg exists
            if not cls.FFMPEG_PATH.exists():
                raise RuntimeError(f"FFmpeg not found: {cls.FFMPEG_PATH}")
            if not cls.FFPROBE_PATH.exists():
                raise RuntimeError(f"FFprobe not found: {cls.FFPROBE_PATH}")
                
            # Check read-only permissions
            try:
                next(cls.CLIPS_DIR.iterdir())
                next(cls.MUSIC_DIR.iterdir())
            except PermissionError:
                raise RuntimeError("Insufficient permissions for input directories")
                
            logger.info("Configuration validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    @classmethod
    def to_dict(cls):
        """Export configuration as dictionary"""
        return {
            'ffmpeg_path': str(cls.FFMPEG_PATH),
            'ffprobe_path': str(cls.FFPROBE_PATH),
            'clips_dir': str(cls.CLIPS_DIR),
            'music_dir': str(cls.MUSIC_DIR),
            'output_dir': str(cls.OUTPUT_DIR),
            'temp_dir': str(cls.TEMP_DIR),
            'test_dir': str(cls.TEST_DIR),
            'test_results_dir': str(cls.TEST_RESULTS_DIR),
            'video_width': cls.VIDEO_WIDTH,
            'video_height': cls.VIDEO_HEIGHT,
            'video_quality_crf': cls.VIDEO_QUALITY_CRF,
            'video_preset': cls.VIDEO_PRESET,
            'audio_fade_duration': cls.AUDIO_FADE_DURATION
        }

    @classmethod
    def get_ffmpeg_base_command(cls):
        """Get base FFmpeg command with proper executable path"""
        return [str(cls.FFMPEG_PATH)]

    @classmethod
    def get_ffprobe_base_command(cls):
        """Get base FFprobe command with proper executable path"""
        return [str(cls.FFPROBE_PATH)]

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Validate configuration on import
if not Config.validate():
    logger.warning("Configuration validation failed - some features may not work")
