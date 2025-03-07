import os
import random
from pathlib import Path
import subprocess
import json

def get_ffmpeg_path():
    """Get FFmpeg executable path."""
    ffmpeg_path = Path("ffmpeg-7.1-full_build-shared/bin/ffmpeg.exe")
    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    else:
        raise FileNotFoundError("FFmpeg not found")

def get_duration(file_path):
    """Get duration of an audio file using FFmpeg."""
    result = subprocess.run([
        get_ffmpeg_path(),
        "-i", str(file_path),
        "-f", "null", "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Extract duration from FFmpeg output
    for line in result.stderr.splitlines():
        if "Duration" in line:
            time_str = line.split("Duration: ")[1].split(",")[0]
            h, m, s = time_str.split(':')
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 0

def concat_audio(input_files, output_file):
    """Concatenate audio files using FFmpeg."""
    # Create a temporary concat file
    concat_file = "concat.txt"
    try:
        # Create concat file with absolute paths
        with open(concat_file, "w", encoding='utf-8') as f:
            for file in input_files:
                abs_path = Path(file).resolve()
                f.write(f"file '{str(abs_path)}'\n")

        # Run FFmpeg concat command
        subprocess.run([
            get_ffmpeg_path(),
            "-f", "concat",  # Use concat demuxer
            "-safe", "0",  # Allow unsafe file paths
            "-i", concat_file,  # Input concat file
            "-acodec", "copy",  # Copy audio codec
            "-y",  # Overwrite output
            output_file  # Output file
        ], check=True)

        return True
    finally:
        if os.path.exists(concat_file):
            os.remove(concat_file)

def main():
    # Set target duration (1 hour in seconds)
    target_duration = 3600
    current_duration = 0
    
    # Get list of MP3 files from music directory
    music_dir = Path("music")
    if not music_dir.exists():
        print(f"Error: Music directory '{music_dir}' not found")
        return
    
    mp3_files = list(music_dir.glob("**/*.mp3"))
    if not mp3_files:
        print(f"Error: No MP3 files found in '{music_dir}'")
        return

    print(f"Found {len(mp3_files)} MP3 files in music directory")
    
    # Create output directory
    output_dir = Path("test_files") / "test_audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Select random files until we reach target duration
    selected_files = []
    total_duration = 0
    used_files = set()
    
    print("\nSelecting random tracks...")
    while total_duration < target_duration:
        available_files = [f for f in mp3_files if f not in used_files]
        if not available_files:
            # If we've used all files, reset the used_files set
            used_files.clear()
            available_files = mp3_files
        
        next_file = random.choice(available_files)
        used_files.add(next_file)
        duration = get_duration(next_file)
        
        if duration > 0:
            selected_files.append(next_file)
            total_duration += duration
            print(f"Added: {next_file.name} (Duration: {duration:.1f}s)")

    # Concatenate all segments
    print("\nConcatenating audio files...")
    output_file = str(output_dir / "one_hour_audio.mp3")
    if concat_audio(selected_files, output_file):
        print(f"\nSuccessfully created {output_file}")
        print(f"Total duration: {total_duration/3600:.1f} hours")
        print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        print("\nSelected tracks:")
        for i, file in enumerate(selected_files, 1):
            print(f"{i}. {file.name}")
    else:
        print("Failed to concatenate audio files")

if __name__ == "__main__":
    main()
