import os
import random
from pathlib import Path
import subprocess
import json

# Get FFmpeg path from Config
def get_ffmpeg_path():
    config_file = Path("src/config.py")
    ffmpeg_path = Path("ffmpeg-7.1-full_build-shared/bin/ffmpeg.exe")
    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    else:
        raise FileNotFoundError("FFmpeg not found")

class AudioManager:
    def __init__(self, ffmpeg_path):
        """Initialize AudioManager with FFmpegWrapper instance."""
        self.ffmpeg_path = ffmpeg_path

    def read_songlist(self, songlist_path):
        """
        Read and validate songlist from JSON file.
        
        Args:
            songlist_path (str): Path to the songlist JSON file.
            
        Returns:
            dict: The songlist data.
            
        Raises:
            json.JSONDecodeError: If the file contains invalid JSON.
            FileNotFoundError: If the file doesn't exist.
        """
        with open(songlist_path, 'r') as f:
            return json.load(f)

    def write_songlist(self, songlist, output_path):
        """
        Write songlist to JSON file.
        
        Args:
            songlist (dict): The songlist data.
            output_path (str): Path where to save the JSON file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(songlist, f, indent=4)
            return True
        except Exception as e:
            print(f"Error writing songlist: {e}")
            return False

    def create_songlist_from_directory(self, music_dir):
        """
        Create a songlist from all MP3 files in a directory.
        
        Args:
            music_dir (str): Path to the music directory.
            
        Returns:
            dict: The songlist data.
        """
        music_path = Path(music_dir)
        if not music_path.exists():
            print(f"Directory not found: {music_dir}")
            return None

        songs = []
        total_duration = 0

        # Find all MP3 files
        for mp3_file in music_path.glob("**/*.mp3"):
            try:
                # Get metadata
                metadata = self.get_audio_metadata(str(mp3_file))
                if metadata:
                    songs.append(metadata)
                    total_duration += metadata["duration"]
            except Exception as e:
                print(f"Error processing {mp3_file}: {e}")

        return {
            "songs": songs,
            "total_duration": total_duration
        }

    def get_audio_metadata(self, file_path):
        """
        Get metadata for an audio file using FFmpeg.
        
        Args:
            file_path (str): Path to the audio file.
            
        Returns:
            dict: The metadata including duration, title, etc.
        """
        try:
            # Get duration and other metadata using FFmpeg
            result = subprocess.run([
                self.ffmpeg_path,
                "-i", file_path,
                "-f", "null", "-"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Initialize metadata
            metadata = {
                "path": str(Path(file_path)),
                "title": Path(file_path).stem,  # Default to filename
                "artist": "Unknown",
                "duration": 0
            }

            # Parse FFmpeg output
            for line in result.stderr.splitlines():
                if "Duration" in line:
                    # Extract duration
                    time_str = line.split("Duration: ")[1].split(",")[0]
                    h, m, s = map(float, time_str.split(":"))
                    metadata["duration"] = h * 3600 + m * 60 + s

                # Look for metadata tags
                if "title" in line.lower():
                    metadata["title"] = line.split(":", 1)[1].strip()
                if "artist" in line.lower():
                    metadata["artist"] = line.split(":", 1)[1].strip()

            return metadata

        except Exception as e:
            print(f"Error getting metadata for {file_path}: {e}")
            return None

    def concat_audio(self, input_files, output_file):
        """
        Concatenate multiple audio files into a single file.
        
        Args:
            input_files (list): List of paths to input audio files.
            output_file (str): Path to the output audio file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Create a temporary concat file next to the output file
        concat_file = str(Path(output_file).parent / "concat.txt")
        try:
            # Verify input files exist
            for file in input_files:
                if not os.path.exists(file):
                    raise FileNotFoundError(f"Audio file not found: {file}")

            # Create concat file with absolute paths
            with open(concat_file, "w", encoding='utf-8') as f:
                for file in input_files:
                    abs_path = Path(file).resolve()
                    f.write(f"file '{str(abs_path)}'\n")

            # Build FFmpeg command
            command = [
                self.ffmpeg_path,
                "-f", "concat",  # Use concat demuxer
                "-safe", "0",  # Allow unsafe file paths
                "-i", concat_file,  # Input concat file
                "-acodec", "copy",  # Copy audio codec
                "-y",  # Overwrite output
                output_file  # Output file
            ]

            # Execute command
            subprocess.run(command, check=True)
            return True

        except Exception as e:
            print(f"Error concatenating audio: {e}")
            return False
        finally:
            if os.path.exists(concat_file):
                os.remove(concat_file)

    def normalize_path(self, path):
        """
        Normalize file path to use forward slashes.
        
        Args:
            path (str): The file path to normalize.
            
        Returns:
            str: Normalized path using forward slashes.
        """
        # Convert to Path object and normalize
        p = Path(path)
        
        try:
            # Try to make path relative to current directory
            p = p.relative_to(Path.cwd())
        except ValueError:
            # If that fails, just use the path as is
            pass

        # Convert to string with forward slashes
        return str(p).replace(os.sep, '/')

