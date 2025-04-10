import argparse
import os
from .generator import ViralClipGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate viral clips from videos")
    parser.add_argument("source", help="URL or path to the source video")
    parser.add_argument(
        "--duration", type=int, default=15, help="Duration of the clip in seconds"
    )
    parser.add_argument(
        "--format",
        choices=["portrait", "square", "landscape"],
        default="portrait",
        help="Output format for social media",
    )
    parser.add_argument(
        "--no-subs", action="store_false", dest="add_subs", help="Disable subtitles"
    )
    parser.add_argument(
        "--no-text", action="store_false", dest="add_text", help="Disable text overlay"
    )
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="Only download the video without creating clips",
    )
    parser.add_argument(
        "--output-filename",
        help="Custom filename for downloaded video (only used with --download-only)",
    )
    parser.add_argument(
        "--transcribe",
        action="store_true",
        help="Transcribe the video using Whisper (creates SRT file by default)",
    )
    parser.add_argument(
        "--transcribe-format",
        choices=["srt", "txt"],
        default="srt",
        help="Format for transcription output (only used with --transcribe)",
    )
    parser.add_argument(
        "--whisper-model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (larger = more accurate but slower)",
    )

    args = parser.parse_args()

    generator = ViralClipGenerator(output_dir=args.output_dir)

    # Handle download-only option
    if args.download_only:
        if not args.source.startswith(("http://", "https://")):
            print("Error: --download-only option requires a URL as the source")
            return

        output_path = None
        if args.output_filename:
            output_path = os.path.join(args.output_dir, args.output_filename)

        downloaded_path = generator.download_video(args.source, output_path)
        print(f"Video downloaded successfully: {downloaded_path}")
        return

    # Handle transcribe option
    if args.transcribe:
        # If it's a URL, download it first
        if args.source.startswith(("http://", "https://")):
            print("Downloading video first...")
            video_path = generator.download_video(args.source)
        else:
            video_path = args.source

        transcript_path = generator.transcribe_video(
            video_path,
            output_format=args.transcribe_format,
            model_size=args.whisper_model,
        )
        print(f"Transcription completed: {transcript_path}")
        return

    # Regular clip generation
    final_path = generator.create_viral_clip(
        args.source,
        clip_duration=args.duration,
        add_subs=args.add_subs,
        add_text=args.add_text,
        format=args.format,
    )

    print(f"Viral clip created successfully: {final_path}")


if __name__ == "__main__":
    main()
