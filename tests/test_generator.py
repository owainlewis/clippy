"""Tests for the clippy.generator module."""

import os
import tempfile
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest

from clippy.generator import (
    ViralClipGenerator,
    FFmpegNotFoundError,
    VideoProcessingError,
    _timedelta_to_srt_time,
    _check_ffmpeg_installed,
    _run_ffmpeg_command,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_CLIP_DURATION,
    DEFAULT_TEXT_OVERLAY,
    WHISPER_MODELS,
    FORMAT_CROP_FILTERS,
    TEXT_POSITIONS,
)


class TestTimedeltaToSrtTime:
    """Tests for _timedelta_to_srt_time function."""

    def test_zero_duration(self):
        """Test conversion of zero duration."""
        result = _timedelta_to_srt_time(timedelta(seconds=0))
        assert result == {
            "hours": 0,
            "minutes": 0,
            "seconds": 0,
            "milliseconds": 0,
        }

    def test_simple_seconds(self):
        """Test conversion of simple seconds."""
        result = _timedelta_to_srt_time(timedelta(seconds=45))
        assert result == {
            "hours": 0,
            "minutes": 0,
            "seconds": 45,
            "milliseconds": 0,
        }

    def test_minutes_and_seconds(self):
        """Test conversion of minutes and seconds."""
        result = _timedelta_to_srt_time(timedelta(minutes=5, seconds=30))
        assert result == {
            "hours": 0,
            "minutes": 5,
            "seconds": 30,
            "milliseconds": 0,
        }

    def test_hours_minutes_seconds(self):
        """Test conversion of hours, minutes, and seconds."""
        result = _timedelta_to_srt_time(timedelta(hours=2, minutes=15, seconds=45))
        assert result == {
            "hours": 2,
            "minutes": 15,
            "seconds": 45,
            "milliseconds": 0,
        }

    def test_with_milliseconds(self):
        """Test conversion with milliseconds."""
        result = _timedelta_to_srt_time(
            timedelta(hours=1, minutes=30, seconds=15, milliseconds=500)
        )
        assert result == {
            "hours": 1,
            "minutes": 30,
            "seconds": 15,
            "milliseconds": 500,
        }

    def test_large_duration_over_24_hours(self):
        """Test that durations over 24 hours are handled correctly.

        This was a bug in the original code that used timedelta.seconds
        instead of total_seconds().
        """
        # 25 hours, 30 minutes, 15 seconds
        result = _timedelta_to_srt_time(
            timedelta(hours=25, minutes=30, seconds=15)
        )
        assert result == {
            "hours": 25,
            "minutes": 30,
            "seconds": 15,
            "milliseconds": 0,
        }


class TestCheckFfmpegInstalled:
    """Tests for _check_ffmpeg_installed function."""

    def test_ffmpeg_not_found(self):
        """Test that FFmpegNotFoundError is raised when ffmpeg is not found."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            with pytest.raises(FFmpegNotFoundError) as exc_info:
                _check_ffmpeg_installed()
            assert "ffmpeg not found" in str(exc_info.value)

    def test_ffprobe_not_found(self):
        """Test that FFmpegNotFoundError is raised when ffprobe is not found."""
        with patch("shutil.which") as mock_which:
            # ffmpeg found, ffprobe not found
            mock_which.side_effect = lambda x: "/usr/bin/ffmpeg" if x == "ffmpeg" else None
            with pytest.raises(FFmpegNotFoundError) as exc_info:
                _check_ffmpeg_installed()
            assert "ffprobe not found" in str(exc_info.value)

    def test_both_found(self):
        """Test that no exception is raised when both are found."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/ffmpeg"
            _check_ffmpeg_installed()  # Should not raise


