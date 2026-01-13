"""Tests for the clippy.cli module."""

import sys
from unittest.mock import patch, MagicMock

import pytest


class TestCLIArguments:
    """Tests for CLI argument parsing."""

    def test_source_required(self):
        """Test that source argument is required."""
        with patch("sys.argv", ["clippy"]):
            from clippy.cli import main
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # argparse error code

    def test_default_values(self):
        """Test default argument values."""
        test_args = ["clippy", "video.mp4"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.create_viral_clip.return_value = "/output/clip.mp4"

                from clippy.cli import main
                main()

                mock_instance.create_viral_clip.assert_called_once_with(
                    "video.mp4",
                    clip_duration=15,  # default
                    add_subs=True,  # default
                    add_text=True,  # default
                    format="portrait",  # default
                )

    def test_download_only_mode(self):
        """Test --download-only flag."""
        test_args = ["clippy", "https://example.com/video", "--download-only"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.download_video.return_value = "/output/video.mp4"

                from clippy.cli import main
                main()

                mock_instance.download_video.assert_called_once()
                mock_instance.create_viral_clip.assert_not_called()

    def test_download_only_requires_url(self, capsys):
        """Test that --download-only requires a URL, not a local file."""
        test_args = ["clippy", "local_video.mp4", "--download-only"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance

                from clippy.cli import main
                main()

                # Should print error and return without downloading
                mock_instance.download_video.assert_not_called()
                captured = capsys.readouterr()
                assert "requires a URL" in captured.out

    def test_transcribe_mode(self):
        """Test --transcribe flag."""
        test_args = ["clippy", "video.mp4", "--transcribe"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.transcribe_video.return_value = "/output/video.srt"

                from clippy.cli import main
                main()

                mock_instance.transcribe_video.assert_called_once()
                mock_instance.create_viral_clip.assert_not_called()

    def test_custom_duration(self):
        """Test --duration argument."""
        test_args = ["clippy", "video.mp4", "--duration", "30"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.create_viral_clip.return_value = "/output/clip.mp4"

                from clippy.cli import main
                main()

                call_kwargs = mock_instance.create_viral_clip.call_args
                assert call_kwargs[1]["clip_duration"] == 30

    def test_no_subs_flag(self):
        """Test --no-subs flag."""
        test_args = ["clippy", "video.mp4", "--no-subs"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.create_viral_clip.return_value = "/output/clip.mp4"

                from clippy.cli import main
                main()

                call_kwargs = mock_instance.create_viral_clip.call_args
                assert call_kwargs[1]["add_subs"] is False

    def test_no_text_flag(self):
        """Test --no-text flag."""
        test_args = ["clippy", "video.mp4", "--no-text"]

        with patch("sys.argv", test_args):
            with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.create_viral_clip.return_value = "/output/clip.mp4"

                from clippy.cli import main
                main()

                call_kwargs = mock_instance.create_viral_clip.call_args
                assert call_kwargs[1]["add_text"] is False

    def test_format_choices(self):
        """Test --format argument accepts valid choices."""
        for fmt in ["portrait", "square", "landscape"]:
            test_args = ["clippy", "video.mp4", "--format", fmt]

            with patch("sys.argv", test_args):
                with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                    mock_instance = MagicMock()
                    mock_gen.return_value = mock_instance
                    mock_instance.create_viral_clip.return_value = "/output/clip.mp4"

                    from clippy.cli import main
                    main()

                    call_kwargs = mock_instance.create_viral_clip.call_args
                    assert call_kwargs[1]["format"] == fmt

    def test_whisper_model_choices(self):
        """Test --whisper-model argument accepts valid choices."""
        for model in ["tiny", "base", "small", "medium", "large"]:
            test_args = [
                "clippy", "video.mp4", "--transcribe", "--whisper-model", model
            ]

            with patch("sys.argv", test_args):
                with patch("clippy.cli.ViralClipGenerator") as mock_gen:
                    mock_instance = MagicMock()
                    mock_gen.return_value = mock_instance
                    mock_instance.transcribe_video.return_value = "/output/video.srt"

                    from clippy.cli import main
                    main()

                    call_kwargs = mock_instance.transcribe_video.call_args
                    assert call_kwargs[1]["model_size"] == model
