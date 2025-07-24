"""
FastAPI application for Clippy video processing service.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, List
import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .generator import ViralClipGenerator
from .models import (
    VideoProcessRequest, TranscribeRequest, DownloadRequest, ClipExtractionRequest,
    RandomClipRequest, AddSubtitlesRequest, TextOverlayRequest, CropRequest,
    ProcessResponse, TaskStatus, UploadResponse, HealthResponse, ApiInfoResponse,
    ErrorResponse, TaskStatusEnum
)


# FastAPI app initialization
app = FastAPI(
    title="Clippy Video Processing API",
    description="A REST API for video processing, transcription, and clip generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for task tracking
tasks = {}
output_dir = "api_output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    print("Clippy API starting up...")
    print(f"Output directory: {output_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Clippy API shutting down...")


@app.get("/", response_model=ApiInfoResponse)
async def root():
    """Root endpoint with API information."""
    return ApiInfoResponse(
        message="Welcome to Clippy Video Processing API",
        version="1.0.0",
        docs="/docs",
        redoc="/redoc"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="clippy-api", version="1.0.0")


@app.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file for processing."""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Validate file size (max 500MB)
    content = await file.read()
    max_size = 500 * 1024 * 1024  # 500MB
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 500MB")

    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix if file.filename else '.mp4'

    # Validate file extension
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
    if file_extension.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )

    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(output_dir, "uploads", filename)

    # Ensure upload directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        return UploadResponse(
            file_id=file_id,
            filename=filename,
            size=len(content),
            message="File uploaded successfully"
        )
    except Exception as e:
        # Clean up file if save failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def update_task_status(task_id: str, status: TaskStatusEnum, message: str, progress: int = None,
                      result_url: str = None, error: str = None):
    """Update task status."""
    from datetime import datetime
    current_time = datetime.now().isoformat()

    if task_id not in tasks:
        created_at = current_time
    else:
        created_at = tasks[task_id].created_at

    tasks[task_id] = TaskStatus(
        task_id=task_id,
        status=status,
        message=message,
        progress=progress,
        result_url=result_url,
        error=error,
        created_at=created_at,
        updated_at=current_time
    )


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a processing task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]


@app.get("/tasks", response_model=List[TaskStatus])
async def list_tasks():
    """List all tasks."""
    return list(tasks.values())


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a processed file."""
    # Check in main output directory
    file_path = os.path.join(output_dir, filename)

    # If not found, check in uploads directory
    if not os.path.exists(file_path):
        file_path = os.path.join(output_dir, "uploads", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type based on file extension
    media_type = 'application/octet-stream'
    if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        media_type = 'video/mp4'
    elif filename.lower().endswith(('.srt', '.txt')):
        media_type = 'text/plain'

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )


@app.get("/files")
async def list_files():
    """List all available files."""
    files = []

    # List files in main output directory
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "type": "processed"
                })

    # List files in uploads directory
    uploads_dir = os.path.join(output_dir, "uploads")
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "type": "uploaded"
                })

    return {"files": files, "total": len(files)}


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file."""
    # Check in main output directory
    file_path = os.path.join(output_dir, filename)

    # If not found, check in uploads directory
    if not os.path.exists(file_path):
        file_path = os.path.join(output_dir, "uploads", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@app.post("/upload-multiple", response_model=List[UploadResponse])
async def upload_multiple_videos(files: List[UploadFile] = File(...)):
    """Upload multiple video files for processing."""
    responses = []

    for file in files:
        if not file.content_type or not file.content_type.startswith('video/'):
            responses.append(UploadResponse(
                file_id="",
                filename=file.filename or "unknown",
                size=0,
                message=f"Skipped {file.filename}: not a video file"
            ))
            continue

        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix if file.filename else '.mp4'
            filename = f"{file_id}{file_extension}"
            file_path = os.path.join(output_dir, "uploads", filename)

            # Ensure upload directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save uploaded file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            responses.append(UploadResponse(
                file_id=file_id,
                filename=filename,
                size=len(content),
                message="File uploaded successfully"
            ))

        except Exception as e:
            responses.append(UploadResponse(
                file_id="",
                filename=file.filename or "unknown",
                size=0,
                message=f"Failed to upload {file.filename}: {str(e)}"
            ))

    return responses


