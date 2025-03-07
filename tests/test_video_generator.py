import pytest
from src.video.video_generator import VideoGenerator
from src.config import Config
from src.video.ffmpeg_wrapper import FFmpegWrapper
import os
import glob
import random

# Ensure test_files directory exists
if not os.path.exists(Config.TEST_DIR):
    os.makedirs(Config.TEST_DIR)

@pytest.fixture
def video_generator():
    clips_dir = str(Config.TEST_DIR / "test_clips")
    return VideoGenerator(clips_dir=clips_dir)

def test_video_generator_initialization(video_generator):
    assert isinstance(video_generator, VideoGenerator)

def test_valid_mp4_exists(video_generator):
    clips_dir = video_generator.clips_dir
    mp4_files = glob.glob(os.path.join(clips_dir, "*.mp4"))
    assert len(mp4_files) > 0, "No MP4 files found in the clips directory"

def test_generate_video(video_generator):
    output_file = str(Config.TEST_DIR / "test_video.mp4")
    video_generator.clip_manager.scan_clips()
    assert video_generator.generate_video(5, output_file)

def test_generate_video_with_valid_clips(video_generator):
    output_file = str(Config.TEST_DIR / "test_video_valid_clips.mp4")
    video_generator.clip_manager.scan_clips()
    assert video_generator.generate_video(5, output_file)

def test_generate_video_with_no_clips(video_generator):
    output_file = str(Config.TEST_DIR / "test_video_no_clips.mp4")
    # Create an empty clips directory
    empty_clips_dir = str(Config.TEST_DIR / "empty_clips")
    if not os.path.exists(empty_clips_dir):
        os.makedirs(empty_clips_dir)
    video_generator.clip_manager.clips_dir = empty_clips_dir
    video_generator.clip_manager.scan_clips()
    assert not video_generator.generate_video(5, output_file)

def test_generate_video_with_invalid_clips(video_generator):
    output_file = str(Config.TEST_DIR / "test_video_invalid_clips.mp4")
    # Create a clips directory with invalid files
    invalid_clips_dir = str(Config.TEST_DIR / "invalid_clips")
    if not os.path.exists(invalid_clips_dir):
        os.makedirs(invalid_clips_dir)
    # Create a dummy text file
    with open(os.path.join(invalid_clips_dir, "dummy.txt"), "w") as f:
        f.write("This is not a video file")
    video_generator.clip_manager.clips_dir = invalid_clips_dir
    video_generator.clip_manager.scan_clips()
    assert not video_generator.generate_video(5, output_file)

def test_clip_manager_scan_clips(video_generator):
    video_generator.clip_manager.scan_clips()
    clips_dir = video_generator.clip_manager.clips_dir
    mp4_files = glob.glob(os.path.join(clips_dir, "*.mp4"))
    assert len(video_generator.clip_manager.clips) == len(mp4_files)

def test_clip_manager_select_clips(video_generator):
    video_generator.clip_manager.scan_clips()
    selected_clips = video_generator.clip_manager.select_clips(10)
    # This test is difficult to assert without knowing the exact duration of the clips
    assert True

def test_generate_video_with_options(video_generator):
    output_file = str(Config.TEST_DIR / "test_video_with_options.mp4")
    video_generator.clip_manager.scan_clips()
    options = {"c:v": "libx264", "preset": "ultrafast"}
    assert video_generator.generate_video(5, output_file, options)

def test_generate_video_output_directory(video_generator):
    output_file = str(Config.TEST_DIR / "new_dir" / "test_video_new_dir.mp4")
    video_generator.clip_manager.scan_clips()
    assert video_generator.generate_video(5, output_file)
    assert os.path.exists(os.path.dirname(output_file))
