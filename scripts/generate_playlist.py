import os
import random
from datetime import datetime
from pathlib import Path
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from src.audio import AudioProcessor

def main():
    # Initialize AudioProcessor with 5-second crossfades
    audio_processor = AudioProcessor(crossfade_duration=5000)
    
    # Set up directories
    music_dir = Path("music")
    output_dir = Path("output") / "playlists"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating songlist from music directory...")
    try:
        songlist = audio_processor.create_songlist_from_directory(music_dir)
        if not songlist or not songlist['songs']:
            print("No songs found in the music directory")
            return
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Save the complete songlist
    songlist_file = output_dir / "complete_songlist.json"
    if audio_processor.write_songlist(songlist, songlist_file):
        print(f"\nSaved complete songlist to {songlist_file}")
        print(f"Total songs: {len(songlist['songs'])}")
        print(f"Total duration: {songlist['total_duration'] / 3600:.2f} hours")
    else:
        print(f"Error: Could not write songlist to {songlist_file}")
        return

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = str(output_dir / f"one_hour_mix_{timestamp}.mp3")

    # Get all file paths
    input_files = [song['path'] for song in songlist['songs'].values()]
    
    print("\nGenerating 1-hour playlist...")
    if audio_processor.create_playlist(input_files, output_file):
        print("\nDone! Check the output files:")
        print(f"1. Audio file: {output_file}")
        print(f"2. Timestamps: {Path(output_file).with_suffix('.txt')}")
        print("\nTimestamp file contents:")
        try:
            with open(Path(output_file).with_suffix('.txt'), 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading timestamps: {e}")
    else:
        print("\nFailed to create playlist")

if __name__ == "__main__":
    main()
