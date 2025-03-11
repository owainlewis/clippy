# Makefile for Clippy (macOS optimized)

# Default output directory (can be overridden via command line)
OUTPUT_DIR = output_clips

# Default targets
.PHONY: all clean help convert install setup

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

# Create virtual environment and install dependencies using uv
setup:
	@echo "Setting up environment with uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "uv is not installed. Please install uv first:"; \
		echo "curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Virtual environment is already active at: $$VIRTUAL_ENV"; \
		echo "Installing dependencies with uv..."; \
		uv pip install -r requirements.txt; \
		echo "Setup complete!"; \
	else \
		echo "Creating virtual environment..."; \
		uv venv; \
		echo "Installing dependencies with uv..."; \
		. .venv/bin/activate && uv pip install -r requirements.txt; \
		echo ""; \
		echo "Creating activation script..."; \
		echo '#!/bin/bash' > activate_env.sh; \
		echo 'source .venv/bin/activate' >> activate_env.sh; \
		echo 'echo "Virtual environment activated! You can now run: python clippy.py [arguments]"' >> activate_env.sh; \
		chmod +x activate_env.sh; \
		echo ""; \
		echo "Setup complete! To activate the virtual environment, run:"; \
		echo "source ./activate_env.sh"; \
		echo ""; \
		echo "This will activate the environment in your current shell."; \
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
		echo "Please download a video first using: python3 clippy.py URL --download-only"; \
		exit 1; \
	else \
		echo "Found source file: $$SOURCE_FILE"; \
		ffmpeg -i "$$SOURCE_FILE" "$(OUTPUT_DIR)/source_video.mp4" -y; \
		if [ "$$SOURCE_FILE" != "$(OUTPUT_DIR)/source_video.mp4" ]; then \
			rm -f "$$SOURCE_FILE"; \
			echo "Removed original file: $$SOURCE_FILE"; \
		fi; \
	fi

# Download a video without processing
download: check-ffmpeg
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL parameter is required. Usage: make download URL=https://www.youtube.com/watch?v=VIDEO_ID"; \
		exit 1; \
	else \
		echo "Downloading video from: $(URL)"; \
		python3 clippy.py "$(URL)" --download-only --output-dir="$(OUTPUT_DIR)"; \
	fi

# All-in-one command: clean, download, and convert
video:
	@if [ -z "$(VIDEO_URL)" ]; then \
		echo "Error: VIDEO_URL parameter is required. Usage: make video VIDEO_URL=https://www.youtube.com/watch?v=VIDEO_ID"; \
		exit 1; \
	else \
		echo "=== Step 1: Cleaning output directory ==="; \
		$(MAKE) clean; \
		echo ""; \
		echo "=== Step 2: Downloading video ==="; \
		python3 clippy.py "$(VIDEO_URL)" --download-only --output-dir="$(OUTPUT_DIR)"; \
		echo ""; \
		echo "=== Step 3: Converting to MP4 ==="; \
		$(MAKE) convert; \
		echo ""; \
		echo "=== Process complete! ==="; \
		echo "Your video is available at: $(OUTPUT_DIR)/source_video.mp4"; \
	fi

# Create a clip with time range
clip: check-ffmpeg
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL parameter is required."; \
		echo "Usage: make clip URL=https://www.youtube.com/watch?v=VIDEO_ID"