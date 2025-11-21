#!/usr/bin/env python3
"""
Debug Dify API calls with different formats
"""
import os
import sys
import django
from pathlib import Path
import requests
import json

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_file_proceed.settings')
django.setup()

from django.conf import settings
from file_processor.models import ConvertedImage

def test_different_formats():
    """Test different API call formats"""
    print("=== Dify API Format Testing ===")
    
    # Get an image and upload it first
    image = ConvertedImage.objects.first()
    if not image:
        print("❌ No images found")
        return
    
    # Upload the image
    url = f'{settings.DIFY_SERVER}/v1/files/upload'
    headers = {'Authorization': f'Bearer {settings.DIFY_API_KEY}'}
    
    with open(image.image_file.path, 'rb') as file:
        files = {'file': (os.path.basename(image.image_file.path), file, 'image/png')}
        data = {'user': settings.DIFY_USER}
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.text}")
        return
    
    file_id = response.json().get('id')
    print(f"✅ Upload successful: {file_id}")
    
    # Test different workflow formats
    workflow_url = f"{settings.DIFY_SERVER}/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    formats = [
        {
            "name": "Format 1: Original upload structure",
            "data": {
                "inputs": {
                    "upload": {
                        "type": "image",
                        "transfer_method": "local_file",
                        "upload_file_id": file_id
                    }
                },
                "user": settings.DIFY_USER,
                "response_mode": "blocking"
            }
        },
        {
            "name": "Format 2: Simple image input",
            "data": {
                "inputs": {
                    "image": file_id
                },
                "user": settings.DIFY_USER,
                "response_mode": "blocking"
            }
        },
        {
            "name": "Format 3: File ID input",
            "data": {
                "inputs": {
                    "file_id": file_id
                },
                "user": settings.DIFY_USER,
                "response_mode": "blocking"
            }
        },
        {
            "name": "Format 4: Empty inputs",
            "data": {
                "inputs": {},
                "user": settings.DIFY_USER,
                "response_mode": "blocking"
            }
        }
    ]
    
    for fmt in formats:
        print(f"\n--- Testing {fmt['name']} ---")
        print(f"Data: {json.dumps(fmt['data'], indent=2)}")
        
        try:
            response = requests.post(workflow_url, headers=headers, json=fmt['data'], timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                resp_json = response.json()
                status = resp_json.get("data", {}).get("status")
                print(f"✅ Workflow status: {status}")
                if status == "succeeded":
                    print("🎉 SUCCESS! This format works!")
                    break
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def check_app_info():
    """Check app information and available endpoints"""
    print("\n=== App Information ===")
    
    # Try different endpoints to understand the app structure
    endpoints = [
        "/v1/parameters",
        "/v1/meta",
        "/v1/info",
        "/v1/app",
        "/v1/workflows",
        "/v1/chat-messages"  # Maybe it's a chat app, not workflow?
    ]
    
    for endpoint in endpoints:
        url = f"{settings.DIFY_SERVER}{endpoint}"
        headers = {'Authorization': f'Bearer {settings.DIFY_API_KEY}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {response.text[:200]}...")
        except Exception as e:
            print(f"{endpoint}: Error - {str(e)}")

if __name__ == "__main__":
    check_app_info()
    test_different_formats()