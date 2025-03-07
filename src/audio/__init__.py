import json
import os
import subprocess
from pathlib import Path
from src.video.ffmpeg_wrapper import FFmpegWrapper

class AudioManager:
    def __init__(self):
        """Initialize AudioManager with FFmpegWrapper instance."""
        self.ffmpeg = FFmpegWrapper()

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
            songlist = json.load(f)
            self._validate_songlist(songlist)
            return songlist

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
            self._validate_songlist(songlist)
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
                self.ffmpeg.ffmpeg_path,
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
                self.ffmpeg.ffmpeg_path,
                "-f", "concat",  # Use concat demuxer
                "-safe", "0",  # Allow unsafe file paths
                "-i", concat_file,  # Input concat file
                "-acodec", "copy",  # Copy audio codec
                "-y",  # Overwrite output
                output_file  # Output file
            ]

            # Execute command
            result = self.ffmpeg._run_command(command)
            return result and os.path.exists(output_file)

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

    def _validate_songlist(self, songlist):
        """
        Validate songlist format.
        
        Args:
            songlist (dict): The songlist to validate.
            
        Raises:
            ValueError: If the songlist is invalid.
        """
        if not isinstance(songlist, dict):
            raise ValueError("Songlist must be a dictionary")
        
        if "songs" not in songlist:
            raise ValueError("Songlist must contain 'songs' key")
        
        if not isinstance(songlist["songs"], list):
            raise ValueError("Songs must be a list")
        
        for song in songlist["songs"]:
            if not isinstance(song, dict):
                raise ValueError("Each song must be a dictionary")
            
            required_keys = ["path", "duration", "title"]
            for key in required_keys:
                if key not in song:
                    raise ValueError(f"Song missing required key: {key}")
