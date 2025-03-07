import subprocess
import logging
import os
from src.config import Config

logger = logging.getLogger(__name__)

class FFmpegWrapper:
    """
    A wrapper class for FFmpeg functionality.
    """

    def __init__(self, ffmpeg_path=None, ffprobe_path=None, timeout=None):
        """
        Initializes the FFmpegWrapper with the paths to the FFmpeg and FFprobe executables.
        If no paths are provided, it uses the paths defined in the Config class.
        Args:
            ffmpeg_path (str, optional): Path to the FFmpeg executable. Defaults to None.
            ffprobe_path (str, optional): Path to the FFprobe executable. Defaults to None.
            timeout (int, optional): Timeout in seconds for FFmpeg commands. Defaults to None.
        """
        self.ffmpeg_path = ffmpeg_path or str(Config.FFMPEG_PATH)
        self.ffprobe_path = ffprobe_path or str(Config.FFPROBE_PATH)
        self.timeout = timeout

    def _run_command(self, command):
        """
        Runs an FFmpeg command using subprocess.

        Args:
            command (list): A list of strings representing the FFmpeg command.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        try:
            logger.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            logger.info(result.stdout)
            if result.returncode != 0:
                logger.error(f"FFmpeg command failed with error: {result.stderr}")
                return None
            return result
        except FileNotFoundError:
            logger.error("FFmpeg executable not found. Please ensure FFmpeg is installed and the path is configured correctly.")
            return None
        except subprocess.TimeoutExpired as e:
            logger.error(f"FFmpeg command timed out after {self.timeout} seconds.")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None

    def encode_video(self, input_file, output_file, options=None):
        """
        Encodes a video file.

        Args:
            input_file (str): Path to the input video file.
            output_file (str): Path to the output video file.
            options (dict, optional): Dictionary of encoding options. Defaults to None.

        Returns:
            bool: True if the encoding was successful, False otherwise.
        """
        command = [self.ffmpeg_path]  # -y to overwrite output file
        
        # If input_file is a raw FFmpeg input (like "testsrc=duration=1..."), don't use -i
        if not os.path.exists(input_file):
            command.extend(["-f", "lavfi", "-i", input_file])
        else:
            command.extend(['-i', input_file])
            
        if options:
            for key, value in options.items():
                command.extend([f"-{key}", str(value)])
        command.extend(['-y', output_file]) # -y to overwrite output file
        return self._run_command(command)

    def concat_video(self, input_files, output_file, options=None):
        """
        Concatenates multiple video clips.

        Args:
            input_files (list): List of paths to the input video files.
            output_file (str): Path to the output video file.
            options (dict, optional): Dictionary of concatenation options. Defaults to None.

        Returns:
            bool: True if the concatenation was successful, False otherwise.
        """
        # Create a temporary concat file
        concat_file = "concat.txt"
        try:
            with open(concat_file, "w") as f:
                for file in input_files:
                    f.write(f"file '{file}'\n")

            command = [
                self.ffmpeg_path,
                "-f",
                "concat",
                "-safe",
                "0",  # Required for relative paths
                "-i",
                concat_file,
                "-c",
                "copy",  # Copy streams directly
                "-y", # Overwrite output file if it exists
                output_file,
            ]
            if options:
                for key, value in options.items():
                    command.extend([f"-{key}", str(value)])
            success = self._run_command(command)
        finally:
            # Clean up the temporary concat file
            import os
            if os.path.exists(concat_file):
                os.remove(concat_file)
        return success

    def add_audio(self, input_file, audio_file, output_file, options=None):
        """
        Adds an audio track to a video file.

        Args:
            input_file (str): Path to the input video file.
            audio_file (str): Path to the audio file.
            output_file (str): Path to the output video file.
            options (dict, optional): Dictionary of audio adding options. Defaults to None.

        Returns:
            bool: True if the audio adding was successful, False otherwise.
        """
        command = [self.ffmpeg_path, '-i', input_file, '-i', audio_file, '-c', 'copy', '-map', '0:v', '-map', '1:a', '-shortest', '-y']
        if options:
            for key, value in options.items():
                command.extend([f"-{key}", str(value)])
        command.append(output_file)
        return self._run_command(command)

    def apply_filter(self, input_file, output_file, filter_name, options=None):
        """
        Applies a video filter to a video file.

        Args:
            input_file (str): Path to the input video file.
            output_file (str): Path to the output video file.
            filter_name (str): Name of the filter to apply.
            options (dict, optional): Dictionary of filter options. Defaults to None.

        Returns:
            bool: True if the filter application was successful, False otherwise.
        """
        command = [self.ffmpeg_path, '-i', input_file, '-vf', filter_name, '-y']
        if options:
            for key, value in options.items():
                command.extend([f"-{key}", str(value)])
        command.append(output_file)
        return self._run_command(command)

    def test_timeout_command(self, timeout):
        """
        Test timeout with a simple sleep command.

        Args:
            timeout (int): Timeout in seconds.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        command = ['python', '-c', 'import time; time.sleep(10)']
        self.timeout = timeout
        return self._run_command(command)

    def extract_audio(self, input_file, output_file, options=None):
        """
        Extracts the audio track from a video file.

        Args:
            input_file (str): Path to the input video file.
            output_file (str): Path to the output audio file.
            options (dict, optional): Dictionary of extraction options. Defaults to None.

        Returns:
            bool: True if the audio extraction was successful, False otherwise.
        """
        command = [self.ffmpeg_path, '-i', input_file, '-vn', '-acodec', 'pcm_s16le', '-f', 'wav', '-y']
        if options:
            for key, value in options.items():
                command.extend([f"-{key}", str(value)])
        command.append(output_file)
        return self._run_command(command)

    def get_video_dimensions(self, file_path):
        """
        Gets the dimensions of a video file using ffprobe.

        Args:
            file_path (str): Path to the video file.

        Returns:
            tuple: A tuple containing (width, height) of the video, or None if an error occurs.
        """
        try:
            command = [
                self.ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                file_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)
            width = int(data["streams"][0]["width"])
            height = int(data["streams"][0]["height"])
            return width, height
        except Exception as e:
            logger.error(f"Error getting video dimensions: {e}")
            return None
