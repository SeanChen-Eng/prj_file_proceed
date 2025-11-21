#!/usr/bin/env python3
"""
Test single image upload and analysis with Dify
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

from file_processor.models import ConvertedImage
from file_processor.services import DifyAPIService

def test_single_image():
    """Test uploading and analyzing a single image"""
    print("=== Single Image Test ===")
    
    # Get the first available image
    image = ConvertedImage.objects.first()
    if not image:
        print("❌ No images found in database")
        return
    
    print(f"Testing image: {image}")
    print(f"File path: {image.image_file.path}")
    
    try:
        service = DifyAPIService()
        
        # Test upload
        print("\n1. Testing upload...")
        file_id = service.upload_image(image.image_file.path)
        print(f"✅ Upload successful: {file_id}")
        
        # Test workflow
        print("\n2. Testing workflow...")
        success, result_data, error_msg = service.run_workflow(file_id)
        
        if success:
            print("✅ Workflow successful!")
            print(f"Result: {result_data}")
        else:
            print(f"❌ Workflow failed: {error_msg}")
            
            # Try to get more details about the workflow
            print("\n3. Checking workflow configuration...")
            import requests
            
            # Try to get workflow info
            url = f"{service.server}/v1/workflows"
            headers = {'Authorization': f'Bearer {service.api_key}'}
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                print(f"Workflows endpoint response: {response.status_code}")
                if response.status_code == 200:
                    print(f"Available workflows: {response.json()}")
                else:
                    print(f"Workflows response: {response.text}")
            except Exception as e:
                print(f"Failed to get workflows: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_single_image()