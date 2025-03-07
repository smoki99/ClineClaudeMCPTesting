#!/usr/bin/env python3

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.config import Config

class OverlayTester:
    """Test text overlay and transition effects"""
    
    def __init__(self):
        # Initialize configuration
        Config.setup()
        if not Config.validate():
            raise RuntimeError("Configuration validation failed")
            
        self.test_dir = Config.TEST_DIR
        self.results_dir = Config.TEST_RESULTS_DIR
        
        # Get sample clip for testing
        self.test_clip = next(Config.CLIPS_DIR.glob('*.mp4'))
        if not self.test_clip:
            raise RuntimeError("No test clip found in clips directory")
    
    def test_fade_timing(self):
        """Test different fade timings for text overlay"""
        logger.info("Testing fade timing variations...")
        
        fade_configs = [
            {
                'name': 'quick_fade',
                'fade_in': 0.5,
                'hold': 2.0,
                'fade_out': 0.5
            },
            {
                'name': 'smooth_fade',
                'fade_in': 1.0,
                'hold': 3.0,
                'fade_out': 1.0
            },
            {
                'name': 'long_hold',
                'fade_in': 0.75,
                'hold': 5.0,
                'fade_out': 0.75
            }
        ]
        
        results = {}
        for config in fade_configs:
            logger.info(f"Testing {config['name']} configuration...")
            success = self._test_fade_config(config)
            results[config['name']] = {
                'config': config,
                'success': success
            }
        
        return results
    
    def _test_fade_config(self, config: Dict) -> bool:
        """Test a specific fade configuration"""
        fade_expression = (
            f"if(lt(t,{config['fade_in']}),"
            f"t/{config['fade_in']},"
            f"if(lt(t,{config['fade_in'] + config['hold']}),"
            f"1,"
            f"if(lt(t,{config['fade_in'] + config['hold'] + config['fade_out']}),"
            f"(1-(t-{config['fade_in'] + config['hold']})/{config['fade_out']}),"
            f"0)))"
        )
        
        cmd = Config.get_ffmpeg_base_command() + [
            '-i', str(self.test_clip),
            '-vf', f"drawtext=text='Test Track':fontcolor=white:fontsize=24:"
                  f"x=(w-text_w)/2:y=h-th-10:"
                  f"alpha='{fade_expression}'",
            str(self.test_dir / f"output_{config['name']}.mp4")
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Fade test error: {e}")
            return False

    def test_font_styles(self):
        """Test different font styles and positions"""
        logger.info("Testing font configurations...")
        
        font_configs = [
            {
                'name': 'standard',
                'font': 'Arial',
                'size': 24,
                'color': 'white',
                'position': '(w-text_w)/2:h-th-10'
            },
            {
                'name': 'large_bold',
                'font': 'Arial',
                'size': 36,
                'color': 'white@0.8',
                'position': '(w-text_w)/2:h-th-20'
            },
            {
                'name': 'outlined',
                'font': 'Arial',
                'size': 28,
                'color': 'white',
                'bordercolor': 'black',
                'borderwidth': 2,
                'position': '(w-text_w)/2:h-th-15'
            }
        ]
        
        results = {}
        for config in font_configs:
            logger.info(f"Testing {config['name']} font configuration...")
            success = self._test_font_config(config)
            results[config['name']] = {
                'config': config,
                'success': success
            }
        
        return results
    
    def _test_font_config(self, config: Dict) -> bool:
        """Test a specific font configuration"""
        filter_text = (
            f"drawtext=text='Test Track':"
            f"fontfile={config['font']}:"
            f"fontsize={config['size']}:"
            f"fontcolor={config['color']}:"
        )
        
        if 'bordercolor' in config:
            filter_text += f"bordercolor={config['bordercolor']}:borderw={config['borderwidth']}:"
        
        filter_text += f"x={config['position'].split(':')[0]}:y={config['position'].split(':')[1]}"
        
        cmd = Config.get_ffmpeg_base_command() + [
            '-i', str(self.test_clip),
            '-vf', filter_text,
            str(self.test_dir / f"output_{config['name']}.mp4")
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Font test error: {e}")
            return False

    def test_track_changes(self):
        """Test track name changes with transitions"""
        logger.info("Testing track name transitions...")
        
        tracks = [
            "First Track",
            "Second Track - Longer Name",
            "Track 3"
        ]
        
        filter_complex = []
        for i, track in enumerate(tracks):
            # Each track name appears for 5 seconds with 1 second crossfade
            duration = 5
            fade_in = i * (duration - 1)
            fade_out = fade_in + duration
            
            filter_complex.append(
                f"drawtext=text='{track}':fontcolor=white:fontsize=24:"
                f"x=(w-text_w)/2:y=h-th-10:"
                f"enable='between(t,{fade_in},{fade_out})':"
                f"alpha='if(lt(t-{fade_in},1),t-{fade_in},if(lt({fade_out}-t,1),{fade_out}-t,1))'"
            )
        
        cmd = [
            'ffmpeg',
            '-i', str(self.test_dir / 'test_clip.mp4'),
            '-vf', ','.join(filter_complex),
            str(self.test_dir / 'output_track_changes.mp4')
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Track change test error: {e}")
            return False

    def save_results(self, results: Dict):
        """Save test results to JSON file"""
        with open(self.results_dir / 'overlay_tests.json', 'w') as f:
            json.dump(results, f, indent=2)

    def cleanup(self):
        """Clean up test files"""
        logger.info("Cleaning up test files...")
        for file in self.test_dir.glob('output_*'):
            file.unlink()

def main():
    """Run overlay tests"""
    try:
        tester = OverlayTester()
        
        # Test configuration
        tests = [
            ('Fade Timing', tester.test_fade_timing),
            ('Font Styles', tester.test_font_styles),
            ('Track Changes', tester.test_track_changes)
        ]
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'clip_used': str(tester.test_clip),
            'tests': {}
        }
        
        # Run each test
        for name, test_func in tests:
            logger.info(f"Running {name} test...")
            try:
                test_results = test_func()
                results['tests'][name] = {
                    'status': 'success',
                    'results': test_results
                }
            except Exception as e:
                logger.error(f"{name} test error: {e}")
                results['tests'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Save results with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(tester.results_dir / f'overlay_tests_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Overlay tests completed. Results saved to overlay_tests_{timestamp}.json")
        
    except Exception as e:
        logger.error(f"Test suite error: {e}")
    finally:
        if 'tester' in locals():
            tester.cleanup()

if __name__ == '__main__':
    main()
