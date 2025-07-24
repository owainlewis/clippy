# Clippy

A Python tool for extracting and processing video clips to create engaging, social media-ready content.

**Now with FastAPI Web API support!** 🚀

## Features

### Core Features
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

### Web API Features
- **REST API**: FastAPI-based web API for programmatic access
- **File Upload**: Upload videos directly through the web interface
- **Background Processing**: Asynchronous task processing with status tracking
- **Interactive Documentation**: Auto-generated API docs with Swagger UI
- **Multiple Output Formats**: Support for various video and transcription formats
- **Task Management**: Track processing status and download results

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
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID

# Extract a 30-second random clip from a local file in square format
python clippy.py my_video.mp4 --duration 30 --format square

# Create a portrait mode clip with no text overlay
python clippy.py my_video.mp4 --format portrait --no-text

# Just download a video without processing it
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --download-only

# Download with a custom filename
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --download-only --output-filename="my_video.mp4"

# Transcribe a video to SRT format using Whisper
python clippy.py my_video.mp4 --transcribe

# Transcribe a video to plain text using Whisper with the medium model
python clippy.py my_video.mp4 --transcribe --transcribe-format txt --whisper-model medium

# Transcribe a YouTube video (will download first)
python clippy.py https://www.youtube.com/watch?v=VIDEO_ID --transcribe
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

# Run functional tests
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

## Web API Usage

Clippy now includes a FastAPI-based web API for programmatic access and integration with other applications.

### Starting the API Server

#### Development Mode
```bash
# Start the server with auto-reload
clippy-server --reload --host 0.0.0.0 --port 8000

# Or using the startup script
python start_server.py
```

#### Production Mode
```bash
# Start with multiple workers
clippy-server --host 0.0.0.0 --port 8000 --workers 4

# Using environment variables
export CLIPPY_HOST=0.0.0.0
export CLIPPY_PORT=8000
export CLIPPY_WORKERS=4
export CLIPPY_OUTPUT_DIR=/path/to/output
python start_server.py
```

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

### API Endpoints

The API provides several endpoints that match the functionality of the original CLI tool:

- **`POST /process`** - Create a complete viral clip (download → random clip → subtitles → text → crop)
- **`POST /extract-clip`** - Extract a specific time segment from a video
- **`POST /generate-random-clip`** - Generate a random clip from a video
- **`POST /transcribe`** - Transcribe video to SRT or text format
- **`POST /download`** - Download video from URL
- **`POST /add-subtitles`** - Add subtitles using Whisper
- **`POST /add-text-overlay`** - Add custom text overlay
- **`POST /crop-for-social`** - Crop video for social media formats
- **`POST /upload`** - Upload video files
- **`GET /tasks/{task_id}`** - Check processing status
- **`GET /download/{filename}`** - Download processed files

#### Upload Video
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_video.mp4"
```

#### Process Video (Create Viral Clip)
```bash
curl -X POST "http://localhost:8000/process" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "clip_duration": 15,
    "format": "portrait",
    "add_subs": true,
    "add_text": true
  }'
```

#### Extract Specific Clip
```bash
curl -X POST "http://localhost:8000/extract-clip" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "start_time": 30.0,
    "duration": 15.0
  }'
```

#### Generate Random Clip
```bash
curl -X POST "http://localhost:8000/generate-random-clip" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "clip_duration": 30
  }'
```

#### Add Subtitles Only
```bash
curl -X POST "http://localhost:8000/add-subtitles" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "model_size": "base"
  }'
```

#### Add Text Overlay Only
```bash
curl -X POST "http://localhost:8000/add-text-overlay" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "text": "Follow for more!",
    "position": "bottom"
  }'
```

#### Crop for Social Media
```bash
curl -X POST "http://localhost:8000/crop-for-social" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "format": "square"
  }'
```

#### Transcribe Video
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file_id_from_upload",
    "output_format": "srt",
    "whisper_model": "base"
  }'
```

#### Download Video from URL
```bash
curl -X POST "http://localhost:8000/download" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "output_filename": "my_video.mp4"
  }'
```

#### Check Task Status
```bash
curl -X GET "http://localhost:8000/tasks/{task_id}" \
  -H "accept: application/json"
```

#### Download Processed File
```bash
curl -X GET "http://localhost:8000/download/{filename}" \
  --output processed_video.mp4
```

### Python Client Example

```python
import requests
import time

# Upload a video
with open('my_video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
    file_id = response.json()['file_id']

# Process the video
response = requests.post(
    'http://localhost:8000/process',
    json={
        'source': file_id,
        'clip_duration': 30,
        'format': 'square',
        'add_subs': True,
        'add_text': True
    }
)
task_id = response.json()['task_id']

# Check status until complete
while True:
    response = requests.get(f'http://localhost:8000/tasks/{task_id}')
    status = response.json()

    if status['status'] == 'completed':
        # Download the result
        result_url = status['result_url']
        response = requests.get(f'http://localhost:8000{result_url}')
        with open('processed_clip.mp4', 'wb') as f:
            f.write(response.content)
        break
    elif status['status'] == 'failed':
        print(f"Processing failed: {status['error']}")
        break

    time.sleep(2)  # Wait 2 seconds before checking again
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