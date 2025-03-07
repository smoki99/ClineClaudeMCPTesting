import os
from pathlib import Path
import json
from pydub import AudioSegment

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
            return True
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return False
