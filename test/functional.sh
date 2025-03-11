#!/bin/bash

# Functional test script for Clippy
# This script downloads a video and generates a text transcription

# Set variables
VIDEO_URL="https://www.youtube.com/watch?v=_ZS8wqwKouI"
OUTPUT_DIR="test_output"
WHISPER_MODEL="base"  # Options: tiny, base, small, medium, large

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Print test information
echo "=== Clippy Functional Test ==="
echo "Video URL: $VIDEO_URL"
echo "Output Directory: $OUTPUT_DIR"
echo "Whisper Model: $WHISPER_MODEL"
echo "=========================="

# Activate virtual environment if it exists and not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "Warning: No virtual environment found. Using system Python."
    fi
fi

# Run the transcription
echo "Starting video download and transcription..."
python clippy.py "$VIDEO_URL" --transcribe --transcribe-format txt --whisper-model $WHISPER_MODEL --output-dir $OUTPUT_DIR

# Check if transcription was successful
if [ $? -eq 0 ]; then
    echo "=== Test Completed Successfully ==="
    
    # Find the transcription file
    TRANSCRIPT_FILE=$(find $OUTPUT_DIR -name "*.txt" -type f -print -quit)
    
    if [ -n "$TRANSCRIPT_FILE" ]; then
        echo "Transcription file created: $TRANSCRIPT_FILE"
        echo "First 10 lines of transcription:"
        head -n 10 "$TRANSCRIPT_FILE"
    else
        echo "Warning: Transcription file not found."
    fi
else
    echo "=== Test Failed ==="
    exit 1
fi

# Clean up (optional, commented out by default)
# echo "Cleaning up..."
# rm -rf $OUTPUT_DIR

echo "Test completed."
exit 0
