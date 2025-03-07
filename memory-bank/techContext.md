# Technical Context

Last Updated: 2025-03-07

## Purpose
This document outlines the technologies used, development setup, technical constraints, and dependencies.

## Technology Stack
### Core Technologies
- Python 3.x
- ffmpeg (provided version)
- Standard library components
  - os, sys for file operations
  - random for selection
  - logging for system logs

### File Formats
- Input Audio: MP3
- Input Video: MP4
- Output Video: MP4
- Intermediate Audio: WAV
- Text: UTF-8 (logs, tracklist)

## Development Environment
### Required Tools
- Python 3.x
- ffmpeg (latest stable)
- pytest for testing
- Virtual environment
- Git for version control

### Directory Structure
```
project/
├── src/
│   ├── audio/
│   ├── video/
│   └── utils/
├── tests/
├── clips/
├── music/
├── output/
└── logs/
```

## Build System
### Development Build
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m pytest
```

### Production Build
```bash
python setup.py build
python setup.py test
python setup.py install
```

## Dependencies
### Core Dependencies
- moviepy>=1.0.0 (video processing abstractions)
- python-ffmpeg>=1.0.0 (ffmpeg wrapper)
- pydub>=0.25.1 (audio processing)
- pillow>=8.0.0 (image processing)
- numpy>=1.19.0 (data handling)
- psutil>=5.8.0 (process management)
- ffmpeg-progress-yield>=0.2.0 (progress tracking)

### Development Dependencies
- pytest>=6.0.0
- pytest-cov>=2.0.0
- black>=21.0
- pylint>=2.0.0
- mypy>=0.900

## Technical Constraints
### System Requirements
- CPU: Multi-core recommended
- RAM: 4GB minimum, 8GB+ recommended
- Storage: SSD recommended for better performance
- Network: Not required for operation

### Limitations
- Single-threaded audio processing
- Memory usage scales with video length
- Temporary storage needs for processing

### FFmpeg Integration Architecture
#### Core Components

1. FFmpeg Wrapper
```python
class FFmpegWrapper:
    """Centralized FFmpeg operations with optimized encoding"""
    def __init__(self, timeout=None):
        self.process = None
        self.timeout = timeout
        self.logger = logging.getLogger('FFmpegWrapper')

    def build_audio_command(self, options):
        """Optimized audio processing command"""
        return [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', options['input_list'],
            '-c', 'copy',  # Stream copy for efficiency
            options['output_file']
        ]

    def build_video_command(self, options):
        """H.264 optimized video processing"""
        return [
            'ffmpeg',
            '-i', options['input_file'],
            '-c:v', 'libx264',
            '-preset', options.get('preset', 'medium'),  # Balanced preset
            '-crf', '23',  # High quality, reasonable size
            '-tune', 'film',  # Optimized for video content
            '-movflags', '+faststart',  # Web playback optimization
            '-profile:v', 'high',  # High profile for better quality
            '-level', '4.1',  # Widely compatible level
            options['output_file']
        ]
```

2. Audio Processing
```python
class AudioProcessor:
    """Audio processing logic separate from FFmpeg"""
    def __init__(self, music_dir, duration):
        self.music_dir = music_dir
        self.target_duration = duration
        self.tracks = []

    def prepare_sequence(self):
        """Prepare audio processing configuration"""
        self.tracks = self._scan_music_files()
        random.shuffle(self.tracks)
        
        return {
            'input_list': self._create_concat_list(),
            'output_file': 'final_audio.wav',
            'duration': self.target_duration
        }

    def _create_concat_list(self):
        """Create FFmpeg concat format file"""
        with open('audio_list.txt', 'w') as f:
            for track in self.tracks:
                f.write(f"file '{track}'\n")
        return 'audio_list.txt'
```

3. Video Processing
```python
class VideoProcessor:
    """Video processing logic separate from FFmpeg"""
    def __init__(self, clips_dir, duration):
        self.clips_dir = clips_dir
        self.target_duration = duration
        self.clips = []

    def prepare_sequence(self):
        """Prepare video processing configuration"""
        self.clips = self._scan_clip_files()
        random.shuffle(self.clips)
        
        return {
            'input_file': self._create_clip_sequence(),
            'output_file': 'final_video.mp4',
            'preset': 'p7',
            'overlay_text': True
        }

    def _create_clip_sequence(self):
        """Create clip sequence avoiding repetition"""
        sequence = []
        while sum(clip.duration for clip in sequence) < self.target_duration:
            next_clip = self._select_next_clip(sequence[-1] if sequence else None)
            sequence.append(next_clip)
        return sequence
