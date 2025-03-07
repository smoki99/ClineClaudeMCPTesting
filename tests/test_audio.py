import pytest
import json
import os
from pathlib import Path
import subprocess
from src.audio import AudioManager
from src.config import Config

# Ensure test directory exists
if not os.path.exists(Config.TEST_DIR):
    os.makedirs(Config.TEST_DIR)

# Create valid test audio files
def create_test_audio(output_path):
    """Create a valid test MP3 file using FFmpeg"""
    subprocess.run([
        str(Config.FFMPEG_PATH),
        "-f", "lavfi",  # Use lavfi input format
        "-i", f"sine=frequency=440:duration=1",  # Generate 1 second sine wave
        "-acodec", "libmp3lame",  # Use MP3 encoder
        "-b:a", "192k",  # Set bitrate
        "-y",  # Overwrite output
        output_path
    ], check=True)

@pytest.fixture
def audio_manager():
    return AudioManager()

@pytest.fixture
def sample_songlist():
    return {
        "songs": [
            {
                "path": str(Path("music/song1.mp3")),
                "duration": 180,
                "title": "Test Song 1",
                "artist": "Test Artist 1"
            },
            {
                "path": str(Path("music/song2.mp3")),
                "duration": 240,
                "title": "Test Song 2",
                "artist": "Test Artist 2"
            }
        ],
        "total_duration": 420
    }

@pytest.fixture
def songlist_path():
    return str(Config.TEST_DIR / "test_songlist.json")

def test_write_songlist(audio_manager, sample_songlist, songlist_path):
    """Test writing songlist to JSON file"""
    assert audio_manager.write_songlist(sample_songlist, songlist_path)
    assert os.path.exists(songlist_path)
    
    # Verify content
    with open(songlist_path, 'r') as f:
        loaded_songlist = json.load(f)
    assert loaded_songlist == sample_songlist

def test_read_songlist(audio_manager, sample_songlist, songlist_path):
    """Test reading songlist from JSON file"""
    # Write test data
    with open(songlist_path, 'w') as f:
        json.dump(sample_songlist, f)
    
    # Test reading
    loaded_songlist = audio_manager.read_songlist(songlist_path)
    assert loaded_songlist == sample_songlist

def test_read_invalid_songlist(audio_manager, songlist_path):
    """Test reading invalid songlist file"""
    # Write invalid JSON
    with open(songlist_path, 'w') as f:
        f.write("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        audio_manager.read_songlist(songlist_path)

def test_concat_audio(audio_manager):
    """Test audio concatenation"""
    # Create test audio files
    input_files = [
        str(Config.TEST_DIR / "test1.mp3"),
        str(Config.TEST_DIR / "test2.mp3")
    ]
    output_file = str(Config.TEST_DIR / "concat_output.mp3")

    # Create valid MP3 files
    for input_file in input_files:
        create_test_audio(input_file)
    
    assert audio_manager.concat_audio(input_files, output_file)
    assert os.path.exists(output_file)

def test_path_handling(audio_manager):
    """Test platform-agnostic path handling"""
    # Convert Windows paths to Posix and back
    windows_path = "music\\song1.mp3"
    posix_path = "music/song1.mp3"
    
    # Test relative path normalization
    assert audio_manager.normalize_path(windows_path) == posix_path
    assert audio_manager.normalize_path(posix_path) == posix_path

def test_create_playlist(audio_manager):
    """Test creating a playlist from the music directory"""
    music_dir = "music"
    output_dir = Path("test_files") / "test_audio"
    output_file = str(output_dir / "test_playlist.mp3")
    
    # Create a songlist
    songlist = audio_manager.create_songlist_from_directory(music_dir)
    assert songlist is not None
    assert len(songlist['songs']) > 0
    
    # Select all songs
    input_files = [song['path'] for song in songlist['songs']]
    
    # Concatenate the audio files
    assert audio_manager.concat_audio(input_files, output_file)
    assert os.path.exists(output_file)
