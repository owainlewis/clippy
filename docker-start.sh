#!/bin/bash

# Docker startup script for Clippy API

# Set default values
export CLIPPY_HOST=${CLIPPY_HOST:-"0.0.0.0"}
export CLIPPY_PORT=${CLIPPY_PORT:-"8000"}
export CLIPPY_WORKERS=${CLIPPY_WORKERS:-"4"}
export CLIPPY_LOG_LEVEL=${CLIPPY_LOG_LEVEL:-"info"}
export CLIPPY_OUTPUT_DIR=${CLIPPY_OUTPUT_DIR:-"/app/output"}

# Create output directory
mkdir -p "$CLIPPY_OUTPUT_DIR"

# Start the server
exec python start_server.py
