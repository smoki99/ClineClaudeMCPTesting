import os
import logging
import json
from pathlib import Path
from src.config import Config
from src.video.ffmpeg_wrapper import FFmpegWrapper

logger = logging.getLogger(__name__)

class ClipManager:
    """
    Manages video clip scanning and selection.
    """

    def __init__(self, clips_dir=None):
        """
        Initializes the ClipManager with the path to the video clips directory.
        If no path is provided, it uses the path defined in the Config class.
        Args:
            clips_dir (str, optional): Path to the video clips directory. Defaults to None.
        """
        self.clips_dir = clips_dir or str(Config.CLIP_DIR)
        self.clips = []
        self.ffmpeg = FFmpegWrapper()

    def scan_clips(self):
        """
        Scans the video clips directory for video files.
        """
        self.clips = []
        for file in Path(self.clips_dir).glob("*"):
            if file.is_file() and file.suffix.lower() in ['.mp4', '.avi', '.mov']:
                self.clips.append(str(file))
        logger.info(f"Found {len(self.clips)} video clips in {self.clips_dir}")

    def get_clip_metadata(self, clip_path):
        """
        Reads clip metadata using FFprobe via FFmpegWrapper.
        Args:
            clip_path (str): Path to the video clip.
        Returns:
            dict: A dictionary containing the clip metadata.
        """
        try:
            command = [
                self.ffmpeg.ffprobe_path,
                '-v', 'error',
                '-show_entries',
                'format=duration,size:stream=codec_type,codec_name,width,height',
                '-of', 'json',
                clip_path
            ]
            result = self.ffmpeg._run_command(command)
            if not result:
                return None
                
            metadata = json.loads(result.stdout)
            return metadata
        except Exception as e:
            logger.error(f"Error getting clip metadata for {clip_path}: {e}")
            return None

    def get_clips_with_metadata(self):
        """
        Gets metadata for all available clips.
        Returns:
            list: List of dicts containing clip metadata ({path, duration}).
        """
        clips_metadata = []
        for clip in self.clips:
            metadata = self.get_clip_metadata(clip)
            if metadata and metadata['format'] and metadata['format']['duration']:
                clips_metadata.append({
                    'path': clip,
                    'duration': float(metadata['format']['duration'])
                })
            else:
                logger.warning(f"Skipping clip {clip} due to missing duration metadata")
        return clips_metadata

    def select_clips_with_metadata(self, target_duration):
        """
        Selects video clips with their metadata to meet the target duration.
        Args:
            target_duration (int): The target duration in seconds.
        Returns:
            list: List of dicts containing selected clip metadata ({path, duration}).
        """
        selected_clips = []
        current_duration = 0

        # Get all clips with metadata
        clips_metadata = self.get_clips_with_metadata()
        if not clips_metadata:
            return []

        # Randomize clip order for variety
        import random
        random.shuffle(clips_metadata)

        # Keep adding clips until we exceed target duration
        # Loop through clips multiple times if needed
        while current_duration < target_duration:
            for clip in clips_metadata:
                selected_clips.append(clip)
                current_duration += clip['duration']
                if current_duration >= target_duration:
                    break
            # If we've used all clips but still haven't reached target duration,
            # shuffle again for next loop
            if current_duration < target_duration:
                random.shuffle(clips_metadata)

        logger.info(f"Selected {len(selected_clips)} clips with a total duration of {current_duration} seconds")
        return selected_clips

    def select_clips(self, target_duration):
        """
        Legacy method that returns only clip paths. Use select_clips_with_metadata() for new code.
        Args:
            target_duration (int): The target duration in seconds.
        Returns:
            list: A list of selected video clip paths.
        """
        clips_with_metadata = self.select_clips_with_metadata(target_duration)
        return [clip['path'] for clip in clips_with_metadata]