```

#### Error Handling
```python
class FFmpegError(Exception):
    ERROR_PATTERNS = {
        'timeout': r'Operation timed out',
        'memory': r'Cannot allocate memory',
        'format': r'Invalid data found when processing input',
        'codec': r'Codec not found',
        'permission': r'Permission denied',
        'io': r'Input/output error'
    }

    def __init__(self, cmd, error_output):
        self.cmd = cmd
        self.error_output = error_output
        self.error_type = self._classify_error(error_output)
        super().__init__(f"FFmpeg error ({self.error_type}): {error_output}")
```

#### Progress Monitoring
```python
class ProgressMonitor:
    """Real-time FFmpeg progress tracking"""
    def __init__(self, total_duration):
        self.total_duration = total_duration
        self.start_time = time.time()
        
    def parse_progress(self, line):
        """Parse FFmpeg output for progress information"""
        patterns = {
            'time': r'time=(\d{2}:\d{2}:\d{2})',
            'frame': r'frame=\s*(\d+)',
            'fps': r'fps=\s*(\d+\.?\d*)',
            'size': r'size=\s*(\d+)kB'
        }
        
        result = {}
        for key, pattern in patterns.items():
            if match := re.search(pattern, line):
                result[key] = match.group(1)
                
        if 'time' in result:
            self._calculate_eta(result['time'])
        
        return result
```

## Configuration
### Environment Variables
```python
VIDEO_GENERATOR_ENV = {
    'OUTPUT_DIR': './output',
    'CLIP_DIR': './clips',
    'MUSIC_DIR': './music',
    'LOG_LEVEL': 'INFO',
    'TEST_DURATION': '300',  # 5 minutes for testing
    'TRANSITION_LENGTH': '2.0',
    'FONT_SIZE': '24',
    'TEMP_DIR': './temp'
}
```

## Deployment
### Local Deployment
1. Clone repository
2. Install dependencies
3. Configure directories
4. Run tests
5. Start processing

### Cloud Deployment
1. Package application
2. Upload to cloud storage
3. Configure cloud environment
4. Set up monitoring
5. Deploy service

## Monitoring
### Logging Strategy
- Use Python's logging module
- Log levels: DEBUG, INFO, WARNING, ERROR
- Rotate logs daily
- Include timestamps and context

### Metrics
- Processing time
- Memory usage
- File operations
- Error rates
- Success rates

## Performance Requirements
### Processing Targets
- Audio processing: <10min for 1 hour
- Video processing: <45min for 1 hour
- Memory usage: <4GB peak
- Storage: <20GB temporary

### Optimization Guidelines
- Optimize libx264 encoding settings
- Implement proper cleanup
- Monitor resource usage
- Cache frequent operations

## Security Requirements
### File Security
- Validate all input files
- Sanitize file names
- Clean up temporary files
- Secure file permissions

### Process Security
- Resource limits
- Input validation
- Error handling
- Secure defaults

## Integration Points
### External Tools
- ffmpeg interface
- File system operations
- Cloud storage (future)

### Internal APIs
- Audio processor
- Video processor
- Text overlay
- Logger interface

## Version Control
### Git Configuration
- Repository initialized with main branch
- .gitignore set up for Python and media files
- clips/ and music/ tracked but contents ignored
- FFmpeg binaries managed separately

### Branch Strategy
- main: Production-ready code
- develop: Integration branch
- feature/*: New features
- bugfix/*: Bug fixes
- test/*: Test additions/modifications
- docs/*: Documentation updates

### Commit Standards
- Present tense in messages
- 50 char summary line
- Reference issues when relevant
- Include breaking changes in body

### Binary Management
- Media files not tracked
- Use designated directories
- Clean working directories
- Test results ignored

## Notes
- Keep this document in sync with package.json or equivalent
- Update when changing development tools or processes
- Document breaking changes in dependencies
- Follow Git commit standards
