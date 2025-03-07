# YouTube Video Generator - Test Suite

## Overview
This test suite validates core functionality for the YouTube video generator project, focusing on:
- FFmpeg command validation
- Performance metrics
- Text overlay system

## Prerequisites
- Anaconda or Miniconda (for Windows development)
- FFmpeg is provided in the project (ffmpeg-7.1-full_build-shared)
- Windows 10/11 for development

## Setup
1. Create and activate conda environment:
```bash
conda create -n videogen python=3.10
conda activate videogen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Project Structure:
```
project/
├── src/
│   ├── config.py        # Central configuration
│   ├── audio/
│   ├── video/
│   └── utils/
├── clips/               # Read-only input clips
├── music/              # Read-only input music
├── tests/              # Test scripts
├── output/             # Generated videos
└── temp/              # Temporary files
```

4. Configuration:
All paths and settings are managed in `src/config.py`:
- FFmpeg path: D:/dev/ClineClaudeMCPTesting/ffmpeg-7.1-full_build-shared/bin
- Input clips: D:/dev/ClineClaudeMCPTesting/clips
- Input music: D:/dev/ClineClaudeMCPTesting/music
- test_clip.mp4 (sample video clip, 10-15 seconds)
- test_clip1.mp4, test_clip2.mp4 (for concatenation tests)
- test_audio1.mp3, test_audio2.mp3 (for audio tests)

## Running Tests

### FFmpeg Command Tests
Tests basic FFmpeg operations:
```bash
python tests/test_ffmpeg_commands.py
```

Tests include:
- Audio concatenation with crossfade
- Video encoding with libx264
- Text overlay basics
- Concat protocol efficiency

### Performance Tests
Measures processing speed and resource usage:
```bash
python tests/test_performance.py
```

Tests include:
- Processing time for different durations
- Memory usage patterns
- CPU utilization
- Concat method comparison

### Overlay Tests
Tests text overlay system:
```bash
python tests/test_overlay.py
```

Tests include:
- Fade timing variations
- Font style configurations
- Track name transitions

## Test Results
- Results are saved in test_results/
- Each test generates JSON output with metrics
- Performance tests include resource usage graphs
- Overlay tests save sample outputs

## Project Organization
- Input directories (clips/, music/) are read-only
- Output files go to output/
- Temporary files use temp/
- Test files use test_files/

## Usage
1. Configure environment:
```python
from src.config import Config

# Setup creates necessary directories
Config.setup()

# Validate configuration
Config.validate()
```

2. Access paths:
```python
clips_dir = Config.CLIPS_DIR
music_dir = Config.MUSIC_DIR
ffmpeg_path = Config.FFMPEG_PATH
```

## Cleanup
Working directories are automatically managed. To manually clean:
```bash
rm -rf output/*
rm -rf temp/*
rm -rf test_files/*
```

## Notes
- All tests include logging for debugging
- Failed tests include error details in logs
- Performance tests may take several minutes
- Resource usage may be high during video processing

## Common Issues
1. FFmpeg not found:
   - Ensure FFmpeg is installed and in system PATH
   - Check with: ffmpeg -version

2. Font issues:
   - Test suite uses Arial font
   - Update font path in test_overlay.py if needed

3. Resource constraints:
   - Tests may require significant CPU/memory
   - Adjust test durations in test_performance.py if needed
