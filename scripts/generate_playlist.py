import os
import random
from pathlib import Path
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from src.audio import AudioProcessor

def main():
    # Initialize AudioProcessor
    audio_processor = AudioProcessor(crossfade_duration=5000)  # 5 seconds in milliseconds
    
    # Set up directories
    music_dir = Path("music")
    output_dir = Path("test_files") / "test_audio"
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

    # Select random files from songlist
    target_duration = 3600  # 1 hour
    selected_files = []
    total_duration = 0
    available_songs = list(songlist['songs'].values())  # Convert to list for random.choice
    
    print("\nSelecting random tracks from songlist...")
    while total_duration < target_duration and available_songs:
        next_song = random.choice(available_songs)
        selected_files.append(next_song['path'])
        total_duration += next_song['duration']
        print(f"Added: {Path(next_song['path']).name} (Duration: {next_song['duration']:.1f}s)")
        available_songs.remove(next_song)

    print("\nApplying crossfades and creating playlist...")
    
    # Create playlist with crossfades
    output_file = str(output_dir / "one_hour_audio.mp3")
    if audio_processor.create_playlist(selected_files, output_file):
        print(f"\nSuccessfully created {output_file}")
        print(f"Total duration: {total_duration/3600:.1f} hours")
        print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        print("\nSelected tracks:")
        for i, file in enumerate(selected_files, 1):
            print(f"{i}. {file}")
        print(f"\nCrossfade duration: {audio_processor.crossfade_duration/1000:.1f} seconds")
        print("Using pydub audio processing with volume-adjusted crossfading")
    else:
        print("Failed to create audio file")

if __name__ == "__main__":
    main()
