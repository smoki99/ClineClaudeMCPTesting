import os
import glob
from pydub import AudioSegment
from importmonkey import add_path
add_path("D:/dev/ClineClaudeMCPTesting")
from src.audio import AudioProcessor
from src.video import VideoGenerator
from src.config import Config

def main():
    # Define directories and output filenames
    music_dir = str(Config.MUSIC_DIR)
    clips_dir = str(Config.CLIPS_DIR)
    output_audio = os.path.join(str(Config.OUTPUT_DIR), "one_hour_audio.mp3")
    output_video = os.path.join(str(Config.OUTPUT_DIR), "one_hour_video.mp4")
    final_output = os.path.join(str(Config.OUTPUT_DIR), "final_prototype.mp4")
    
    # Step 1: Generate the one-hour audio track.
    print("Generating audio sequence...")
    audio_processor = AudioProcessor()
    songlist = audio_processor.create_songlist_from_directory(music_dir)
    
    if not songlist or not songlist["songs"]:
        print("No audio files found or songlist creation failed.")
        return
    
    # Create a playlist of 1 hour
    audio_processor.create_playlist(list(songlist["songs"].keys()), output_audio, target_duration=3600)
    
    # Step 2: Create the video sequence.
    print("Generating video sequence...")
    video_generator = VideoGenerator()
    options = {"c:v": "libx264"}
    video_generator.generate_video(3600, output_video, options)
    
    # Step 3: Merge the audio and video.
    try:
        from src.video import ffmpeg_wrapper
        wrapper = ffmpeg_wrapper.FFmpegWrapper()
        print("Merging audio and video...")
        merge_result = wrapper.add_audio(output_video, output_audio, final_output)
        if merge_result is not None:
            print(f"Final prototype video with audio saved to {final_output}")
        else:
            print("Merging audio and video failed.")
    except ImportError:
        print("FFmpeg wrapper module not available. Skipping merge step.")
    
    print("Prototype generation completed.")

if __name__ == "__main__":
    Config.setup()
    main()
