# YouTube Video Generator - Test Suite

A sample video generator project created with AI assistance:
- GitHub Copilot
- Claude-3.5-sonnet (Anthropic)
- Cline

## Overview
This test suite validates core functionality for the YouTube video generator project, focusing on:
- FFmpeg command validation
- Performance metrics
- Text overlay system

## Author
Christian Mueller (christian.mueller@vr-worlds.de)
Project Repository: [ClineClaudeMCPTesting](https://github.com/smoki99/ClineClaudeMCPTesting)

## Prerequisites

### System Requirements
- Windows 10/11 (development platform)
- 8GB RAM minimum (16GB recommended)
- SSD storage recommended
- Multi-core CPU recommended

### Required Software
1. Anaconda or Miniconda
   - Download from: https://docs.conda.io/en/latest/miniconda.html
   - Add to PATH during installation

2. Git
   - Download from: https://git-scm.com/download/win
   - Required for version control

3. FFmpeg (provided)
   - Located in ffmpeg-7.1-full_build-shared/
   - No manual installation needed

### Optional Tools
- VSCode (recommended IDE)
- SourceTree (Git GUI client)
- FFmpeg GUI for testing

## Setup

### 1. Environment Setup

#### Option A: Using Conda Environment File (Recommended)
```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate videogen

# Verify installation
conda list
python --version
```

#### Option B: Manual Setup
```bash
# Create base environment
conda create -n videogen python=3.10

# Activate environment
conda activate videogen

# Install core dependencies
conda install -c conda-forge ffmpeg=7.1
conda install numpy pillow pytest jupyter

# Install remaining packages
pip install -r requirements.txt
```

### 2. Development Setup
```bash
# Install in development mode
pip install -e .[dev]

# Setup pre-commit hooks
pre-commit install

# Configure git
git config --local core.autocrlf true

# Run initial checks
pre-commit run --all-files
```

### 3. Verify Installation
```bash
# Check FFmpeg
ffmpeg -version

# Check Python packages
python -c "import moviepy; print(f'moviepy: {moviepy.__version__}')"
python -c "import pydub; print(f'pydub: {pydub.__version__}')"
python -c "import numpy; print(f'numpy: {numpy.__version__}')"

# Run tests
pytest -v
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

## Version Control

### Repository Setup
The project uses Git for version control. Initial setup:

```bash
# Clone the repository
git clone [repository-url]
cd video-generator

# Configure Git (if not already done)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Development Workflow

1. Create feature branch:
```bash
git checkout -b feature/new-feature
```

2. Make changes and commit:
```bash
git add .
git commit -m "Description of changes"
```

3. Push changes:
```bash
git push origin feature/new-feature
```

### Branch Naming Convention
- feature/* - For new features
- bugfix/* - For bug fixes
- test/* - For test additions/modifications
- docs/* - For documentation updates

### Commit Message Guidelines
- Use present tense ("Add feature" not "Added feature")
- First line is a summary (50 chars or less)
- Optionally followed by blank line and detailed description
- Reference issues and pull requests when relevant

### File Management
- Media files (clips/, music/) are not tracked in Git
- FFmpeg binaries are managed separately
- Output and temporary files are ignored
- Test results are not tracked

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

4. Git-related:
   - Large files should not be committed
   - Use .gitignore for project-specific exclusions
   - Keep media files in designated directories
