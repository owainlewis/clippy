#!/usr/bin/env python3
"""
Basic test script for the Clippy FastAPI implementation.
This tests the API endpoints without requiring heavy dependencies.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that we can import the basic modules."""
    print("Testing imports...")
    
    try:
        from clippy.models import (
            VideoProcessRequest, TranscribeRequest, DownloadRequest,
            ProcessResponse, TaskStatus, UploadResponse
        )
        print("✓ Models import successfully")
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False
    
    try:
        # Test basic model creation
        request = VideoProcessRequest(
            source="test_video.mp4",
            duration=30,
            format="portrait"
        )
        print("✓ VideoProcessRequest model works")
    except Exception as e:
        print(f"✗ Failed to create VideoProcessRequest: {e}")
        return False
    
    return True

def test_api_creation():
    """Test that we can create the FastAPI app."""
    print("Testing API creation...")
    
    try:
        # Set a temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['CLIPPY_OUTPUT_DIR'] = temp_dir
            
            from clippy.api import app
            print("✓ FastAPI app created successfully")
            
            # Test that we have the expected endpoints
            routes = [route.path for route in app.routes]
            expected_routes = [
                "/", "/health", "/upload", "/process", 
                "/transcribe", "/download", "/tasks/{task_id}"
            ]
            
            for route in expected_routes:
                if route in routes or any(r.startswith(route.split('{')[0]) for r in routes):
                    print(f"✓ Route {route} found")
                else:
                    print(f"✗ Route {route} missing")
                    return False
            
            return True
            
    except ImportError as e:
        print(f"✗ Failed to import API: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to create API: {e}")
        return False

def test_server_module():
    """Test that the server module can be imported."""
    print("Testing server module...")
    
    try:
        from clippy.server import main
        print("✓ Server module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import server module: {e}")
        return False

def test_cli_compatibility():
    """Test that the original CLI still works."""
    print("Testing CLI compatibility...")
    
    try:
        from clippy.cli import main as cli_main
        print("✓ CLI module still importable")
        return True
    except ImportError as e:
        print(f"✗ Failed to import CLI: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Clippy FastAPI Implementation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_api_creation,
        test_server_module,
        test_cli_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{test.__name__}:")
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
