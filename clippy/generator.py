import os
import argparse
import subprocess
import random
from datetime import timedelta
import yt_dlp


class ViralClipGenerator:
    def __init__(self, output_dir="output"):
        """Initialize the ViralClipGenerator.

        Args:
            output_dir (str): Directory to save the generated clips
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def download_video(self, url, output_path=None):
        """Download a video from YouTube or other supported platforms.

        Args:
            url (str): URL of the video to download
            output_path (str, optional): Path to save the downloaded video

        Returns:
            str: Path to the downloaded video file
        """
        if output_path is None:
            output_path = os.path.join(self.output_dir, "source_video")

        # Download in best available quality with specific format selection
        ydl_opts = {
            "outtmpl": output_path + ".%(ext)s",  # Let yt-dlp add the correct extension
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",  # Prefer 1080p or lower
            "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
            "quiet": False,  # Show download progress
            "no_warnings": False,  # Show warnings
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First try to get video info
                info = ydl.extract_info(url, download=False)
                if info:
                    # If we got info, proceed with download
                    info = ydl.extract_info(url, download=True)
                    downloaded_file = ydl.prepare_filename(info)
                    print(f"Video downloaded to: {downloaded_file}")
                    return downloaded_file
                else:
                    raise Exception("Could not extract video information")
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            # Try with simpler format selection as fallback
            ydl_opts["format"] = "best"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                print(f"Video downloaded to: {downloaded_file}")
                return downloaded_file

    def get_video_duration(self, video_path):
        """Get the duration of a video file.

        Args:
            video_path (str): Path to the video file

        Returns:
            float: Duration of the video in seconds
        """
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip())

    def extract_clip(self, video_path, start_time, duration, output_path=None):
        """Extract a clip from a video.

        Args:
            video_path (str): Path to the source video
            start_time (float): Start time in seconds
            duration (float): Duration of the clip in seconds
            output_path (str, optional): Path to save the clip

        Returns:
            str: Path to the extracted clip
        """
        if output_path is None:
            filename = f"clip_{int(start_time)}_{int(duration)}.mp4"
            output_path = os.path.join(self.output_dir, filename)

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-ss",
            str(timedelta(seconds=start_time)),
            "-t",
            str(timedelta(seconds=duration)),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            output_path,
            "-y",  # Overwrite if file exists
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path

    def add_subtitles(self, video_path, output_path=None, model_size="base"):
        """Add subtitles to a video using OpenAI's Whisper speech recognition.

        Args:
            video_path (str): Path to the video
            output_path (str, optional): Path to save the video with subtitles
            model_size (str, optional): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')

        Returns:
            str: Path to the video with subtitles
        """
        try:
            import whisper
            import pysrt
            from datetime import timedelta
        except ImportError:
            print("Error: Required packages not installed.")
            print("Please install them with: pip install openai-whisper torch pysrt")
            return video_path

        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_subtitled{ext}")

        # Extract audio from video
        audio_path = os.path.join(
            self.output_dir, f"{os.path.basename(video_path)}_audio.wav"
        )
        extract_cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-q:a",
            "0",
            "-map",
            "a",
            "-f",
            "wav",
            audio_path,
            "-y",
        ]

        print(f"Extracting audio from video...")
        subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Load Whisper model
        print(f"Loading Whisper {model_size} model...")
        model = whisper.load_model(model_size)

        # Transcribe audio
        print(f"Transcribing audio with Whisper...")
        result = model.transcribe(audio_path, fp16=False)

        # Create SRT file
        srt_path = os.path.join(self.output_dir, f"{os.path.basename(video_path)}.srt")
        subs = pysrt.SubRipFile()

        for i, segment in enumerate(result["segments"]):
            start = timedelta(seconds=segment["start"])
            end = timedelta(seconds=segment["end"])
            text = segment["text"].strip()

            item = pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(
                    hours=start.seconds // 3600,
                    minutes=(start.seconds // 60) % 60,
                    seconds=start.seconds % 60,
                    milliseconds=start.microseconds // 1000,
                ),
                end=pysrt.SubRipTime(
                    hours=end.seconds // 3600,
                    minutes=(end.seconds // 60) % 60,
                    seconds=end.seconds % 60,
                    milliseconds=end.microseconds // 1000,
                ),
                text=text,
            )
            subs.append(item)

        subs.save(srt_path, encoding="utf-8")
        print(f"Subtitles saved to {srt_path}")

        # Burn subtitles into video
        print(f"Adding subtitles to video...")
        subtitle_cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,Bold=1,Alignment=2'",
            "-c:a",
            "copy",
            output_path,
            "-y",
        ]

        subprocess.run(subtitle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Clean up temporary files
        os.remove(audio_path)

        print(f"Video with subtitles created: {output_path}")
        return output_path

    def transcribe_video(self, video_path, output_format="srt", model_size="base"):
        """Transcribe a video using OpenAI's Whisper and save as SRT or text file.

        Args:
            video_path (str): Path to the video
            output_format (str): Output format ('srt' or 'txt')
            model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')

        Returns:
            str: Path to the transcript file
        """
        try:
            import whisper
            import pysrt
            from datetime import timedelta
        except ImportError:
            print("Error: Required packages not installed.")
            print("Please install them with: pip install openai-whisper torch pysrt")
            return None

        # Extract audio from video
        audio_path = os.path.join(
            self.output_dir, f"{os.path.basename(video_path)}_audio.wav"
        )
        extract_cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-q:a",
            "0",
            "-map",
            "a",
            "-f",
            "wav",
            audio_path,
            "-y",
        ]

        print(f"Extracting audio from video...")
        subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Load Whisper model
        print(f"Loading Whisper {model_size} model...")
        model = whisper.load_model(model_size)

        # Transcribe audio
        print(f"Transcribing audio with Whisper...")
        result = model.transcribe(audio_path, fp16=False)

        base_name = os.path.splitext(os.path.basename(video_path))[0]

        if output_format.lower() == "srt":
            # Create SRT file
            output_path = os.path.join(self.output_dir, f"{base_name}.srt")
            subs = pysrt.SubRipFile()

            for i, segment in enumerate(result["segments"]):
                start = timedelta(seconds=segment["start"])
                end = timedelta(seconds=segment["end"])
                text = segment["text"].strip()

                item = pysrt.SubRipItem(
                    index=i + 1,
                    start=pysrt.SubRipTime(
                        hours=start.seconds // 3600,
                        minutes=(start.seconds // 60) % 60,
                        seconds=start.seconds % 60,
                        milliseconds=start.microseconds // 1000,
                    ),
                    end=pysrt.SubRipTime(
                        hours=end.seconds // 3600,
                        minutes=(end.seconds // 60) % 60,
                        seconds=end.seconds % 60,
                        milliseconds=end.microseconds // 1000,
                    ),
                    text=text,
                )
                subs.append(item)

            subs.save(output_path, encoding="utf-8")
        else:
            # Create plain text file
            output_path = os.path.join(self.output_dir, f"{base_name}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["text"])

        # Clean up temporary files
        os.remove(audio_path)

        print(f"Transcript saved to {output_path}")
        return output_path

    def add_text_overlay(self, video_path, text, position="bottom", output_path=None):
        """Add text overlay to a video.

        Args:
            video_path (str): Path to the video
            text (str): Text to overlay
            position (str): Position of the text (top, bottom, center)
            output_path (str, optional): Path to save the video with text overlay

        Returns:
            str: Path to the video with text overlay
        """
        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_text{ext}")

        # Set position coordinates
        position_map = {
            "top": "x=(w-text_w)/2:y=h*0.1",
            "center": "x=(w-text_w)/2:y=(h-text_h)/2",
            "bottom": "x=(w-text_w)/2:y=h*0.9",
        }

        pos = position_map.get(position, position_map["bottom"])

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"drawtext=text='{text}':fontsize=24:fontcolor=white:bordercolor=black:borderw=2:{pos}",
            "-c:a",
            "copy",
            output_path,
            "-y",
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path

    def crop_for_social(self, video_path, format="portrait", output_path=None):
        """Crop video for social media platforms.

        Args:
            video_path (str): Path to the video
            format (str): Target format (portrait, square, landscape)
            output_path (str, optional): Path to save the cropped video

        Returns:
            str: Path to the cropped video
        """
        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_{format}{ext}")

        # Define crop parameters for different formats
        format_map = {
            "portrait": "crop=ih*9/16:ih:iw/2-ih*9/32:0",  # 9:16 ratio (centered)
            "square": "crop=ih:ih:iw/2-ih/2:0",  # 1:1 ratio (centered)
            "landscape": "crop=iw:iw*9/16:0:ih/2-iw*9/32",  # 16:9 ratio (centered)
        }

        crop_filter = format_map.get(format, format_map["portrait"])

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            crop_filter,
            "-c:a",
            "copy",
            output_path,
            "-y",
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path

    def generate_random_clip(self, video_path, clip_duration=15, output_path=None):
        """Generate a random clip from a video.

        Args:
            video_path (str): Path to the source video
            clip_duration (int): Duration of the clip in seconds
            output_path (str, optional): Path to save the clip

        Returns:
            str: Path to the generated clip
        """
        # Get video duration
        duration = self.get_video_duration(video_path)

        # Calculate maximum start time
        max_start = max(0, duration - clip_duration)

        # Generate random start time
        start_time = random.uniform(0, max_start)

        # Extract the clip
        return self.extract_clip(video_path, start_time, clip_duration, output_path)

    def create_viral_clip(
        self,
        video_source,
        clip_duration=15,
        add_subs=True,
        add_text=True,
        format="portrait",
    ):
        """Create a viral-ready clip from a video source.

        Args:
            video_source (str): URL or path to the source video
            clip_duration (int): Duration of the clip in seconds
            add_subs (bool): Whether to add subtitles
            add_text (bool): Whether to add text overlay
            format (str): Target format (portrait, square, landscape)

        Returns:
            str: Path to the final viral clip
        """
        # Download the video if it's a URL
        if video_source.startswith(("http://", "https://")):
            video_path = self.download_video(video_source)
        else:
            video_path = video_source

        # Extract a random clip
        clip_path = self.generate_random_clip(video_path, clip_duration)

        # Process the clip
        processed_path = clip_path

        # Add subtitles if requested
        if add_subs:
            processed_path = self.add_subtitles(processed_path)

        # Add text overlay if requested
        if add_text:
            processed_path = self.add_text_overlay(
                processed_path, "Follow for more content like this!", "bottom"
            )

        # Crop for social media
        final_path = self.crop_for_social(processed_path, format)

        return final_path
