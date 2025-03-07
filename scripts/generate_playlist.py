import os
import random
from pathlib import Path
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from src.audio import AudioManager
from src.config import Config

def main():
    # Initialize AudioManager
    audio_manager = AudioManager()
    
    # Set up directories
    music_dir = Path("music")
    output_dir = Path("test_files") / "test_audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating songlist from music directory...")
    try:
        songlist = audio_manager.create_songlist_from_directory(music_dir)
        if not songlist or not songlist['songs']:
            print("No songs found in the music directory")
            return
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Save the complete songlist
    songlist_file = output_dir / "complete_songlist.json"
    if audio_manager.write_songlist(songlist, songlist_file):
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
    available_songs = songlist['songs'].copy()  # Create a copy to avoid modifying original
    
    print("\nSelecting random tracks from songlist...")
    while total_duration < target_duration and available_songs:
        next_song = random.choice(available_songs)
        selected_files.append(next_song['path'])
        total_duration += next_song['duration']
        print(f"Added: {Path(next_song['path']).name} (Duration: {next_song['duration']:.1f}s)")
        available_songs.remove(next_song)

    # Create a temporary directory for processed audio files
    temp_dir = output_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    try:
        # Process each audio file with crossfading
        processed_files = []
        crossfade_duration = 3  # seconds
        
        print("\nProcessing audio files for crossfading...")
        for i, input_file in enumerate(selected_files):
            # Add padding at the end of each file (except the last one)
            output_file = temp_dir / f"processed_{i}.mp3"
            if i < len(selected_files) - 1:
                # Add padding for crossfade
                filter_complex = f"apad=pad_dur={crossfade_duration}"
                command = [
                    audio_manager.ffmpeg.ffmpeg_path,
                    "-i", input_file,
                    "-af", filter_complex,
                    "-y",
                    str(output_file)
                ]
            else:
                # Last file doesn't need padding
                command = [
                    audio_manager.ffmpeg.ffmpeg_path,
                    "-i", input_file,
                    "-c", "copy",
                    "-y",
                    str(output_file)
                ]
            
            print(f"Processing file {i+1}/{len(selected_files)}")
            result = audio_manager.ffmpeg._run_command(command)
            if not result:
                print(f"Error processing file: {input_file}")
                return
            processed_files.append(str(output_file))

        # Create filter graph for crossfading
        print("\nApplying crossfades...")
        filter_complex = []
        
        # First file stays as is
        filter_complex.append(f"[0:a]aformat=sample_fmts=fltp[a0];")
        
        # Chain remaining files with crossfades
        for i in range(1, len(processed_files)):
            # Format current file
            filter_complex.append(f"[{i}:a]aformat=sample_fmts=fltp[a{i}];")
            
            # Apply crossfade between previous output and current file
            prev_out = f"a{i-1}" if i == 1 else f"cf{i-1}"
            curr_out = f"cf{i}"
            
            filter_complex.append(
                f"[{prev_out}][a{i}]acrossfade=d={crossfade_duration}:c1=tri:c2=tri[{curr_out}];")

        # Remove trailing semicolon
        filter_str = "".join(filter_complex).rstrip(";")
        
        # Build the final FFmpeg command
        output_file = str(output_dir / "one_hour_audio.mp3")
        inputs = []
        for file in processed_files:
            inputs.extend(["-i", file])
            
        command = [
            audio_manager.ffmpeg.ffmpeg_path,
            *inputs,
            "-filter_complex", filter_str,
            "-map", f"[cf{len(processed_files)-1}]",
            "-y",
            output_file
        ]

        print("\nConcatenating audio files with crossfades...")
        result = audio_manager.ffmpeg._run_command(command)
        
        if result and os.path.exists(output_file):
            print(f"\nSuccessfully created {output_file}")
            print(f"Total duration: {total_duration/3600:.1f} hours")
            print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
            print("\nSelected tracks:")
            for i, file in enumerate(selected_files, 1):
                print(f"{i}. {file}")
        else:
            print("Failed to create audio file")
            
    finally:
        # Clean up temporary files
        for file in processed_files:
            try:
                os.remove(file)
            except:
                pass
        try:
            temp_dir.rmdir()
        except:
            pass

if __name__ == "__main__":
    main()
