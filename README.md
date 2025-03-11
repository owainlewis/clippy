# Clippy

A Python tool for extracting and processing video clips to create engaging, social media-ready content.

## Features

- Extract specific segments from longer videos using timestamps
- Download videos from YouTube and other platforms
- Generate random clips if no time range is specified
- Add automatic subtitles (via optional speech recognition)
- Add text overlays like calls-to-action
- Format videos for various social media platforms (portrait, square, landscape)
- Command-line interface for easy use in scripts and automation workflows
- Download-only option for saving videos without processing
- Easy conversion between video formats using Make

## Installation

### Prerequisites

- Python 3.7+
- FFmpeg (for video processing)
- Make (for using the Makefile functionality)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/owainlewis/clippy.git
   cd clippy
   ```

2. Create a virtual environment and install dependencies:

   #### Using pip (traditional method):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   #### Using uv (faster alternative):
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

   #### Using the Makefile (recommended):
   ```bash
   # This will set up everything and create an activation script
   make setup
   
   # Then activate the environment in your current shell
   source ./activate_env.sh
   ```

## Usage

### Command Line Interface

Extract a clip from a video file or URL:

```bash
python clippy.py video_source [options]
```

#### Options:

- `--time-range "START-END"`: Specific time range for the clip (e.g., "1:13-1:45")
- `--duration SECONDS`: Duration in seconds (used if no time-range specified)
- `--format {portrait,square,landscape}`: Target format for social media
- `--no-subs`: Disable subtitles
- `--no-text`: Disable text overlay
- `--output-dir DIRECTORY`: Directory to save output files
- `--download-only`: Only download the video without creating clips
- `--output-filename FILENAME`: Custom filename for downloaded video (only used with --download-only)

#### Examples:

```bash
# Extract from 1:13 to 1:45 from a YouTube video
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --time-range "1:13-1:45"

# Extract a 30-second random clip from a local file in square format
python clippy.py my_video.mp4 --duration 30 --format square

# Create a portrait mode clip with no text overlay
python clippy.py my_video.mp4 --time-range "2:30-3:15" --format portrait --no-text

# Just download a video without processing it
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --download-only

# Download with a custom filename
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --download-only --output-filename="my_video.mp4"
```

### Using the Makefile (macOS)

For macOS users, a Makefile is provided for common operations:

```bash
# Clean the output directory
make clean

# Convert a downloaded video to MP4 format
make convert

# For help with Makefile commands
make help
```

#### Typical Workflow with Makefile:

1. Download a video: 
   ```bash
   python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --download-only
   ```

2. Convert to MP4 format:
   ```bash
   make convert
   ```

### Time Format

Time ranges can be specified in multiple formats:
- `MM:SS-MM:SS`: Minutes and seconds (e.g., "1:30-2:45")
- `H:MM:SS-H:MM:SS`: Hours, minutes, and seconds (e.g., "1:30:00-1:45:30")
- `S-S`: Raw seconds (e.g., "90-180")

### Python API

You can also use the tool programmatically:

```python
from clippy import ViralClipGenerator

# Initialize the generator
generator = ViralClipGenerator(output_dir="output_clips")

# Create a clip with specific time range
clip_path = generator.create_viral_clip(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    time_range="1:13-1:45",
    add_subs=True,
    add_text=True,
    format="portrait"
)
print(f"Clip created: {clip_path}")

# Process a local file with random clip selection
clip_path = generator.create_viral_clip(
    "path/to/local/video.mp4",
    clip_duration=15,  # 15 seconds
    format="square"
)

# Just download a video without processing
downloaded_path = generator.download_video("https://www.youtube.com/watch?v=VIDEO_ID")
print(f"Video downloaded to: {downloaded_path}")
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

### Speech Recognition for Subtitles

The subtitle functionality currently provides a framework that you can extend with your preferred speech recognition library:

- [Whisper](https://github.com/openai/whisper): OpenAI's speech recognition system
- [Vosk](https://github.com/alphacep/vosk-api): Offline speech recognition
- [SpeechRecognition](https://github.com/Uberi/speech_recognition): Python library for speech recognition

To implement, modify the `add_subtitles()` method in the `ViralClipGenerator` class.

## Requirements

- `ffmpeg`: Video processing
- `yt-dlp`: Video downloading
- `pandas` (optional): For metadata processing
- Speech recognition library of your choice (for subtitle functionality)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request