#!/usr/bin/env python3

import os
import time
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.config import Config

class PerformanceTester:
    """Test performance metrics for video processing"""
    
    def __init__(self):
        # Initialize configuration
        Config.setup()
        if not Config.validate():
            raise RuntimeError("Configuration validation failed")
            
        self.test_dir = Config.TEST_DIR
        self.results_dir = Config.TEST_RESULTS_DIR
        
        # Get available input files
        self.available_clips = list(Config.CLIPS_DIR.glob('*.mp4'))
        self.available_music = list(Config.MUSIC_DIR.glob('*.mp3'))
        
        if not self.available_clips or not self.available_music:
            raise RuntimeError("No input files found in clips or music directories")
        
    def get_media_duration(self, filepath):
        """Get precise duration of media file"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(filepath)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Duration detection error: {e}")
        return None

    def measure_processing_speed(self, input_file, duration):
        """Measure processing time and resource usage"""
        metrics = {
            'start_time': datetime.now().isoformat(),
            'input_file': str(input_file),
            'target_duration': duration,
            'memory_usage': [],
            'cpu_usage': []
        }
        
        process = psutil.Process()
        start_time = time.time()
        
        cmd = Config.get_ffmpeg_base_command() + [
            '-i', str(input_file),
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            str(self.test_dir / f'output_{duration}s.mp4')
        ]
        
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Monitor resource usage while processing
            while proc.poll() is None:
                metrics['memory_usage'].append(process.memory_info().rss / 1024 / 1024)  # MB
                metrics['cpu_usage'].append(process.cpu_percent())
                time.sleep(1)
            
            end_time = time.time()
            metrics['processing_time'] = end_time - start_time
            
            # Calculate statistics
            metrics['avg_memory_usage'] = sum(metrics['memory_usage']) / len(metrics['memory_usage'])
            metrics['max_memory_usage'] = max(metrics['memory_usage'])
            metrics['avg_cpu_usage'] = sum(metrics['cpu_usage']) / len(metrics['cpu_usage'])
            metrics['max_cpu_usage'] = max(metrics['cpu_usage'])
            
            # Get output file size
            output_file = self.test_dir / f'output_{duration}s.mp4'
            if output_file.exists():
                metrics['output_size'] = output_file.stat().st_size / 1024 / 1024  # MB
            
            return metrics
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return None

    def run_performance_tests(self):
        """Run performance tests with different durations"""
        logger.info("Starting performance tests...")
        
        test_durations = [
            ('1min', 60),
            ('5min', 300),
            ('15min', 900)
        ]
        
        results = {}
        for name, duration in test_durations:
            logger.info(f"Testing {name} duration...")
            input_file = self.test_dir / 'test_clip.mp4'
            
            if not input_file.exists():
                logger.error(f"Test file not found: {input_file}")
                continue
                
            metrics = self.measure_processing_speed(input_file, duration)
            if metrics:
                results[name] = metrics
                
                # Save individual test results
                with open(self.results_dir / f'metrics_{name}.json', 'w') as f:
                    json.dump(metrics, f, indent=2)
                    
                logger.info(f"Results for {name}:")
                logger.info(f"Processing time: {metrics['processing_time']:.2f}s")
                logger.info(f"Average memory usage: {metrics['avg_memory_usage']:.2f}MB")
                logger.info(f"Maximum memory usage: {metrics['max_memory_usage']:.2f}MB")
                logger.info(f"Average CPU usage: {metrics['avg_cpu_usage']:.2f}%")
        
        return results

    def test_concat_performance(self):
        """Test performance of different concat methods"""
        logger.info("Testing concat methods performance...")
        
        methods = {
            'concat_protocol': self._test_concat_protocol,
            'concat_filter': self._test_concat_filter
        }
        
        results = {}
        for name, method in methods.items():
            logger.info(f"Testing {name}...")
            start_time = time.time()
            success = method()
            end_time = time.time()
            
            results[name] = {
                'success': success,
                'processing_time': end_time - start_time
            }
            
        return results

    def _test_concat_protocol(self):
        """Test concat protocol performance"""
        # Use actual clip files for concat test
        with open(self.test_dir / 'concat.txt', 'w') as f:
            for clip in self.available_clips[:2]:  # Use first two clips
                f.write(f"file '{clip}'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(self.test_dir / 'concat.txt'),
            '-c', 'copy',
            str(self.test_dir / 'output_concat_protocol.mp4')
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def _test_concat_filter(self):
        """Test concat filter performance"""
        cmd = [
            'ffmpeg',
            '-i', str(self.test_dir / 'test_clip1.mp4'),
            '-i', str(self.test_dir / 'test_clip2.mp4'),
            '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]',
            '-map', '[v]',
            '-map', '[a]',
            str(self.test_dir / 'output_concat_filter.mp4')
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def cleanup(self):
        """Clean up test files"""
        logger.info("Cleaning up test files...")
        for file in self.test_dir.glob('output_*'):
            file.unlink()
        if (self.test_dir / 'concat.txt').exists():
            (self.test_dir / 'concat.txt').unlink()

def main():
    """Run performance tests"""
    try:
        tester = PerformanceTester()
        
        # Run tests with progress reporting
        logger.info("Starting performance tests...")
        
        results = {
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
                'ffmpeg_version': subprocess.check_output([Config.get_ffmpeg_base_command()[0], '-version']).decode().split('\n')[0]
            },
            'test_results': {}
        }
        
        # Run performance tests
        performance_results = tester.run_performance_tests()
        results['test_results']['performance'] = performance_results
        
        # Run concat tests
        concat_results = tester.test_concat_performance()
        results['test_results']['concat'] = concat_results
        
        # Save combined results with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(tester.results_dir / f'performance_summary_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Performance tests completed. Results saved to performance_summary_{timestamp}.json")
        
    except Exception as e:
        logger.error(f"Test suite error: {e}")
    finally:
        if 'tester' in locals():
            tester.cleanup()

if __name__ == '__main__':
    main()