@app.post("/process", response_model=ProcessResponse)
async def process_video(request: VideoProcessRequest, background_tasks: BackgroundTasks):
    """Process a video to create a viral clip."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Task created", progress=0)

    # Add background task
    background_tasks.add_task(process_video_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Video processing started"
    )


@app.post("/transcribe", response_model=ProcessResponse)
async def transcribe_video(request: TranscribeRequest, background_tasks: BackgroundTasks):
    """Transcribe a video using Whisper."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Transcription task created", progress=0)

    # Add background task
    background_tasks.add_task(transcribe_video_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Video transcription started"
    )


@app.post("/download", response_model=ProcessResponse)
async def download_video_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Download a video from URL."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Download task created", progress=0)

    # Add background task
    background_tasks.add_task(download_video_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Video download started"
    )


@app.post("/extract-clip", response_model=ProcessResponse)
async def extract_clip(request: ClipExtractionRequest, background_tasks: BackgroundTasks):
    """Extract a specific clip from a video."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Clip extraction task created", progress=0)

    # Add background task
    background_tasks.add_task(extract_clip_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Clip extraction started"
    )


# Background task functions
async def process_video_task(task_id: str, request: VideoProcessRequest):
    """Background task for video processing using create_viral_clip."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting video processing", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Creating viral clip", progress=50)

        # Create viral clip using the actual method signature
        result_path = generator.create_viral_clip(
            video_source=source_path,
            clip_duration=request.clip_duration,
            add_subs=request.add_subs,
            add_text=request.add_text,
            format=request.format.value
        )

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Viral clip created successfully",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Video processing failed",
            error=str(e)
        )


async def transcribe_video_task(task_id: str, request: TranscribeRequest):
    """Background task for video transcription."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting transcription", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Transcribing video", progress=50)

        # Transcribe video
        result_path = generator.transcribe_video(
            source_path,
            output_format=request.output_format.value,
            model_size=request.whisper_model.value
        )

        if result_path:
            # Generate result URL
            result_filename = os.path.basename(result_path)
            result_url = f"/download/{result_filename}"

            update_task_status(
                task_id,
                TaskStatusEnum.COMPLETED,
                "Transcription completed",
                progress=100,
                result_url=result_url
            )
        else:
            update_task_status(
                task_id,
                TaskStatusEnum.FAILED,
                "Transcription failed - no result file generated"
            )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Transcription failed",
            error=str(e)
        )


async def download_video_task(task_id: str, request: DownloadRequest):
    """Background task for video download."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting download", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Downloading video", progress=50)

        # Download video
        output_path = None
        if request.output_filename:
            output_path = os.path.join(output_dir, request.output_filename)

        result_path = generator.download_video(str(request.url), output_path)

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Download completed",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Download failed",
            error=str(e)
        )


async def extract_clip_task(task_id: str, request: ClipExtractionRequest):
    """Background task for clip extraction using extract_clip."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting clip extraction", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Extracting clip", progress=50)

        # Extract clip using the actual method signature
        result_path = generator.extract_clip(
            video_path=source_path,
            start_time=request.start_time,
            duration=request.duration,
            output_path=None
        )

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Clip extraction completed",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Clip extraction failed",
            error=str(e)
        )


@app.post("/generate-random-clip", response_model=ProcessResponse)
async def generate_random_clip(request: RandomClipRequest, background_tasks: BackgroundTasks):
    """Generate a random clip from a video."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Random clip generation task created", progress=0)

    # Add background task
    background_tasks.add_task(generate_random_clip_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Random clip generation started"
    )


@app.post("/add-subtitles", response_model=ProcessResponse)
async def add_subtitles_endpoint(request: AddSubtitlesRequest, background_tasks: BackgroundTasks):
    """Add subtitles to a video using Whisper."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Subtitle addition task created", progress=0)

    # Add background task
    background_tasks.add_task(add_subtitles_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Subtitle addition started"
    )


@app.post("/add-text-overlay", response_model=ProcessResponse)
async def add_text_overlay_endpoint(request: TextOverlayRequest, background_tasks: BackgroundTasks):
    """Add text overlay to a video."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Text overlay task created", progress=0)

    # Add background task
    background_tasks.add_task(add_text_overlay_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Text overlay addition started"
    )


