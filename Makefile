# Makefile for ViralClipGenerator (macOS optimized)

# Default output directory (can be overridden via command line)
OUTPUT_DIR = output

# Default targets
.PHONY: all clean help convert

# Default target
all: help

# Clean the output directory
clean:
	@echo "Cleaning output directory: $(OUTPUT_DIR)"
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		rm -rf "$(OUTPUT_DIR)"/*; \
		echo "Directory cleaned successfully."; \
	else \
		echo "Directory $(OUTPUT_DIR) does not exist."; \
	fi

# Check for FFmpeg installation on macOS
check-ffmpeg:
	@if ! command -v ffmpeg >/dev/null 2>&1; then \
		echo "FFmpeg is not installed. Installing with Homebrew..."; \
		if ! command -v brew >/dev/null 2>&1; then \
			echo "Homebrew is not installed. Please install Homebrew first:"; \
			echo "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""; \
			exit 1; \
		fi; \
		brew install ffmpeg; \
	fi

# Convert the downloaded source video to MP4
convert: check-ffmpeg
	@echo "Converting source video to MP4..."
	@SOURCE_FILE=$$(find $(OUTPUT_DIR) -name "source_video*" | head -n 1); \
	if [ -z "$$SOURCE_FILE" ]; then \
		echo "Error: No source video found in $(OUTPUT_DIR) directory"; \
		echo "Please download a video first using: python3 main.py URL --download-only"; \
		exit 1; \
	else \
		echo "Found source file: $$SOURCE_FILE"; \
		ffmpeg -i "$$SOURCE_FILE" "$(OUTPUT_DIR)/source_video.mp4" -y; \
		if [ "$$SOURCE_FILE" != "$(OUTPUT_DIR)/source_video.mp4" ]; then \
			rm -f "$$SOURCE_FILE"; \
			echo "Removed original file: $$SOURCE_FILE"; \
		fi; \
	fi

# Show help
help:
	@echo "ViralClipGenerator Makefile (macOS Version)"
	@echo ""
	@echo "Available targets:"
	@echo "  clean              - Remove all files from the output directory"
	@echo "  convert            - Convert the downloaded source video to QuickTime-compatible MP4"
	@echo "  help               - Display this help message"
	@echo ""
	@echo "Usage pattern:"
	@echo "  1. python3 main.py URL --download-only"
	@echo "  2. make convert"
	@echo ""
	@echo "Variables:"
	@echo "  OUTPUT_DIR         - Output directory (default: '$(OUTPUT_DIR)')"
	@echo "                       Override with: make clean OUTPUT_DIR=my_directory"