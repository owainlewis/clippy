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
            output_path = os.path.join(self.output_dir, "source_video.mp4")
            
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': output_path,
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        return output_path
    
    def get_video_duration(self, video_path):
        """Get the duration of a video file.
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            float: Duration of the video in seconds
        """
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            video_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
            "-i", video_path,
            "-ss", str(timedelta(seconds=start_time)),
            "-t", str(timedelta(seconds=duration)),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path,
            "-y"  # Overwrite if file exists
        ]
        
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    
    def add_subtitles(self, video_path, output_path=None):
        """Add subtitles to a video using speech recognition.
        
        Args:
            video_path (str): Path to the video
            output_path (str, optional): Path to save the video with subtitles
            
        Returns:
            str: Path to the video with subtitles
        """
        # For this function you'll need to install additional libraries:
        # pip install vosk or whisper for speech recognition
        # This is a placeholder - implement speech-to-text and subtitle burning as needed
        
        # Example implementation with whisper:
        # 1. Extract audio
        # 2. Transcribe audio with timestamps
        # 3. Create SRT file
        # 4. Burn subtitles into video
        
        if output_path is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(self.output_dir, f"{base}_subtitled{ext}")
            
        # Placeholder: just copy the file for now
        cmd = ["cp", video_path, output_path]
        subprocess.run(cmd)
        
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
            "bottom": "x=(w-text_w)/2:y=h*0.9"
        }
        
        pos = position_map.get(position, position_map["bottom"])
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"drawtext=text='{text}':fontsize=24:fontcolor=white:bordercolor=black:borderw=2:{pos}",
            "-c:a", "copy",
            output_path,
            "-y"
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
            "landscape": "crop=iw:iw*9/16:0:ih/2-iw*9/32"  # 16:9 ratio (centered)
        }
        
        crop_filter = format_map.get(format, format_map["portrait"])
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", crop_filter,
            "-c:a", "copy",
            output_path,
            "-y"
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
    
    def create_viral_clip(self, video_source, clip_duration=15, add_subs=True, 
                         add_text=True, format="portrait"):
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
                processed_path, 
                "Follow for more content like this!",
                "bottom"
            )
        
        # Crop for social media
        final_path = self.crop_for_social(processed_path, format)
        
        return final_path


def main():
    parser = argparse.ArgumentParser(description="Generate viral clips from videos")
    parser.add_argument("source", help="URL or path to the source video")
    parser.add_argument("--duration", type=int, default=15, help="Duration of the clip in seconds")
    parser.add_argument("--format", choices=["portrait", "square", "landscape"], default="portrait", 
                        help="Output format for social media")
    parser.add_argument("--no-subs", action="store_false", dest="add_subs", 
                        help="Disable subtitles")
    parser.add_argument("--no-text", action="store_false", dest="add_text", 
                        help="Disable text overlay")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    generator = ViralClipGenerator(output_dir=args.output_dir)
    
    final_path = generator.create_viral_clip(
        args.source,
        clip_duration=args.duration,
        add_subs=args.add_subs,
        add_text=args.add_text,
        format=args.format
    )
    
    print(f"Viral clip created successfully: {final_path}")


if __name__ == "__main__":
    main()