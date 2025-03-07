import pytest
import subprocess
from src.video.ffmpeg_wrapper import FFmpegWrapper
from src.config import Config
import os

# Ensure test_files directory exists
if not os.path.exists(Config.TEST_DIR):
    os.makedirs(Config.TEST_DIR)

# Create a dummy video file for testing
dummy_video_path = str(Config.TEST_DIR / "dummy_video.mp4")
if not os.path.exists(dummy_video_path):
    subprocess.run([
        str(Config.FFMPEG_PATH),
        "-f", "lavfi",
        "-i", "testsrc=duration=1:size=640x480:rate=30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-acodec", "aac",
        "-strict", "experimental",
        "-ac", "1",
        "-ar", "44100",
        dummy_video_path
    ], check=True, capture_output=True)

# Create a dummy audio file for testing
dummy_audio_path = str(Config.TEST_DIR / "dummy_audio.mp3")
if not os.path.exists(dummy_audio_path):
    subprocess.run([
        str(Config.FFMPEG_PATH),
        "-f", "lavfi",
        "-i", "sine=frequency=1000:duration=1",
        dummy_audio_path
    ], check=True, capture_output=True)

@pytest.fixture
def ffmpeg_wrapper():
    return FFmpegWrapper()

def test_encode_video(ffmpeg_wrapper):
    output_file = str(Config.TEST_DIR / "encoded_video.mp4")
    assert ffmpeg_wrapper.encode_video(dummy_video_path, output_file)
    assert os.path.exists(output_file)

def test_concat_video(ffmpeg_wrapper):
    output_file = str(Config.TEST_DIR / "concat_video.mp4")
    assert ffmpeg_wrapper.concat_video([dummy_video_path, dummy_video_path], output_file)
    assert os.path.exists(output_file)

def test_add_audio(ffmpeg_wrapper):
    output_file = str(Config.TEST_DIR / "audio_video.mp4")
    assert ffmpeg_wrapper.add_audio(dummy_video_path, dummy_audio_path, output_file)
    assert os.path.exists(output_file)

def test_apply_filter(ffmpeg_wrapper):
    output_file = str(Config.TEST_DIR / "filtered_video.mp4")
    assert ffmpeg_wrapper.apply_filter(dummy_video_path, output_file, "scale=320:240")
    assert os.path.exists(output_file)

def test_timeout():
    ffmpeg_wrapper = FFmpegWrapper(timeout=1)
    with pytest.raises(subprocess.TimeoutExpired):
        ffmpeg_wrapper.test_timeout_command(1)
