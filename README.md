# Clippy

A Python tool for extracting and processing video clips to create engaging, social media-ready content.

## Features

- Extract specific segments from longer videos using timestamps
- Download videos from YouTube and other supported platforms
- Generate random clips if no time range is specified
- Add automatic subtitles using OpenAI's Whisper speech recognition
- Transcribe videos to SRT or text format
- Add text overlays like calls-to-action
- Format videos for various social media platforms (portrait, square, landscape)
- Command-line interface for easy use in scripts and automation workflows
- Download-only option for saving videos without processing
- Easy conversion between video formats using Make
- Support for multiple video formats and quality options

## Installation

### Prerequisites

- Python 3.9+
- FFmpeg (for video processing)
- Make (optional, for using Makefile commands)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/owainlewis/clippy.git
   cd clippy
   ```

2. Install using uv (recommended):
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install the package with dependencies
   uv sync

   # Run clippy
   uv run clippy --help
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

Extract a clip from a video file or URL:

```bash
clippy video_source [options]
```

#### Options:

- `--duration SECONDS`: Duration in seconds for random clip generation
- `--format {portrait,square,landscape}`: Target format for social media
- `--no-subs`: Disable subtitles
- `--no-text`: Disable text overlay
- `--output-dir DIRECTORY`: Directory to save output files
- `--download-only`: Only download the video without creating clips
- `--output-filename FILENAME`: Custom filename for downloaded video (only used with --download-only)
- `--transcribe`: Transcribe the video using Whisper (creates SRT file by default)
- `--transcribe-format {srt,txt}`: Format for transcription output (default: srt)
- `--whisper-model {tiny,base,small,medium,large}`: Whisper model size (default: base)

#### Examples:

```bash
# Extract a 15-second random clip from a YouTube video
clippy https://www.youtube.com/watch?v=VIDEO_ID

# Extract a 30-second random clip from a local file in square format
clippy my_video.mp4 --duration 30 --format square

# Create a portrait mode clip with no text overlay
clippy my_video.mp4 --format portrait --no-text

# Just download a video without processing it
clippy https://www.youtube.com/watch?v=VIDEO_ID --download-only

# Download with a custom filename
clippy https://www.youtube.com/watch?v=VIDEO_ID --download-only --output-filename="my_video.mp4"

# Transcribe a video to SRT format using Whisper
clippy my_video.mp4 --transcribe

# Transcribe a video to plain text using Whisper with the medium model
clippy my_video.mp4 --transcribe --transcribe-format txt --whisper-model medium

# Transcribe a YouTube video (will download first)
clippy https://www.youtube.com/watch?v=VIDEO_ID --transcribe
```

### Using the Makefile (macOS)

For macOS users, a Makefile is provided for common operations:

```bash
# Clean the output directory
make clean

# Convert a downloaded video to MP4 format
make convert

# Download a video
make download URL=https://www.youtube.com/watch?v=VIDEO_ID

# All-in-one: clean, download, and convert
make video VIDEO_URL=https://www.youtube.com/watch?v=VIDEO_ID

# Run tests
make test
```

### Python API

You can also use the tool programmatically:

```python
from clippy import ViralClipGenerator

# Initialize the generator
generator = ViralClipGenerator(output_dir="output_clips")

# Create a viral clip
clip_path = generator.create_viral_clip(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    clip_duration=15,  # 15 seconds
    add_subs=True,
    add_text=True,
    format="portrait"
)
print(f"Clip created: {clip_path}")

# Process a local file with random clip selection
clip_path = generator.create_viral_clip(
    "path/to/local/video.mp4",
    clip_duration=30,  # 30 seconds
    format="square"
)

# Just download a video without processing
downloaded_path = generator.download_video("https://www.youtube.com/watch?v=VIDEO_ID")
print(f"Video downloaded to: {downloaded_path}")

# Transcribe a video using Whisper
transcript_path = generator.transcribe_video(
    "path/to/video.mp4",
    output_format="srt",  # or "txt"
    model_size="base"  # options: tiny, base, small, medium, large
)
print(f"Transcript saved to: {transcript_path}")
```

## Advanced Usage

### Custom Text Overlays

You can customize the text overlay:

```python
generator = ViralClipGenerator()
clip_path = generator.extract_clip("video.mp4", 60, duration=30)
result = generator.add_text_overlay(
    clip_path,
    "Follow @YourAccount for more!",
    position="bottom"  # Options: "top", "bottom", "center"
)
```

### Speech Recognition with Whisper

The subtitle functionality uses OpenAI's Whisper for speech recognition:

```python
generator = ViralClipGenerator()
video_with_subs = generator.add_subtitles(
    "video.mp4",
    model_size="base"  # Options: tiny, base, small, medium, large
)
```

## Requirements

- `ffmpeg`: Video processing
- `yt-dlp`: Video downloading
- `openai-whisper`: Speech recognition
- `torch`: Required for Whisper
- `pysrt`: SRT file handling
- `ffmpeg-python`: Python bindings for FFmpeg

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request