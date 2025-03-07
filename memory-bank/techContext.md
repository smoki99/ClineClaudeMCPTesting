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
    """
    A wrapper class for FFmpeg functionality with optimized encoding
    and resolution handling.
    """
    def __init__(self, ffmpeg_path=None, ffprobe_path=None, timeout=None):
        self.ffmpeg_path = ffmpeg_path or str(Config.FFMPEG_PATH)
        self.ffprobe_path = ffprobe_path or str(Config.FFPROBE_PATH)
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

    def get_video_dimensions(self, file_path):
        """Gets the dimensions of a video file using ffprobe"""
        try:
            command = [
                self.ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                file_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)
            return (int(data["streams"][0]["width"]), 
                   int(data["streams"][0]["height"]))
        except Exception as e:
            self.logger.error(f"Error getting video dimensions: {e}")
            return None
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
class TransitionHandler:
    """Handles video transitions and effects"""
    def __init__(self, ffmpeg_wrapper):
        self.ffmpeg = ffmpeg_wrapper
        self.transition_length = 2.0  # seconds
        self.resolution = (1920, 1080)  # target resolution
        
    def apply_transition(self, clip1, clip2, transition_type='fade'):
        """Applies transition between two clips"""
        # Get dimensions for both clips
        dim1 = self.ffmpeg.get_video_dimensions(clip1)
        dim2 = self.ffmpeg.get_video_dimensions(clip2)
        
        # Scale clips to target resolution
        scaled1 = self._scale_video(clip1, dim1)
        scaled2 = self._scale_video(clip2, dim2)
        
        # Apply transition effect
        if transition_type == 'fade':
            return self._apply_fade_transition(scaled1, scaled2)
        elif transition_type == 'dissolve':
            return self._apply_dissolve_transition(scaled1, scaled2)
        else:
            return self._apply_cut(scaled1, scaled2)
            
    def _scale_video(self, clip, dimensions):
        """Scales video to target resolution"""
        if dimensions == self.resolution:
            return clip
            
        options = {
            'input_file': clip,
            'output_file': f'temp_{os.path.basename(clip)}',
            'vf': f'scale={self.resolution[0]}:{self.resolution[1]}'
        }
        return self.ffmpeg.build_video_command(options)
            
    def _apply_fade_transition(self, clip1, clip2):
        """Creates a fade transition between clips"""
        options = {
            'input_file': clip1,
            'output_file': 'transition.mp4',
            'filter_complex': f'[0:v]fade=t=out:st={self.transition_length}:d=1[v1];' \
                            f'[1:v]fade=t=in:st=0:d=1[v2];' \
                            f'[v1][v2]concat=n=2:v=1:a=0'
        }
        return self.ffmpeg.build_video_command(options)

    def _apply_dissolve_transition(self, clip1, clip2):
        """Creates a dissolve/crossfade transition"""
        options = {
            'input_file': clip1,
            'input_file2': clip2,
            'output_file': 'transition.mp4',
            'filter_complex': f'[0:v][1:v]xfade=transition=fade:duration={self.transition_length}'
        }
        return self.ffmpeg.build_video_command(options)

class TextOverlay:
    """Handles text overlays on video"""
    def __init__(self, ffmpeg_wrapper):
        self.ffmpeg = ffmpeg_wrapper
        self.font = "Arial"
        self.font_size = 24
        self.color = "white"
        
    def add_text(self, video_file, text, position="bottom", duration=None):
        """Adds text overlay to video"""
        # Calculate text position
        if position == "bottom":
            y_pos = "(h-text_h-20)"
        elif position == "top":
            y_pos = "20"
        else:
            y_pos = "(h-text_h)/2"
            
        # Build drawtext filter
        drawtext = f"drawtext=text='{text}':fontfile={self.font}:" \
                  f"fontsize={self.font_size}:fontcolor={self.color}:" \
                  f"x=(w-text_w)/2:y={y_pos}"
                  
        if duration:
            drawtext += f":enable='between(t,0,{duration})'"
            
        options = {
            'input_file': video_file,
            'output_file': f'text_{os.path.basename(video_file)}',
            'vf': drawtext
        }
        return self.ffmpeg.build_video_command(options)

class ProgressMonitor:
    """Real-time FFmpeg progress tracking"""
    def __init__(self, total_duration):
        self.total_duration = total_duration
        self.start_time = time.time()
        self.current_time = 0
        self.estimated_total = 0
        
    def parse_progress(self, line):
        """Parse FFmpeg output for progress information"""
        patterns = {
            'time': r'time=(\d{2}:\d{2}:\d{2})',
            'frame': r'frame=\s*(\d+)',
            'fps': r'fps=\s*(\d+\.?\d*)',
            'size': r'size=\s*(\d+)kB',
            'bitrate': r'bitrate=\s*(\d+\.\d+)kbits/s'
        }
        
        result = {}
        for key, pattern in patterns.items():
            if match := re.search(pattern, line):
                result[key] = match.group(1)
                
        if 'time' in result:
            self._calculate_eta(result['time'])
        
        return result
        
    def _calculate_eta(self, time_str):
        """Calculate estimated time remaining"""
        h, m, s = map(int, time_str.split(':'))
        self.current_time = h * 3600 + m * 60 + s
        
        if self.current_time > 0:
            elapsed = time.time() - self.start_time
            self.estimated_total = (elapsed * self.total_duration) / self.current_time
            
        return self.estimated_total - elapsed if 'elapsed' in locals() else None

    def get_progress(self):
        """Get current progress as percentage"""
        if self.total_duration > 0:
            return (self.current_time / self.total_duration) * 100
        return 0
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
