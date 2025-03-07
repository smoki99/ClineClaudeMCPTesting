from pathlib import Path
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
import os
import glob
import random
import logging
import argparse
import subprocess
from src.video.video_generator import VideoGenerator
from src.config import Config
from src.video.ffmpeg_wrapper import FFmpegWrapper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # 1. Command-Line Argument Parsing
    parser = argparse.ArgumentParser(description="Generate a 1-hour test video with transitions.")
    parser.add_argument("--clips-dir", default="clips", help="Source directory of input MP4 clips.")
    parser.add_argument("--output", default="output/test_video.mp4", help="Path for the final output video.")
    parser.add_argument("--duration", type=int, default=3600, help="Target duration in seconds (default: 3600 for 1 hour).")
    parser.add_argument("--audio", help="Path to a background audio file (optional).")
    args = parser.parse_args()

    # 2. Clip Acquisition
    logging.info(f"Searching for MP4 files in: {args.clips_dir}")
    mp4_files = glob.glob(os.path.join(args.clips_dir, "*.mp4"))
    if not mp4_files:
        logging.error("No MP4 files found in the clips directory. Exiting.")
        return

    logging.info(f"Found {len(mp4_files)} MP4 files.")

    # 3. Initialize VideoGenerator
    video_generator = VideoGenerator(clips_dir=args.clips_dir)

    # 4. Select Clips
    video_generator.clip_manager.scan_clips()
    selected_clips = video_generator.clip_manager.select_clips(args.duration)

    if not selected_clips:
        logging.error("Could not select enough clips to meet target duration. Exiting.")
        return

    logging.info(f"Selected {len(selected_clips)} clips for video generation.")

    # 5. Generate Video
    logging.info(f"Generating video with selected clips.")
    options = {"c:v": "libx264"}
    if video_generator.generate_video(args.duration, args.output, options):
        logging.info(f"Successfully generated test video: {args.output}")
    else:
        logging.error(f"Failed to generate test video.")

if __name__ == "__main__":
    main()
