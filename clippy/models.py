"""
Pydantic models for the Clippy API.
"""

from typing import Optional, List, Union
from pydantic import BaseModel, HttpUrl, Field, validator
from enum import Enum


class VideoFormat(str, Enum):
    """Enum for video output formats."""
    PORTRAIT = "portrait"
    SQUARE = "square"
    LANDSCAPE = "landscape"


class TranscriptionFormat(str, Enum):
    """Enum for transcription output formats."""
    SRT = "srt"
    TXT = "txt"


class WhisperModel(str, Enum):
    """Enum for Whisper model sizes."""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class TaskStatusEnum(str, Enum):
    """Enum for task statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Request Models
class VideoProcessRequest(BaseModel):
    """Request model for video processing (create_viral_clip)."""
    source: str = Field(..., description="URL or uploaded file identifier")
    clip_duration: int = Field(15, ge=1, le=300, description="Duration of the clip in seconds")
    format: VideoFormat = Field(VideoFormat.PORTRAIT, description="Output format")
    add_subs: bool = Field(True, description="Whether to add subtitles")
    add_text: bool = Field(True, description="Whether to add text overlay (hardcoded message)")

    @validator('source')
    def validate_source(cls, v):
        """Validate source is either URL or file ID."""
        if not v:
            raise ValueError('Source cannot be empty')
        return v


class TranscribeRequest(BaseModel):
    """Request model for video transcription."""
    source: str = Field(..., description="URL or uploaded file identifier")
    output_format: TranscriptionFormat = Field(TranscriptionFormat.SRT, description="Output format for transcription")
    whisper_model: WhisperModel = Field(WhisperModel.BASE, description="Whisper model size")

    @validator('source')
    def validate_source(cls, v):
        """Validate source is either URL or file ID."""
        if not v:
            raise ValueError('Source cannot be empty')
        return v


class DownloadRequest(BaseModel):
    """Request model for video download."""
    url: HttpUrl = Field(..., description="Video URL to download")
    output_filename: Optional[str] = Field(None, description="Custom output filename")

    @validator('output_filename')
    def validate_filename(cls, v):
        """Validate filename if provided."""
        if v and ('/' in v or '\\' in v):
            raise ValueError('Filename cannot contain path separators')
        return v


class ClipExtractionRequest(BaseModel):
    """Request model for extracting a specific clip (extract_clip)."""
    source: str = Field(..., description="URL or uploaded file identifier")
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    duration: float = Field(..., gt=0, le=300, description="Duration in seconds")


class RandomClipRequest(BaseModel):
    """Request model for generating a random clip (generate_random_clip)."""
    source: str = Field(..., description="URL or uploaded file identifier")
    clip_duration: int = Field(15, ge=1, le=300, description="Duration of the clip in seconds")


class AddSubtitlesRequest(BaseModel):
    """Request model for adding subtitles (add_subtitles)."""
    source: str = Field(..., description="URL or uploaded file identifier")
    model_size: WhisperModel = Field(WhisperModel.BASE, description="Whisper model size")


class TextOverlayRequest(BaseModel):
    """Request model for adding text overlay (add_text_overlay)."""
    source: str = Field(..., description="URL or uploaded file identifier")
    text: str = Field(..., description="Text to overlay on the video")
    position: str = Field("bottom", pattern="^(top|bottom|center)$", description="Text position")


class CropRequest(BaseModel):
    """Request model for cropping video for social media (crop_for_social)."""
    source: str = Field(..., description="URL or uploaded file identifier")
    format: VideoFormat = Field(VideoFormat.PORTRAIT, description="Output format")


# Response Models
class ProcessResponse(BaseModel):
    """Response model for processing operations."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatusEnum = Field(..., description="Task status")
    message: str = Field(..., description="Status message")
    result_url: Optional[str] = Field(None, description="URL to download the result")


class TaskStatus(BaseModel):
    """Model for task status."""
    task_id: str
    status: TaskStatusEnum
    message: str
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    result_url: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UploadResponse(BaseModel):
    """Response model for file upload."""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    message: str = Field(..., description="Upload status message")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: Optional[str] = Field(None, description="Service version")


class ApiInfoResponse(BaseModel):
    """Response model for API information."""
    message: str
    version: str
    docs: str
    redoc: str


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    task_id: Optional[str] = Field(None, description="Task ID if applicable")


class VideoInfo(BaseModel):
    """Model for video information."""
    duration: Optional[float] = Field(None, description="Video duration in seconds")
    width: Optional[int] = Field(None, description="Video width in pixels")
    height: Optional[int] = Field(None, description="Video height in pixels")
    fps: Optional[float] = Field(None, description="Frames per second")
    format: Optional[str] = Field(None, description="Video format")
    size: Optional[int] = Field(None, description="File size in bytes")


class ProcessingOptions(BaseModel):
    """Model for processing options."""
    add_subtitles: bool = True
    add_text_overlay: bool = True
    text_content: Optional[str] = None
    text_position: str = "bottom"
    subtitle_style: Optional[dict] = None
    video_quality: str = "high"
    audio_quality: str = "high"


# List response models
class TaskListResponse(BaseModel):
    """Response model for task list."""
    tasks: List[TaskStatus]
    total: int
    page: int = 1
    per_page: int = 50


class FileListResponse(BaseModel):
    """Response model for file list."""
    files: List[dict]
    total: int
