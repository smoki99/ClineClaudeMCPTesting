# Project Brief

Last Updated: 2025-03-07

## Purpose
This document serves as the foundation for the project, defining core requirements, goals, and scope. All other Memory Bank documents build upon the information established here.

## Core Requirements
- Python-based video generator for YouTube content
- Create 1-hour long continuous videos
- Process input from clips/ and music/ directories
- Use ffmpeg for high-quality video processing
- Implement test-driven development approach
- Support cloud deployment readiness

## Goals
- Generate professional-quality 1-hour YouTube videos
- Automate video creation process
- Ensure consistent audio-visual quality
- Maintain track attribution for music
- Support development and production environments

## Project Scope
### Audio Processing
- Generate 1-hour music track from mp3 files
- Prevent song repetition
- Implement crossfading between tracks
- Preserve original audio quality
- Generate tracklist with timestamps

### Video Processing
- Output 1920x1080 resolution videos
- Random clip selection (5-10s durations)
- Prevent consecutive clip repetition
- Smooth transitions between clips
- Text overlay for track names

## Success Metrics
- Successful generation of 1-hour videos
- Smooth transitions between audio tracks
- Smooth transitions between video clips
- Accurate track name display
- Complete tracklist generation
- Comprehensive test coverage
- Reliable logging system

## Key Stakeholders
- Development team
- Content creators
- YouTube audience
- Music track providers
- Video clip providers

## Critical Path
1. Audio processing implementation
   - Music file handling
   - Track sequencing
   - Crossfade implementation
2. Video processing implementation
   - Clip handling
   - Transition effects
   - Duration management
3. Text overlay system
   - Track name display
   - Fade effects
4. Testing and logging
   - Unit test implementation
   - Integration testing
   - Logging system
5. Production readiness
   - Cloud deployment preparation
   - Performance optimization

## Constraints
- Input Formats:
  - Music: MP3 files only
  - Video: MP4 files only
- Processing:
  - Must use provided ffmpeg
  - Must run without GUI
  - Console-based operation only
- Output:
  - 1920x1080 resolution
  - 1-hour duration (configurable for testing)
  - Arial font for text overlay

## Notes
- This is a living document that should be updated as project requirements evolve
- All major requirement changes must be documented here first
- Changes here may trigger updates to other Memory Bank documents
