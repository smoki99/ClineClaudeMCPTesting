## Problem
The file path `D:\dev\ClineClaudeMCPTesting\test_files\clips/girls1.mp4` is incorrect and should be `D:\dev\ClineClaudeMCPTesting\clips\girls1.mp4`. The project needs to be cross-platform compatible (Windows and Linux), so path separator differences (`\` and `/`) need to be handled.

## Plan
1.  **Identify where the incorrect file path is being used.** Use the `search_files` tool to search for the specific file path `D:\dev\ClineClaudeMCPTesting\test_files\clips/girls1.mp4` within the project.
2.  **Analyze the context of where the incorrect file path is being used.** Use the `read_file` tool to examine the contents of the files where the incorrect path is present to understand how the path is being used.
3.  **Implement a helper function (if necessary) to handle path separator differences.** If the file path is being constructed dynamically, create a helper function that can convert between Windows and Linux path separators. This function will ensure that the correct path separator is used based on the operating system.
4.  **Correct the file path.** Use the `replace_in_file` tool to replace the incorrect path with the correct path `D:\dev\ClineClaudeMCPTesting\clips\girls1.mp4`. If a helper function is implemented, use it to ensure the correct path separator is used.

## Cross-Platform Compatibility
The implementation will consider the need for cross-platform compatibility (Windows and Linux) and the potential need to handle different path separators (`\` and `/`).

## FFmpeg Wrapper Class

### Scope

The FFmpeg wrapper class will provide the following core functionalities:

*   **Encoding video:** Convert video files from one format to another.
*   **Concatenating video clips:** Join multiple video clips into a single video.
*   **Adding audio to video:** Add an audio track to a video file.
*   **Applying video filters:** Apply various video filters, such as scaling, cropping, and color correction.

### API

The FFmpeg wrapper class will expose the following methods:

*   `encode_video(input_file, output_file, options)`: Encodes a video file.
    *   `input_file`: Path to the input video file.
    *   `output_file`: Path to the output video file.
    *   `options`: Dictionary of encoding options (e.g., codec, bitrate, resolution).
*   `concat_video(input_files, output_file, options)`: Concatenates multiple video clips.
    *   `input_files`: List of paths to the input video files.
    *   `output_file`: Path to the output video file.
     *   `options`: Dictionary of concatenation options (e.g., transition effects).
*   `add_audio(input_file, audio_file, output_file, options)`: Adds an audio track to a video file.
    *   `input_file`: Path to the input video file.
    *   `audio_file`: Path to the audio file.
    *   `output_file`: Path to the output video file.
    *   `options`: Dictionary of audio adding options (e.g., volume, start time).
*   `apply_filter(input_file, output_file, filter_name, options)`: Applies a video filter to a video file.
    *   `input_file`: Path to the input video file.
    *   `output_file`: Path to the output video file.
    *   `filter_name`: Name of the filter to apply (e.g., scale, crop, color balance).
    *   `options`: Dictionary of filter options (e.g., width, height, x, y).

The `options` parameter in each method will be a dictionary that allows the user to specify various FFmpeg options for each operation.

Error Handling: The wrapper should include robust error handling, raising exceptions with informative messages when FFmpeg commands fail.

### Timeout Handling

The `FFmpegWrapper` class must include timeout checks to prevent long-running processes from looping indefinitely. The timeout value should be configurable via a parameter in the `__init__` method. The `_run_command` method should use the timeout value when running the FFmpeg process and raise a `TimeoutExpired` exception if the process exceeds the specified timeout.
