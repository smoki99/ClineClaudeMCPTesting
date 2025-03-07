import os
from pathlib import Path
import sys
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from pydub import AudioSegment

def create_test_audio(output_path):
    """Create a 1-second silent audio file using pydub"""
    silent_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
    silent_audio.export(output_path, format="mp3")

def main():
    music_dir = Path("music")
    music_dir.mkdir(parents=True, exist_ok=True)
    
    create_test_audio(str(music_dir / "song1.mp3"))
    create_test_audio(str(music_dir / "song2.mp3"))

if __name__ == "__main__":
    main()
