#!/usr/bin/env python3
"""
Simple startup script for Clippy FastAPI server.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set default output directory
output_dir = os.environ.get('CLIPPY_OUTPUT_DIR', 'api_output')
os.environ['CLIPPY_OUTPUT_DIR'] = output_dir

# Ensure output directory exists
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Update the API module with the output directory
from clippy import api
api.output_dir = output_dir

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.environ.get('CLIPPY_HOST', '127.0.0.1')
    port = int(os.environ.get('CLIPPY_PORT', '8000'))
    workers = int(os.environ.get('CLIPPY_WORKERS', '1'))
    log_level = os.environ.get('CLIPPY_LOG_LEVEL', 'info')
    reload = os.environ.get('CLIPPY_RELOAD', 'false').lower() == 'true'
    
    print(f"Starting Clippy API server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Output directory: {output_dir}")
    print(f"Workers: {workers}")
    print(f"Log level: {log_level}")
    print(f"Reload: {reload}")
    print(f"API docs will be available at: http://{host}:{port}/docs")
    
    # Start the server
    uvicorn.run(
        "clippy.api:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        log_level=log_level,
        reload=reload,
        access_log=True
    )
