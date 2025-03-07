from pathlib import Path
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from src.audio import AudioProcessor

def main():
    music_dir = Path("music")
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize AudioProcessor
    audio_processor = AudioProcessor()

    # Create playlist
    input_files = [str(f) for f in music_dir.glob("*.mp3")]
    output_file = str(output_dir / "test_playlist.mp3")
    target_duration = 3600  # 1 hour in seconds

    if audio_processor.create_playlist(input_files, output_file, target_duration):
        print("Test playlist created successfully!")
    else:
        print("Failed to create test playlist.")

if __name__ == "__main__":
    main()