class TestRunFfmpegCommand:
    """Tests for _run_ffmpeg_command function."""

    def test_successful_command(self):
        """Test running a successful command."""
        with patch("clippy.generator.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            result = _run_ffmpeg_command(["ffmpeg", "-version"], "check version")
            assert result.returncode == 0

    def test_failed_command(self):
        """Test that VideoProcessingError is raised on command failure."""
        with patch("clippy.generator.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Error: invalid input"
            mock_run.return_value = mock_result

            with pytest.raises(VideoProcessingError) as exc_info:
                _run_ffmpeg_command(["ffmpeg", "-i", "bad.mp4"], "process video")
            assert "Failed to process video" in str(exc_info.value)
            assert "invalid input" in str(exc_info.value)


class TestViralClipGenerator:
    """Tests for ViralClipGenerator class."""

    def test_init_creates_output_dir(self, mock_ffmpeg):
        """Test that __init__ creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "new_output")
            generator = ViralClipGenerator(output_dir=output_dir)
            assert os.path.exists(output_dir)
            assert generator.output_dir == output_dir

    def test_init_raises_without_ffmpeg(self):
        """Test that __init__ raises FFmpegNotFoundError without ffmpeg."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            with pytest.raises(FFmpegNotFoundError):
                ViralClipGenerator()

    def test_get_video_duration(self, mock_ffmpeg, mock_subprocess, temp_output_dir):
        """Test getting video duration."""
        generator = ViralClipGenerator(output_dir=temp_output_dir)
        duration = generator.get_video_duration("/path/to/video.mp4")
        assert duration == 10.5

    def test_extract_clip_default_output(
        self, mock_ffmpeg, mock_subprocess, temp_output_dir
    ):
        """Test extract_clip generates correct default output path."""
        generator = ViralClipGenerator(output_dir=temp_output_dir)
        output_path = generator.extract_clip("/path/to/video.mp4", 5.0, 15.0)
        assert output_path == os.path.join(temp_output_dir, "clip_5_15.mp4")

    def test_extract_clip_custom_output(
        self, mock_ffmpeg, mock_subprocess, temp_output_dir
    ):
        """Test extract_clip with custom output path."""
        generator = ViralClipGenerator(output_dir=temp_output_dir)
        custom_path = os.path.join(temp_output_dir, "custom_clip.mp4")
        output_path = generator.extract_clip(
            "/path/to/video.mp4", 5.0, 15.0, output_path=custom_path
        )
        assert output_path == custom_path

    def test_add_text_overlay_positions(
        self, mock_ffmpeg, mock_subprocess, temp_output_dir
    ):
        """Test that text overlay supports all positions."""
        generator = ViralClipGenerator(output_dir=temp_output_dir)

        for position in TEXT_POSITIONS:
            output_path = generator.add_text_overlay(
                "/path/to/video.mp4",
                text="Test",
                position=position,
            )
            assert output_path is not None

    def test_crop_for_social_formats(
        self, mock_ffmpeg, mock_subprocess, temp_output_dir
    ):
        """Test that crop_for_social supports all formats."""
        generator = ViralClipGenerator(output_dir=temp_output_dir)

        for fmt in FORMAT_CROP_FILTERS:
            output_path = generator.crop_for_social("/path/to/video.mp4", format=fmt)
            assert fmt in output_path


class TestConstants:
    """Tests for module constants."""

    def test_whisper_models(self):
        """Test that all expected Whisper models are defined."""
        expected = ("tiny", "base", "small", "medium", "large")
        assert WHISPER_MODELS == expected

    def test_format_crop_filters(self):
        """Test that all social media formats are defined."""
        assert "portrait" in FORMAT_CROP_FILTERS
        assert "square" in FORMAT_CROP_FILTERS
        assert "landscape" in FORMAT_CROP_FILTERS

    def test_text_positions(self):
        """Test that all text positions are defined."""
        assert "top" in TEXT_POSITIONS
        assert "center" in TEXT_POSITIONS
        assert "bottom" in TEXT_POSITIONS

    def test_default_values(self):
        """Test default values are sensible."""
        assert DEFAULT_OUTPUT_DIR == "output"
        assert DEFAULT_CLIP_DURATION == 15
        assert isinstance(DEFAULT_TEXT_OVERLAY, str)
        assert len(DEFAULT_TEXT_OVERLAY) > 0
