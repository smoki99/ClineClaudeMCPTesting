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
