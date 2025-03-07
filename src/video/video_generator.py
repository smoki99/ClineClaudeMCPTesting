import os
import logging
from src.config import Config
from src.video.clip_manager import ClipManager
from src.video.transition_handler import TransitionHandler
from src.video.ffmpeg_wrapper import FFmpegWrapper

logger = logging.getLogger(__name__)

class VideoGenerator:
    """
    Orchestrates the video generation process.
    """

    def __init__(self, clips_dir=None):
        """
        Initializes the VideoGenerator with the path to the video clips directory.
        If no path is provided, it uses the path defined in the Config class.
        Args:
            clips_dir (str, optional): Path to the video clips directory. Defaults to None.
        """
        self.clips_dir = clips_dir or str(Config.CLIPS_DIR)
        ffmpeg_path = str(Config.FFMPEG_PATH)
        self.clip_manager = ClipManager(self.clips_dir)
        self.transition_handler = TransitionHandler(ffmpeg_path)
        self.ffmpeg_wrapper = FFmpegWrapper(ffmpeg_path)

    def generate_video(self, target_duration, output_file, options=None):
        """
        Generates a video from a sequence of video clips, applying transitions between them, and adding background audio.
        Args:
            target_duration (int): The target duration of the video in seconds.
            output_file (str): Path to the output video file.
            options (dict, optional): Dictionary of encoding options. Defaults to None.
        Returns:
            bool: True if the video was generated successfully, False otherwise.
        """
        try:
            # Scan for video clips
            self.clip_manager.scan_clips()

            # Select video clips based on target duration
            selected_clips = self.clip_manager.select_clips(target_duration)

            if not selected_clips:
                logger.warning("No clips selected. Aborting video generation.")
                return False

            # Apply transitions between clips
            transitioned_clips = []
            if len(selected_clips) > 1:
                for i in range(len(selected_clips) - 1):
                    input_file1 = selected_clips[i]
                    input_file2 = selected_clips[i+1]
                    transitioned_file = str(Config.TEST_DIR / f"transitioned_{i}.mp4")
                    if self.transition_handler.apply_transition(input_file1, input_file2, transitioned_file):
                        transitioned_clips.append(transitioned_file)
                    else:
                        logger.error(f"Failed to apply transition between {input_file1} and {input_file2}")
                        return False
            else:
                transitioned_clips = selected_clips

            # Add background audio
            # TODO: Implement audio integration

            # Encode the final video
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if self.ffmpeg_wrapper.concat_video(transitioned_clips, output_file, options):
                return True
            else:
                logger.error("Failed to encode the final video.")
                return False
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return False
