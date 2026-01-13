import os
import subprocess
import random
import shutil
from datetime import timedelta
from typing import Optional, Dict, Any

import yt_dlp

# Constants
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_CLIP_DURATION = 15
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_TEXT_OVERLAY = "Follow for more content like this!"
DEFAULT_TEXT_POSITION = "bottom"

# Whisper model sizes
WHISPER_MODELS = ("tiny", "base", "small", "medium", "large")

# Social media format crop filters
FORMAT_CROP_FILTERS = {
    "portrait": "crop=ih*9/16:ih:iw/2-ih*9/32:0",  # 9:16 ratio (centered)
    "square": "crop=ih:ih:iw/2-ih/2:0",  # 1:1 ratio (centered)
    "landscape": "crop=iw:iw*9/16:0:ih/2-iw*9/32",  # 16:9 ratio (centered)
}

# Text position coordinates for overlay
TEXT_POSITIONS = {
    "top": "x=(w-text_w)/2:y=h*0.1",
    "center": "x=(w-text_w)/2:y=(h-text_h)/2",
    "bottom": "x=(w-text_w)/2:y=h*0.9",
}


class FFmpegNotFoundError(Exception):
    """Raised when ffmpeg or ffprobe is not found on the system."""
    pass


class VideoProcessingError(Exception):
    """Raised when video processing fails."""
    pass


def _check_ffmpeg_installed() -> None:
    """Check if ffmpeg and ffprobe are installed.

    Raises:
        FFmpegNotFoundError: If ffmpeg or ffprobe is not found.
    """
    if not shutil.which("ffmpeg"):
        raise FFmpegNotFoundError(
            "ffmpeg not found. Please install ffmpeg: "
            "brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
        )
    if not shutil.which("ffprobe"):
        raise FFmpegNotFoundError(
            "ffprobe not found. Please install ffmpeg: "
            "brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
        )


def _run_ffmpeg_command(cmd: list, operation: str) -> subprocess.CompletedProcess:
    """Run an ffmpeg command with proper error handling.

    Args:
        cmd: Command to run as a list of arguments.
        operation: Description of the operation for error messages.

    Returns:
        CompletedProcess instance.

    Raises:
        VideoProcessingError: If the command fails.
    """
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = result.stderr.strip() if result.stderr else "Unknown error"
        raise VideoProcessingError(f"Failed to {operation}: {error_msg}")
    return result


