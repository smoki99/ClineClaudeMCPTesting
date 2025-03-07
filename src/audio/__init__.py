import os
from pathlib import Path
import json
from pydub import AudioSegment
from datetime import timedelta

class AudioProcessor:
    def __init__(self, crossfade_duration=15000):  # in ms
        self.crossfade_duration = crossfade_duration

    def create_songlist_from_directory(self, directory):
        """Create a songlist from all mp3 files in a directory."""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} not found")

        songs = {}
        total_duration = 0

        for file in directory.glob("*.mp3"):
            audio = AudioSegment.from_mp3(str(file))
            duration = len(audio) / 1000  # Convert ms to seconds
            songs[str(file)] = {
                "path": str(file),
                "duration": duration
            }
            total_duration += duration

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

    def write_youtube_timestamps(self, selected_files, output_file):
        """Write timestamps file for YouTube in format 'HH:MM:SS TrackName'."""
        try:
            current_time = 0  # in seconds
            with open(output_file, 'w', encoding='utf-8') as f:
                for file_path in selected_files:
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
            
            # Combine everything: main part + crossfade + rest of next track
            result = result[:fade_out_pos] + overlap + next_track[self.crossfade_duration:]

        return result

    def create_playlist(self, input_files, output_file):
        """Create a playlist from input files with crossfading."""
        try:
            # Create crossfaded mix
            result = self.crossfade_tracks(input_files)
            if result is None:
                return False

            # Export as MP3
            result.export(
                output_file,
                format="mp3",
                bitrate="192k",
                tags={"album": "Generated Playlist", "artist": "AudioProcessor"}
            )
            
            # Generate YouTube timestamps
            timestamps_file = str(Path(output_file).with_suffix('.txt'))
            self.write_youtube_timestamps(input_files, timestamps_file)
            
            return True
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return False
