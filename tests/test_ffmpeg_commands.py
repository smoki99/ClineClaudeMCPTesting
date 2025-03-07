#!/usr/bin/env python3

import os
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.config import Config

class FFmpegTester:
    """Test FFmpeg commands and their behavior"""
    
    def __init__(self):
        # Initialize configuration
        Config.setup()
        if not Config.validate():
            raise RuntimeError("Configuration validation failed")
            
        self.test_dir = Config.TEST_DIR
        self.results_dir = Config.TEST_RESULTS_DIR
        
    def _run_ffmpeg(self, cmd):
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

    def test_audio_concat(self):
        """Test audio concatenation with crossfade"""
        logger.info("Testing audio concatenation...")
        
        cmd = Config.get_ffmpeg_base_command() + [
            '-i', str(Config.MUSIC_DIR / 'test_audio1.mp3'),
            '-i', str(Config.MUSIC_DIR / 'test_audio2.mp3'),
            '-filter_complex',
            '[0:a][1:a]acrossfade=d=2:c1=tri:c2=tri[out]',
            '-map', '[out]',
            str(self.test_dir / 'output_concat.mp3')
        ]
        
        success = self._run_ffmpeg(cmd)
        if success:
            logger.info("Audio concatenation test completed")
            self._analyze_output('output_concat.mp3')
        return success

    def test_video_encoding(self):
        """Test libx264 encoding settings"""
        logger.info("Testing video encoding...")
        
        cmd = Config.get_ffmpeg_base_command() + [
            '-i', str(Config.CLIPS_DIR / 'girls1.mp4'),  # Using existing clip
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-tune', 'film',
            '-movflags', '+faststart',
            str(self.test_dir / 'output_encoded.mp4')
        ]
        
        success = self._run_ffmpeg(cmd)
        if success:
            logger.info("Video encoding test completed")
            self._analyze_output('output_encoded.mp4')
        return success

    def test_text_overlay(self):
        """Test text overlay with fade effect"""
        logger.info("Testing text overlay...")
        
        cmd = Config.get_ffmpeg_base_command() + [
            '-i', str(Config.CLIPS_DIR / 'girls1.mp4'),  # Using existing clip
            '-vf', "drawtext=text='Test Track':fontcolor=white:fontsize=24:"
                  "x=(w-text_w)/2:y=h-th-10:"
                  "alpha='if(lt(t,1),t,if(lt(t,3),1,if(lt(t,4),4-t,0)))'",
            str(self.test_dir / 'output_overlay.mp4')
        ]
        
        success = self._run_ffmpeg(cmd)
        if success:
            logger.info("Text overlay test completed")
            self._analyze_output('output_overlay.mp4')
        return success

    def test_concat_protocol(self):
        """Test FFmpeg concat protocol for efficient joining"""
        logger.info("Testing concat protocol...")
        
        # Create concat file
        with open(self.test_dir / 'concat.txt', 'w') as f:
            f.write("file 'test_clip1.mp4'\n")
            f.write("file 'test_clip2.mp4'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(self.test_dir / 'concat.txt'),
            '-c', 'copy',
            str(self.test_dir / 'output_concat.mp4')
        ]
        
        success = self._run_ffmpeg(cmd)
        if success:
            logger.info("Concat protocol test completed")
            self._analyze_output('output_concat.mp4')
        return success

    def _analyze_output(self, filename):
        """Analyze output file properties"""
        cmd = Config.get_ffprobe_base_command() + [
            '-v', 'error',
            '-show_entries',
            'format=duration,size:stream=codec_type,codec_name',
            '-of', 'json',
            str(self.test_dir / filename)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Output analysis for {filename}:")
                logger.info(result.stdout)
        except Exception as e:
            logger.error(f"Analysis error: {e}")

    def cleanup(self):
        """Clean up test files"""
        logger.info("Cleaning up test files...")
        for file in self.test_dir.glob('output_*'):
            file.unlink()
        if (self.test_dir / 'concat.txt').exists():
            (self.test_dir / 'concat.txt').unlink()

def main():
    """Run all FFmpeg tests"""
    try:
        tester = FFmpegTester()
        
        # Run tests
        tests = [
            ('Audio Concatenation', tester.test_audio_concat),
            ('Video Encoding', tester.test_video_encoding),
            ('Text Overlay', tester.test_text_overlay),
            ('Concat Protocol', tester.test_concat_protocol)
        ]
        
        results = {}
        for name, test_func in tests:
            logger.info(f"Running {name} test...")
            try:
                success = test_func()
                results[name] = 'Success' if success else 'Failed'
            except Exception as e:
                logger.error(f"{name} test error: {e}")
                results[name] = f'Error: {str(e)}'
        
        # Save results
        with open(Config.TEST_RESULTS_DIR / 'ffmpeg_tests.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info("Test results saved to ffmpeg_tests.json")
        
    except Exception as e:
        logger.error(f"Test suite error: {e}")
    finally:
        # Clean up
        if 'tester' in locals():
            tester.cleanup()

if __name__ == '__main__':
    main()
