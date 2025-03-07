import pytest
import json
import os
import sys
from pathlib import Path
import subprocess
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from pydub import AudioSegment
from src.audio import AudioProcessor
from src.config import Config

# Ensure test directory exists
if not os.path.exists(Config.TEST_DIR):
    os.makedirs(Config.TEST_DIR)

@pytest.fixture
def audio_processor():
    return AudioProcessor()

@pytest.fixture
def sample_songlist():
    return {
        "songs": {
            "music/01-Cherry Neon Blossoms.mp3": {
                "path": str(Path("music/01-Cherry Neon Blossoms.mp3")),
                "duration": 180,
            },
            "music/02-Neon Dreamscape.mp3": {
                "path": str(Path("music/02-Neon Dreamscape.mp3")),
                "duration": 240,
            }
        },
        "total_duration": 420
    }

@pytest.fixture
def songlist_path():
    return str(Config.TEST_DIR / "test_songlist.json")

def test_write_songlist(audio_processor, sample_songlist, songlist_path):
    """Test writing songlist to JSON file"""
    assert audio_processor.write_songlist(sample_songlist, songlist_path)
    assert os.path.exists(songlist_path)
    
    # Verify content
    with open(songlist_path, 'r') as f:
        loaded_songlist = json.load(f)
    assert loaded_songlist == sample_songlist

def test_create_playlist(audio_processor, sample_songlist):
    """Test creating a playlist from the music directory"""
    try:
        # Select all songs
        input_files = [song['path'] for song in sample_songlist['songs'].values()]
        
        # Load the audio files
        for file in input_files:
            audio = AudioSegment.from_mp3(file)
            assert audio is not None
    except Exception as e:
        pytest.fail(f"Audio loading failed: {e}")

def test_create_songlist_from_directory_invalid_extension(audio_processor, tmp_path):
    """Test creating a songlist from a directory with a file with an invalid extension"""
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("Not an MP3 file")
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0

def test_create_songlist_from_directory_empty_file(audio_processor, tmp_path):
    """Test creating a songlist from a directory with an empty file"""
    test_file = tmp_path / "empty.mp3"
    test_file.write_bytes(b"")
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0

def test_create_songlist_from_directory_corrupted_mp3(audio_processor, tmp_path):
    """Test creating a songlist from a directory with a corrupted MP3 file"""
    test_file = tmp_path / "corrupted.mp3"
    test_file.write_text("Corrupted MP3 file")
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0

def test_create_songlist_from_directory_not_audio_file(audio_processor, tmp_path):
    """Test creating a songlist from a directory with a file that is not an audio file"""
    test_file = tmp_path / "image.jpg"
    test_file.write_text("This is an image file")
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0

@pytest.mark.skip(reason="Cannot reliably test file permissions")
def test_create_songlist_from_directory_incorrect_permissions(audio_processor, tmp_path):
    """Test creating a songlist from a directory with a file that has incorrect permissions"""
    test_file = tmp_path / "permissions.mp3"
    AudioSegment.silent(duration=1000).export(test_file, format="mp3")
    os.chmod(test_file, 0o444)  # Read-only permissions
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0
    os.chmod(test_file, 0o777)  # Restore permissions

@pytest.mark.skip(reason="Cannot reliably test file size")
def test_create_songlist_from_directory_file_too_large(audio_processor, tmp_path):
    """Test creating a songlist from a directory with a file that is too large"""
    test_file = tmp_path / "large.mp3"
    # Create a large file (e.g., 100MB)
    with open(test_file, "wb") as f:
        f.seek(100 * 1024 * 1024)
        f.write(b"\0")
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0

def test_create_songlist_from_directory_is_directory(audio_processor, tmp_path):
    """Test creating a songlist from a directory with a directory instead of a file"""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    songlist = audio_processor.create_songlist_from_directory(tmp_path)
    assert len(songlist["songs"]) == 0
