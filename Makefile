# Makefile for Clippy (macOS optimized)

# Default output directory (can be overridden via command line)
OUTPUT_DIR = output_clips

# Default targets
.PHONY: all clean help convert install setup test server server-dev api-docs

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
		echo "Installing package in development mode..."; \
		pip install -e .; \
		echo "Setup complete!"; \
	else \
		echo "Creating virtual environment..."; \
		uv venv; \
		echo "Installing package in development mode..."; \
		. .venv/bin/activate && pip install -e .; \
		echo ""; \
		echo "Creating activation script..."; \
		echo '#!/bin/bash' > activate_env.sh; \
		echo 'source .venv/bin/activate' >> activate_env.sh; \
		echo 'echo "Virtual environment activated! You can now run: python -m clippy.cli [arguments]"' >> activate_env.sh; \
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
		echo "Please download a video first using: make download URL=..."; \
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
		if [ -n "$$VIRTUAL_ENV" ]; then \
			python -m clippy.cli "$(URL)" --download-only --output-dir="$(OUTPUT_DIR)"; \
		else \
			. .venv/bin/activate && python -m clippy.cli "$(URL)" --download-only --output-dir="$(OUTPUT_DIR)"; \
		fi; \
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
		if [ -n "$$VIRTUAL_ENV" ]; then \
			python -m clippy.cli "$(VIDEO_URL)" --download-only --output-dir="$(OUTPUT_DIR)"; \
		else \
			. .venv/bin/activate && python -m clippy.cli "$(VIDEO_URL)" --download-only --output-dir="$(OUTPUT_DIR)"; \
		fi; \
		echo ""; \
		echo "=== Step 3: Converting to MP4 ==="; \
		$(MAKE) convert; \
		echo ""; \
		echo "=== Process complete! ==="; \
		echo "Your video is available at: $(OUTPUT_DIR)/source_video.mp4"; \
	fi

# Run functional tests
test:
	@echo "Running functional tests..."
	@if [ -f "./test/functional.sh" ]; then \
		if [ -n "$$VIRTUAL_ENV" ]; then \
			./test/functional.sh; \
		else \
			. .venv/bin/activate && ./test/functional.sh; \
		fi; \
	else \
		echo "Error: Functional test script not found."; \
		exit 1; \
	fi

# Start the API server in development mode
server-dev:
	@echo "Starting Clippy API server in development mode..."
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		clippy-server --reload --host 0.0.0.0 --port 8000; \
	else \
		. .venv/bin/activate && clippy-server --reload --host 0.0.0.0 --port 8000; \
	fi

# Start the API server in production mode
server:
	@echo "Starting Clippy API server..."
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		clippy-server --host 0.0.0.0 --port 8000 --workers 4; \
	else \
		. .venv/bin/activate && clippy-server --host 0.0.0.0 --port 8000 --workers 4; \
	fi

# Open API documentation in browser
api-docs:
	@echo "Opening API documentation..."
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Please open http://localhost:8000/docs in your browser"

# Help target
help:
	@echo "Clippy - Video Processing Tool"
	@echo ""
	@echo "Available targets:"
	@echo "  make setup           - Set up the development environment"
	@echo "  make clean           - Clean the output directory"
	@echo "  make convert         - Convert downloaded video to MP4"
	@echo "  make download URL=   - Download a video"
	@echo "  make video VIDEO_URL=- Download and convert a video"
	@echo "  make test           - Run functional tests"
	@echo "  make server-dev      - Start API server in development mode"
	@echo "  make server          - Start API server in production mode"
	@echo "  make api-docs        - Open API documentation in browser"
	@echo ""
	@echo "CLI Examples:"
	@echo "  make video VIDEO_URL=https://www.youtube.com/watch?v=VIDEO_ID"
	@echo ""
	@echo "API Examples:"
	@echo "  make server-dev      # Start development server"
	@echo "  make api-docs        # View API documentation"