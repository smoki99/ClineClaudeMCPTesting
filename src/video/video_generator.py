import os
import logging
from pathlib import Path
from src.config import Config
from src.video.clip_manager import ClipManager
from src.video.transition_handler import TransitionHandler
from src.video.ffmpeg_wrapper import FFmpegWrapper

logger = logging.getLogger(__name__)

class VideoGenerator:
    """
    Orchestrates the video generation process.
    """
    BATCH_SIZE = 10  # Process 10 clips at a time

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
        self.temp_dir = Config.TEST_DIR

    def build_batch_filter_complex(self, clips_metadata, transition_duration=1.0):
        """
        Builds a filter complex string for a batch of clips.
        """
        if not clips_metadata:
            return "", []

        filter_parts = []
        cumulative_duration = 0

        # Scale all inputs first
        for i, clip in enumerate(clips_metadata):
            filter_parts.append(
                f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2[scaled{i}]"
            )

        # Chain the transitions
        last_output = "scaled0"
        for i in range(1, len(clips_metadata)):
            offset = cumulative_duration - transition_duration
            cumulative_duration += float(clips_metadata[i-1]["duration"])
            
            current = f"scaled{i}"
            output = f"v{i}" if i < len(clips_metadata) - 1 else "v"
            
            filter_parts.append(
                f"[{last_output}][{current}]xfade=transition=fade:duration={transition_duration}"
                f":offset={offset}[{output}]"
            )
            last_output = output

        input_files = [clip["path"] for clip in clips_metadata]
        return ";".join(filter_parts), input_files

    def process_batch(self, clips_metadata, output_file):
        """Process a batch of clips into a single video."""
        filter_complex, input_files = self.build_batch_filter_complex(clips_metadata)
        
        command = [self.ffmpeg_wrapper.ffmpeg_path]
        for input_file in input_files:
            command.extend(["-i", input_file])
            
        command.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-y",
            output_file
        ])

        return self.ffmpeg_wrapper._run_command(command)

    def generate_video(self, target_duration, output_file, options=None):
        """
        Generates a video from a sequence of video clips in batches.
        """
        try:
            self.clip_manager.scan_clips()
            clips_metadata = self.clip_manager.select_clips_with_metadata(target_duration)

            if not clips_metadata:
                logger.warning("No clips selected. Aborting video generation.")
                return False

            # Process clips in batches
            batch_files = []
            for i in range(0, len(clips_metadata), self.BATCH_SIZE):
                batch = clips_metadata[i:i + self.BATCH_SIZE]
                batch_output = str(self.temp_dir / f"batch_{i//self.BATCH_SIZE}.mp4")
                if self.process_batch(batch, batch_output):
                    batch_files.append(batch_output)
                else:
                    logger.error(f"Failed to process batch {i//self.BATCH_SIZE}")
                    return False

            # Create output directory if needed
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Concatenate all batches
            concat_options = {"c:v": "copy"}  # Just copy streams, no re-encoding needed
            if self.ffmpeg_wrapper.concat_video(batch_files, output_file, concat_options):
                # Clean up batch files
                for batch_file in batch_files:
                    try:
                        os.remove(batch_file)
                    except OSError:
                        pass
                return True
            else:
                logger.error("Failed to concatenate final video")
                return False

        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return False
