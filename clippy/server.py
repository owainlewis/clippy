"""
Server startup script for Clippy FastAPI application.
"""

import argparse
import uvicorn
from pathlib import Path


def main():
    """Main entry point for the Clippy API server."""
    parser = argparse.ArgumentParser(description="Start the Clippy API server")
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--output-dir",
        default="api_output",
        help="Directory for storing processed files (default: api_output)"
    )
    
    args = parser.parse_args()
    
    # Set output directory and update the API module
    import os
    os.environ['CLIPPY_OUTPUT_DIR'] = args.output_dir

    # Update the output_dir in the API module
    from clippy import api
    api.output_dir = args.output_dir
    
    # Ensure output directory exists
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Clippy API server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Output directory: {args.output_dir}")
    print(f"Reload: {args.reload}")
    print(f"Workers: {args.workers}")
    print(f"Log level: {args.log_level}")
    print(f"API docs will be available at: http://{args.host}:{args.port}/docs")
    
    # Start the server
    uvicorn.run(
        "clippy.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,  # reload doesn't work with multiple workers
        log_level=args.log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
