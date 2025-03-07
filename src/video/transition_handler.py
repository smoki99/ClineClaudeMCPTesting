import logging
from src.config import Config
from src.video.ffmpeg_wrapper import FFmpegWrapper

logger = logging.getLogger(__name__)

class TransitionHandler:
    """
    Handles transition effects between video clips.
    """

    def __init__(self, ffmpeg_path=None):
        """
        Initializes the TransitionHandler with the path to the FFmpeg executable.
        If no path is provided, it uses the path defined in the Config class.
        Args:
            ffmpeg_path (str, optional): Path to the FFmpeg executable. Defaults to None.
        """
        self.ffmpeg = FFmpegWrapper(ffmpeg_path=ffmpeg_path)

    def apply_transition(self, input_file1, input_file2, output_file, transition_type="fade", duration=1.0):
        """
        Applies a transition between two video clips using FFmpeg's xfade filter.
        Args:
            input_file1 (str): Path to the first video clip.
            input_file2 (str): Path to the second video clip.
            output_file (str): Path to the output video clip with the transition.
            transition_type (str, optional): The type of transition to apply (e.g., "fade", "wipe"). Defaults to "fade".
            duration (float, optional): The duration of the transition in seconds. Defaults to 1.0.
        Returns:
            bool: True if the transition was applied successfully, False otherwise.
        """
        try:
            # Get dimensions of both inputs using FFmpegWrapper
            dim1 = self.ffmpeg.get_video_dimensions(input_file1)
            dim2 = self.ffmpeg.get_video_dimensions(input_file2)
            
            if not dim1 or not dim2:
                logger.error("Failed to get video dimensions")
                return False

            w1, h1 = dim1
            w2, h2 = dim2
            logger.info(f"Input 1 dimensions: {w1}x{h1}")
            logger.info(f"Input 2 dimensions: {w2}x{h2}")

            # Only scale if needed
            if w1 != 1920 or h1 != 1080 or w2 != 1920 or h2 != 1080:
                filter_complex = (
                    "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v0];"
                    "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v1];"
                    f"[v0][v1]xfade=transition=fade:duration={duration}:offset=0"
                )
            else:
                filter_complex = f"xfade=transition=fade:duration={duration}:offset=0"

            # Use FFmpegWrapper to apply the filter
            options = {
                "filter_complex": filter_complex,
                "c:v": "libx264"
            }
            
            command = [
                self.ffmpeg.ffmpeg_path,
                "-i", input_file1,
                "-i", input_file2,
                "-filter_complex", filter_complex,
                "-y",
                output_file
            ]
            
            if self.ffmpeg._run_command(command):
                return True
            else:
                logger.error(f"FFmpeg command failed to apply transition between {input_file1} and {input_file2}")
                return False

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return False