@app.post("/crop-for-social", response_model=ProcessResponse)
async def crop_for_social_endpoint(request: CropRequest, background_tasks: BackgroundTasks):
    """Crop video for social media platforms."""
    task_id = str(uuid.uuid4())

    # Initialize task
    update_task_status(task_id, TaskStatusEnum.PENDING, "Video cropping task created", progress=0)

    # Add background task
    background_tasks.add_task(crop_for_social_task, task_id, request)

    return ProcessResponse(
        task_id=task_id,
        status=TaskStatusEnum.PENDING,
        message="Video cropping started"
    )


def get_source_path(source: str) -> str:
    """Get the actual file path from source (URL or file ID)."""
    if not source:
        raise ValueError("Source cannot be empty")

    if source.startswith(('http://', 'https://')):
        # Validate URL format
        try:
            from urllib.parse import urlparse
            result = urlparse(source)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception:
            raise ValueError("Invalid URL format")
        return source
    else:
        # Assume it's a file ID from upload
        # Find the file in uploads directory
        uploads_dir = os.path.join(output_dir, "uploads")

        if not os.path.exists(uploads_dir):
            raise ValueError("No uploaded files found")

        try:
            for filename in os.listdir(uploads_dir):
                if filename.startswith(source):
                    file_path = os.path.join(uploads_dir, filename)
                    if os.path.isfile(file_path):
                        return file_path
        except Exception as e:
            raise ValueError(f"Error accessing uploads directory: {str(e)}")

        raise ValueError(f"File not found for ID: {source}")


async def generate_random_clip_task(task_id: str, request: RandomClipRequest):
    """Background task for generating random clips."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting random clip generation", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Generating random clip", progress=50)

        # Generate random clip
        result_path = generator.generate_random_clip(
            video_path=source_path,
            clip_duration=request.clip_duration,
            output_path=None
        )

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Random clip generated successfully",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Random clip generation failed",
            error=str(e)
        )


async def add_subtitles_task(task_id: str, request: AddSubtitlesRequest):
    """Background task for adding subtitles."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting subtitle addition", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Adding subtitles", progress=50)

        # Add subtitles
        result_path = generator.add_subtitles(
            video_path=source_path,
            output_path=None,
            model_size=request.model_size.value
        )

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Subtitles added successfully",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Subtitle addition failed",
            error=str(e)
        )


async def add_text_overlay_task(task_id: str, request: TextOverlayRequest):
    """Background task for adding text overlay."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting text overlay addition", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Adding text overlay", progress=50)

        # Add text overlay
        result_path = generator.add_text_overlay(
            video_path=source_path,
            text=request.text,
            position=request.position,
            output_path=None
        )

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Text overlay added successfully",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Text overlay addition failed",
            error=str(e)
        )


async def crop_for_social_task(task_id: str, request: CropRequest):
    """Background task for cropping video for social media."""
    try:
        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Starting video cropping", progress=10)

        generator = ViralClipGenerator(output_dir=output_dir)

        # Determine source path
        source_path = get_source_path(request.source)

        update_task_status(task_id, TaskStatusEnum.PROCESSING, "Cropping video", progress=50)

        # Crop for social media
        result_path = generator.crop_for_social(
            video_path=source_path,
            format=request.format.value,
            output_path=None
        )

        # Generate result URL
        result_filename = os.path.basename(result_path)
        result_url = f"/download/{result_filename}"

        update_task_status(
            task_id,
            TaskStatusEnum.COMPLETED,
            "Video cropped successfully",
            progress=100,
            result_url=result_url
        )

    except Exception as e:
        update_task_status(
            task_id,
            TaskStatusEnum.FAILED,
            "Video cropping failed",
            error=str(e)
        )


# Error handlers
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "status_code": 400}
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle file not found errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "File not found", "detail": str(exc), "status_code": 404}
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    """Handle permission errors."""
    return JSONResponse(
        status_code=403,
        content={"error": "Permission denied", "detail": str(exc), "status_code": 403}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    import traceback
    error_detail = f"Internal server error: {str(exc)}"

    # Log the full traceback for debugging
    print(f"Unhandled exception: {traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": error_detail,
            "status_code": 500
        }
    )