def main():
    ffmpeg_path = get_ffmpeg_path()
    #audio_manager = AudioManager(ffmpeg_path)
    
    # Set up directories
    music_dir = Path("music")
    output_dir = Path("test_files") / "test_audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating songlist from music directory...")
    #try:
    #    songlist = audio_manager.create_songlist_from_directory(music_dir)
    #except FileNotFoundError as e:
    #    print(f"Error: {e}")
    #    return
    
    # Save the complete songlist
    #songlist_file = output_dir / "complete_songlist.json"
    #if audio_manager.write_songlist(songlist, songlist_file):
    #    print(f"\nSaved complete songlist to {songlist_file}")
    #    print(f"Total songs: {len(songlist['songs'])}")
    #    print(f"Total duration: {songlist['total_duration'] / 3600:.2f} hours")
    #else:
    #    print(f"Error: Could not write songlist to {songlist_file}")
    #    return

    # Select random files from songlist
    target_duration = 3600  # 1 hour
    selected_files = []
    total_duration = 0
    
    print("\nSelecting random tracks from music directory...")
    
    music_path = Path("music")
    mp3_files = list(music_path.glob("**/*.mp3"))
    
    def get_duration(file_path):
        """Get duration of an audio file using FFmpeg."""
        result = subprocess.run([
            ffmpeg_path,
            "-i", str(file_path),
            "-f", "null", "-"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Extract duration from FFmpeg output
        for line in result.stderr.splitlines():
            if "Duration" in line:
                time_str = line.split("Duration: ")[1].split(",")[0]
                h, m, s = map(float, time_str.split(":"))
                return float(h) * 3600 + float(m) * 60 + float(s)
        return 0
    
    while total_duration < target_duration and mp3_files:
        next_file = random.choice(mp3_files)
        duration = get_duration(next_file)
        if duration > 0:
            selected_files.append(str(next_file))
            total_duration += duration
            print(f"Added: {Path(next_file).name} (Duration: {duration:.1f}s)")
        mp3_files.remove(next_file)

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
                ffmpeg_path,
                "-f", "concat",  # Use concat demuxer
                "-safe", "0",  # Allow unsafe file paths
                "-i", concat_file,  # Input concat file
                "-acodec", "copy",  # Copy audio codec
                "-y",  # Overwrite output
                output_file  # Output file
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            return True
        except Exception as e:
            print(f"Error concatenating audio: {e}")
            return False
        finally:
            if os.path.exists(concat_file):
                os.remove(concat_file)

    # Concatenate the selected audio files
    print("\nConcatenating audio files...")
    output_file = str(output_dir / "one_hour_audio.mp3")
    if concat_audio(selected_files, output_file):
        print(f"\nSuccessfully created {output_file}")
        print(f"Total duration: {total_duration/3600:.1f} hours")
        print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        print("\nSelected tracks:")
        for i, file in enumerate(selected_files, 1):
            print(f"{i}. {file}")
    else:
        print("Failed to concatenate audio files")

if __name__ == "__main__":
    main()
