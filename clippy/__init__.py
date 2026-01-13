"""
Clippy - A Python tool for extracting and processing video clips
"""

from .generator import (
    ViralClipGenerator,
    FFmpegNotFoundError,
    VideoProcessingError,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_CLIP_DURATION,
    DEFAULT_WHISPER_MODEL,
    DEFAULT_TEXT_OVERLAY,
    WHISPER_MODELS,
    FORMAT_CROP_FILTERS,
)

__version__ = "0.1.0"
__all__ = [
    "ViralClipGenerator",
    "FFmpegNotFoundError",
    "VideoProcessingError",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_CLIP_DURATION",
    "DEFAULT_WHISPER_MODEL",
    "DEFAULT_TEXT_OVERLAY",
    "WHISPER_MODELS",
    "FORMAT_CROP_FILTERS",
]
