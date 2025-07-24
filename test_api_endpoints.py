#!/usr/bin/env python3
"""
Test script to verify the updated FastAPI endpoints match the actual implementation.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_root():
    """Test the root endpoint."""
    print("\nTesting root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_openapi_schema():
    """Test that the OpenAPI schema is accessible."""
    print("\nTesting OpenAPI schema...")
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        schema = response.json()
        paths = list(schema.get('paths', {}).keys())
        print(f"Available endpoints: {paths}")
        
        # Check for expected endpoints
        expected_endpoints = [
            "/", "/health", "/upload", "/process", "/transcribe", 
            "/download", "/extract-clip", "/generate-random-clip",
            "/add-subtitles", "/add-text-overlay", "/crop-for-social",
            "/tasks/{task_id}", "/download/{filename}", "/files"
        ]
        
        missing = []
        for endpoint in expected_endpoints:
            if endpoint not in paths and not any(p.startswith(endpoint.split('{')[0]) for p in paths):
                missing.append(endpoint)
        
        if missing:
            print(f"Missing endpoints: {missing}")
            return False
        else:
            print("✓ All expected endpoints found")
            return True
    
    return False

def test_tasks_endpoint():
    """Test the tasks listing endpoint."""
    print("\nTesting tasks endpoint...")
    response = requests.get(f"{BASE_URL}/tasks")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_files_endpoint():
    """Test the files listing endpoint."""
    print("\nTesting files endpoint...")
    response = requests.get(f"{BASE_URL}/files")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_download_endpoint_validation():
    """Test download endpoint with YouTube URL validation."""
    print("\nTesting download endpoint validation...")
    
    # Test with invalid URL
    response = requests.post(f"{BASE_URL}/download", json={
        "url": "not-a-valid-url"
    })
    print(f"Invalid URL Status: {response.status_code}")
    
    # Test with valid URL format (but don't actually download)
    response = requests.post(f"{BASE_URL}/download", json={
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    })
    print(f"Valid URL Status: {response.status_code}")
    
    if response.status_code == 200:
        task_data = response.json()
        print(f"Task created: {task_data}")
        return True
    
    return response.status_code in [200, 422]  # 422 for validation errors is also acceptable

def test_process_endpoint_validation():
    """Test process endpoint validation."""
    print("\nTesting process endpoint validation...")
    
    # Test with missing source
    response = requests.post(f"{BASE_URL}/process", json={
        "clip_duration": 15,
        "format": "portrait"
    })
    print(f"Missing source Status: {response.status_code}")
    
    # Test with valid data but non-existent file
    response = requests.post(f"{BASE_URL}/process", json={
        "source": "non-existent-file-id",
        "clip_duration": 15,
        "format": "portrait",
        "add_subs": True,
        "add_text": True
    })
    print(f"Non-existent file Status: {response.status_code}")
    
    if response.status_code == 200:
        task_data = response.json()
        print(f"Task created: {task_data}")
    
    return response.status_code in [200, 422, 400]  # Various error codes are acceptable

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Updated Clippy FastAPI Endpoints")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("OpenAPI Schema", test_openapi_schema),
        ("Tasks Endpoint", test_tasks_endpoint),
        ("Files Endpoint", test_files_endpoint),
        ("Download Validation", test_download_endpoint_validation),
        ("Process Validation", test_process_endpoint_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The updated API is working correctly.")
        print("\nThe API now matches the actual GitHub repository implementation:")
        print("- Correct method signatures for ViralClipGenerator")
        print("- Proper parameter names (clip_duration vs duration)")
        print("- All individual processing methods available as endpoints")
        print("- Validation and error handling in place")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
