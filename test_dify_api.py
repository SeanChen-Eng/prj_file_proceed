#!/usr/bin/env python3
"""
Test script to verify Dify API connection
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_file_proceed.settings')
django.setup()

from django.conf import settings
from file_processor.services import DifyAPIService
import requests

def test_dify_connection():
    """Test basic Dify API connection"""
    print("=== Dify API Connection Test ===")
    
    # Check environment variables
    print(f"DIFY_API_KEY: {'✓' if settings.DIFY_API_KEY else '✗'}")
    print(f"DIFY_USER: {settings.DIFY_USER}")
    print(f"DIFY_SERVER: {settings.DIFY_SERVER}")
    
    if not settings.DIFY_API_KEY:
        print("❌ DIFY_API_KEY not found in environment variables")
        return False
    
    # Test basic API connectivity
    try:
        service = DifyAPIService()
        print(f"Service initialized with timeout: {service.timeout}s")
        
        # Test a simple API call (this might fail but will show connectivity)
        url = f"{settings.DIFY_SERVER}/v1/files/upload"
        headers = {'Authorization': f'Bearer {settings.DIFY_API_KEY}'}
        
        print(f"Testing connection to: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code in [200, 400, 401, 405]:  # Any response means connectivity is OK
            print("✅ Dify API is reachable")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_image_file_access():
    """Test if we can access image files"""
    print("\n=== Image File Access Test ===")
    
    from file_processor.models import ConvertedImage
    
    images = ConvertedImage.objects.all()[:3]  # Test first 3 images
    
    if not images:
        print("❌ No images found in database")
        return False
    
    for image in images:
        print(f"Testing image: {image}")
        print(f"File path: {image.image_file.path}")
        
        if os.path.exists(image.image_file.path):
            file_size = os.path.getsize(image.image_file.path)
            print(f"✅ File exists, size: {file_size} bytes")
        else:
            print(f"❌ File not found: {image.image_file.path}")
            return False
    
    return True

if __name__ == "__main__":
    print("Starting Dify API tests...\n")
    
    api_ok = test_dify_connection()
    files_ok = test_image_file_access()
    
    print(f"\n=== Test Results ===")
    print(f"API Connection: {'✅' if api_ok else '❌'}")
    print(f"File Access: {'✅' if files_ok else '❌'}")
    
    if api_ok and files_ok:
        print("\n🎉 All tests passed! Dify API should work.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")