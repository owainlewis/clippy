# Viral Clip Generator

A Python tool for extracting and processing video clips to create engaging, social media-ready content.

## Features

- Extract specific segments from longer videos using timestamps
- Download videos from YouTube and other platforms
- Generate random clips if no time range is specified
- Add automatic subtitles (via optional speech recognition)
- Add text overlays like calls-to-action
- Format videos for various social media platforms (portrait, square, landscape)
- Command-line interface for easy use in scripts and automation workflows

## Installation

### Prerequisites

- Python 3.7+
- FFmpeg (for video processing)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/viral-clip-generator.git
   cd viral-clip-generator
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

Extract a clip from a video file or URL:

```bash
python viral_clip_generator.py video_source [options]
```

#### Options:

- `--time-range "START-END"`: Specific time range for the clip (e.g., "1:13-1:45")
- `--duration SECONDS`: Duration in seconds (used if no time-range specified)
- `--format {portrait,square,landscape}`: Target format for social media
- `--no-subs`: Disable subtitles
- `--no-text`: Disable text overlay
- `--output-dir DIRECTORY`: Directory to save output files

#### Examples:

```bash
# Extract from 1:13 to 1:45 from a YouTube video
python viral_clip_generator.py https://www.youtube.com/watch?v=VIDEO_ID --time-range "1:13-1:45"

# Extract a 30-second random clip from a local file in square format
python viral_clip_generator.py my_video.mp4 --duration 30 --format square

# Create a portrait mode clip with no text overlay
python viral_clip_generator.py my_video.mp4 --time-range "2:30-3:15" --format portrait --no-text
```

### Time Format

Time ranges can be specified in multiple formats:
- `MM:SS-MM:SS`: Minutes and seconds (e.g., "1:30-2:45")
- `H:MM:SS-H:MM:SS`: Hours, minutes, and seconds (e.g., "1:30:00-1:45:30")
- `S-S`: Raw seconds (e.g., "90-180")

### Python API

You can also use the tool programmatically:

```python
from viral_clip_generator import ViralClipGenerator

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