import os
from pathlib import Path
import json
from datetime import timedelta
from pydub import AudioSegment
import random

class AudioProcessor:
    def __init__(self, crossfade_duration=5000):  # 5 seconds in milliseconds
        self.crossfade_duration = crossfade_duration

    def create_songlist_from_directory(self, directory):
        """Create a songlist from all mp3 files in a directory."""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} not found")

        songs = {}
        total_duration = 0

        for file in directory.glob("*.mp3"):
            file_path = Path(file)
            try:
                # Check File Extension
                if file_path.suffix.lower() != ".mp3":
                    print(f"Skipping {file}: Invalid file extension")
                    continue

                # Check File Size
                if file_path.stat().st_size == 0:
                    print(f"Skipping {file}: File is empty")
                    continue

                # Check Audio Format
                audio = AudioSegment.from_mp3(str(file))
                duration = len(audio) / 1000  # Convert ms to seconds
                songs[str(file)] = {
                    "path": str(file),
                    "duration": duration
                }
                total_duration += duration
            except Exception as e:
                print(f"Error loading {file}: {e}")
                continue

        return {
            "songs": songs,
            "total_duration": total_duration
        }

    def write_songlist(self, songlist, output_file):
        """Write songlist to a JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(songlist, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing songlist: {e}")
            return False

    def write_youtube_timestamps(self, files, output_file, playlist_duration=None):
        """Write timestamps file for YouTube in format 'HH:MM:SS TrackName'."""
        try:
            current_time = 0  # in seconds
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write total duration if provided
                if playlist_duration:
                    duration_str = str(timedelta(seconds=int(playlist_duration)))
                    f.write(f"Total Duration: {duration_str}\n\n")
                
                for file_path in files:
                    # Convert current time to HH:MM:SS
                    time_str = str(timedelta(seconds=int(current_time)))
                    if time_str.startswith('0:'):  # Remove leading 0: for times less than 1 hour
                        time_str = time_str[2:]
                    
                    # Get track name without path and extension
                    track_name = Path(file_path).stem
                    # Remove any track numbers from the start (e.g., "01-" or "1.")
                    track_name = '-'.join(track_name.split('-')[1:]) if '-' in track_name else track_name
                    track_name = track_name.strip()
                    
                    # Write timestamp and track name
                    f.write(f"{time_str} {track_name}\n")
                    
                    # Add duration of current track minus crossfade for next timestamp
                    audio = AudioSegment.from_mp3(file_path)
                    current_time += len(audio) / 1000 - (self.crossfade_duration / 1000)
            return True
        except Exception as e:
            print(f"Error writing YouTube timestamps: {e}")
            return False

    def crossfade_tracks(self, tracks):
        """Crossfade a list of audio tracks."""
        if not tracks:
            return None

        # Load all audio files
        audio_segments = []
        for track in tracks:
            try:
                audio = AudioSegment.from_mp3(track)
                # Normalize volume
                audio = audio.normalize()
                audio_segments.append(audio)
            except Exception as e:
                print(f"Error loading {track}: {e}")
                continue

        if not audio_segments:
            return None

        # Crossfade all tracks
        result = audio_segments[0]
        for next_track in audio_segments[1:]:
            # Get the last crossfade_duration milliseconds of the current track
            fade_out_pos = len(result) - self.crossfade_duration
            fade_out = result[fade_out_pos:]
            
            # Get the first crossfade_duration milliseconds of the next track
            fade_in = next_track[:self.crossfade_duration]
            
            # Create crossfade by overlaying the fades with volume adjustment
            overlap = fade_out.overlay(
                fade_in,
                position=0,
                gain_during_overlay=-6  # Reduce volume during crossfade to prevent clipping
            )
            
            # Combine everything: main part + crossfade + next_track[self.crossfade_duration:]
            result = result[:fade_out_pos] + overlap + next_track[self.crossfade_duration:]

        return result

    def create_playlist(self, input_files, output_file, target_duration=3600):
        """Create a playlist from input files with crossfading, targeting specific duration."""
        try:
            # Filter to actual files and randomize
            available_files = [f for f in input_files if Path(f).exists()]
            if not available_files:
                print("No valid input files found")
                return False

            # Select files until we reach target duration
            total_duration = 0
            selected_files = []
            remaining_files = available_files.copy()
            
            while total_duration < target_duration and remaining_files:
                next_file = random.choice(remaining_files)
                remaining_files.remove(next_file)
                
                try:
                    audio = AudioSegment.from_mp3(next_file)
                    duration = len(audio) / 1000  # Convert to seconds
                    
                    # Add file if it doesn't exceed target duration by too much
                    if total_duration + duration <= target_duration * 1.1:  # Allow 10% overflow
                        selected_files.append(next_file)
                        total_duration += duration - (self.crossfade_duration / 1000)  # Account for crossfade
                except Exception as e:
                    print(f"Error loading {next_file}: {e}")
                    continue

            if not selected_files:
                print("No files selected for playlist")
                return False

            # Create the playlist with crossfades
            result = self.crossfade_tracks(selected_files)
            if result is None:
                return False

            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Export as MP3
            result.export(
                output_file,
                format="mp3",
                bitrate="192k",
                tags={"album": "Generated Playlist", "artist": "AudioProcessor"}
            )

            # Generate YouTube timestamps
            timestamps_file = str(output_path.with_suffix('.txt'))
            self.write_youtube_timestamps(selected_files, timestamps_file, total_duration)

            print(f"\nPlaylist created successfully:")
            print(f"Duration: {total_duration/60:.1f} minutes")
            print(f"Tracks: {len(selected_files)}")
            print(f"Audio file: {output_file}")
            print(f"Timestamps: {timestamps_file}")
            
            return True
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return False
