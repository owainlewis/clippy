"""Pytest configuration and fixtures for clippy tests."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_ffmpeg():
    """Mock ffmpeg/ffprobe availability check."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/ffmpeg"
        yield mock_which


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for ffmpeg commands."""
    with patch("clippy.generator.subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "10.5"  # Duration in seconds
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def sample_whisper_result():
    """Sample Whisper transcription result."""
    return {
        "text": "Hello world, this is a test transcription.",
        "segments": [
            {
                "start": 0.0,
                "end": 2.5,
                "text": " Hello world,",
            },
            {
                "start": 2.5,
                "end": 5.0,
                "text": " this is a test transcription.",
            },
        ],
    }