def _timedelta_to_srt_time(td: timedelta) -> Dict[str, int]:
    """Convert a timedelta to SRT time components.

    Uses total_seconds() to correctly handle durations > 1 hour.

    Args:
        td: timedelta object to convert.

    Returns:
        Dictionary with hours, minutes, seconds, and milliseconds.
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000

    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "milliseconds": milliseconds,
    }


class ViralClipGenerator:
    """Generator for creating viral-ready video clips."""

    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR):
        """Initialize the ViralClipGenerator.

        Args:
            output_dir: Directory to save the generated clips.

        Raises:
            FFmpegNotFoundError: If ffmpeg/ffprobe is not installed.
        """
        _check_ffmpeg_installed()
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def download_video(self, url: str, output_path: Optional[str] = None) -> str:
        """Download a video from YouTube or other supported platforms.

        Args:
            url: URL of the video to download.
            output_path: Path to save the downloaded video.

        Returns:
            Path to the downloaded video file.
        """
        if output_path is None:
            output_path = os.path.join(self.output_dir, "source_video")

        ydl_opts = {
            "outtmpl": output_path + ".%(ext)s",
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
            "quiet": False,
            "no_warnings": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                print(f"Video downloaded to: {downloaded_file}")
                return downloaded_file
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            print("Retrying with simpler format selection...")
            ydl_opts["format"] = "best"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                print(f"Video downloaded to: {downloaded_file}")
                return downloaded_file

    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video file.

        Args:
            video_path: Path to the video file.

        Returns:
            Duration of the video in seconds.

        Raises:
            VideoProcessingError: If duration cannot be determined.
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]

        result = _run_ffmpeg_command(cmd, "get video duration")
        try:
            return float(result.stdout.strip())
        except ValueError as e:
            raise VideoProcessingError(f"Invalid duration value: {result.stdout}") from e

    def extract_clip(
        self,
        video_path: str,
        start_time: float,
        duration: float,
        output_path: Optional[str] = None,
    ) -> str:
        """Extract a clip from a video.

        Args:
            video_path: Path to the source video.
            start_time: Start time in seconds.
            duration: Duration of the clip in seconds.
            output_path: Path to save the clip.

        Returns:
            Path to the extracted clip.
        """
        if output_path is None:
            filename = f"clip_{int(start_time)}_{int(duration)}.mp4"
            output_path = os.path.join(self.output_dir, filename)

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(timedelta(seconds=start_time)),
            "-t", str(timedelta(seconds=duration)),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path,
            "-y",
        ]

        _run_ffmpeg_command(cmd, "extract clip")
        return output_path

    def _extract_audio(self, video_path: str) -> str:
        """Extract audio from a video file.

        Args:
            video_path: Path to the video file.

        Returns:
            Path to the extracted audio file.
        """
        audio_path = os.path.join(
            self.output_dir, f"{os.path.basename(video_path)}_audio.wav"
        )

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-q:a", "0",
            "-map", "a",
            "-f", "wav",
            audio_path,
            "-y",
        ]

        print("Extracting audio from video...")
        _run_ffmpeg_command(cmd, "extract audio")
        return audio_path

    def _transcribe_audio(
        self,
        audio_path: str,
        model_size: str = DEFAULT_WHISPER_MODEL,
    ) -> Dict[str, Any]:
        """Transcribe audio using Whisper.

        Args:
            audio_path: Path to the audio file.
            model_size: Whisper model size.

        Returns:
            Whisper transcription result dictionary.

        Raises:
            ImportError: If whisper is not installed.
        """
        try:
            import whisper
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. "
                "Install with: uv add openai-whisper torch"
            )

        print(f"Loading Whisper {model_size} model...")
        model = whisper.load_model(model_size)

        print("Transcribing audio with Whisper...")
        return model.transcribe(audio_path, fp16=False)

    def _create_srt_subtitles(
        self,
        segments: list,
        output_path: str,
    ) -> str:
        """Create an SRT subtitle file from transcription segments.

        Args:
            segments: List of transcription segments from Whisper.
            output_path: Path to save the SRT file.

        Returns:
            Path to the created SRT file.
        """
        try:
            import pysrt
        except ImportError:
            raise ImportError(
                "pysrt not installed. Install with: uv add pysrt"
            )

        subs = pysrt.SubRipFile()

        for i, segment in enumerate(segments):
            start = timedelta(seconds=segment["start"])
            end = timedelta(seconds=segment["end"])
            text = segment["text"].strip()

            start_time = _timedelta_to_srt_time(start)
            end_time = _timedelta_to_srt_time(end)

            item = pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(**start_time),
                end=pysrt.SubRipTime(**end_time),
                text=text,
            )
            subs.append(item)

        subs.save(output_path, encoding="utf-8")
        return output_path

    def add_subtitles(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        model_size: str = DEFAULT_WHISPER_MODEL,
    ) -> str:
        """Add subtitles to a video using Whisper speech recognition.

        Args:
            video_path: Path to the video.
            output_path: Path to save the video with subtitles.
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large').

        Returns:
            Path to the video with subtitles.
        """
        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_subtitled{ext}")

        # Extract and transcribe audio
        audio_path = self._extract_audio(video_path)

        try:
            result = self._transcribe_audio(audio_path, model_size)

            # Create SRT file
            srt_path = os.path.join(
                self.output_dir, f"{os.path.basename(video_path)}.srt"
            )
            self._create_srt_subtitles(result["segments"], srt_path)
            print(f"Subtitles saved to {srt_path}")

            # Burn subtitles into video
            print("Adding subtitles to video...")
            subtitle_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,Bold=1,Alignment=2'",
                "-c:a", "copy",
                output_path,
                "-y",
            ]

            _run_ffmpeg_command(subtitle_cmd, "burn subtitles")
            print(f"Video with subtitles created: {output_path}")
        finally:
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

        return output_path

    def transcribe_video(
        self,
        video_path: str,
        output_format: str = "srt",
        model_size: str = DEFAULT_WHISPER_MODEL,
    ) -> str:
        """Transcribe a video using Whisper and save as SRT or text file.

        Args:
            video_path: Path to the video.
            output_format: Output format ('srt' or 'txt').
            model_size: Whisper model size.

        Returns:
            Path to the transcript file.
        """
        # Extract and transcribe audio
        audio_path = self._extract_audio(video_path)

        try:
            result = self._transcribe_audio(audio_path, model_size)
            base_name = os.path.splitext(os.path.basename(video_path))[0]

            if output_format.lower() == "srt":
                output_path = os.path.join(self.output_dir, f"{base_name}.srt")
                self._create_srt_subtitles(result["segments"], output_path)
            else:
                output_path = os.path.join(self.output_dir, f"{base_name}.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result["text"])
        finally:
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

        print(f"Transcript saved to {output_path}")
        return output_path

    def add_text_overlay(
        self,
        video_path: str,
        text: str = DEFAULT_TEXT_OVERLAY,
        position: str = DEFAULT_TEXT_POSITION,
        output_path: Optional[str] = None,
    ) -> str:
        """Add text overlay to a video.

        Args:
            video_path: Path to the video.
            text: Text to overlay.
            position: Position of the text (top, bottom, center).
            output_path: Path to save the video with text overlay.

        Returns:
            Path to the video with text overlay.
        """
        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_text{ext}")

        pos = TEXT_POSITIONS.get(position, TEXT_POSITIONS[DEFAULT_TEXT_POSITION])

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"drawtext=text='{text}':fontsize=24:fontcolor=white:bordercolor=black:borderw=2:{pos}",
            "-c:a", "copy",
            output_path,
            "-y",
        ]

        _run_ffmpeg_command(cmd, "add text overlay")
        return output_path

    def crop_for_social(
        self,
        video_path: str,
        format: str = "portrait",
        output_path: Optional[str] = None,
    ) -> str:
        """Crop video for social media platforms.

        Args:
            video_path: Path to the video.
            format: Target format (portrait, square, landscape).
            output_path: Path to save the cropped video.

        Returns:
            Path to the cropped video.
        """
        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_{format}{ext}")

        crop_filter = FORMAT_CROP_FILTERS.get(format, FORMAT_CROP_FILTERS["portrait"])

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", crop_filter,
            "-c:a", "copy",
            output_path,
            "-y",
        ]

        _run_ffmpeg_command(cmd, f"crop video for {format}")
        return output_path

    def generate_random_clip(
        self,
        video_path: str,
        clip_duration: int = DEFAULT_CLIP_DURATION,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate a random clip from a video.

        Args:
            video_path: Path to the source video.
            clip_duration: Duration of the clip in seconds.
            output_path: Path to save the clip.

        Returns:
            Path to the generated clip.
        """
        duration = self.get_video_duration(video_path)
        max_start = max(0, duration - clip_duration)
        start_time = random.uniform(0, max_start)
        return self.extract_clip(video_path, start_time, clip_duration, output_path)

    def create_viral_clip(
        self,
        video_source: str,
        clip_duration: int = DEFAULT_CLIP_DURATION,
        add_subs: bool = True,
        add_text: bool = True,
        text_overlay: str = DEFAULT_TEXT_OVERLAY,
        format: str = "portrait",
    ) -> str:
        """Create a viral-ready clip from a video source.

        Args:
            video_source: URL or path to the source video.
            clip_duration: Duration of the clip in seconds.
            add_subs: Whether to add subtitles.
            add_text: Whether to add text overlay.
            text_overlay: Custom text for overlay.
            format: Target format (portrait, square, landscape).

        Returns:
            Path to the final viral clip.
        """
        # Download the video if it's a URL
        if video_source.startswith(("http://", "https://")):
            video_path = self.download_video(video_source)
        else:
            video_path = video_source

        # Extract a random clip
        clip_path = self.generate_random_clip(video_path, clip_duration)
        processed_path = clip_path

        # Add subtitles if requested
        if add_subs:
            processed_path = self.add_subtitles(processed_path)

        # Add text overlay if requested
        if add_text:
            processed_path = self.add_text_overlay(
                processed_path, text_overlay, DEFAULT_TEXT_POSITION
            )

        # Crop for social media
        final_path = self.crop_for_social(processed_path, format)

        return final_path
