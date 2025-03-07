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

    def select_clips(self, target_duration):
         """
         Selects video clips based on a target duration.
         Args:
             target_duration (int): The target duration in seconds.
         Returns:
             list: A list of selected video clips.
         """
         selected_clips = []
         current_duration = 0
         import json
         # Load clip metadata and store it
         clip_metadata = []
         for clip in self.clips:
             metadata = self.get_clip_metadata(clip)
             if metadata and metadata['format'] and metadata['format']['duration']:
                 clip_metadata.append({
                     'path': clip,
                     'duration': float(metadata['format']['duration'])
                 })
             else:
                 logger.warning(f"Skipping clip {clip} due to missing duration metadata")

         # Sort clips by duration (shortest first)
         clip_metadata.sort(key=lambda x: x['duration'])

         # Select clips to meet target duration
         for clip in clip_metadata:
             if current_duration + clip['duration'] <= target_duration:
                 selected_clips.append(clip['path'])
                 current_duration += clip['duration']
             else:
                 break

         logger.info(f"Selected {len(selected_clips)} clips with a total duration of {current_duration} seconds")
         return selected_clips
