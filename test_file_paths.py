#!/usr/bin/env python3
"""
Test file paths for images
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
from file_processor.models import ConvertedImage

def test_file_paths():
    """Test file paths for converted images"""
    print("=== File Path Test ===")
    print(f"BASE_DIR: {settings.BASE_DIR}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"Current working directory: {os.getcwd()}")
    
    images = ConvertedImage.objects.all()[:5]  # Test first 5 images
    
    if not images:
        print("❌ No images found in database")
        return False
    
    print(f"\nTesting {len(images)} images:")
    
    for image in images:
        print(f"\n--- Image: {image} ---")
        print(f"image.image_file.name: {image.image_file.name}")
        print(f"image.image_file.path: {image.image_file.path}")
        
        # Test different path constructions
        paths_to_test = [
            image.image_file.path,  # Django's default
            os.path.join(settings.MEDIA_ROOT, image.image_file.name),  # Manual construction
            os.path.join(settings.BASE_DIR, 'media', image.image_file.name),  # Alternative
            os.path.abspath(image.image_file.path),  # Absolute path
        ]
        
        for i, path in enumerate(paths_to_test):
            exists = os.path.exists(path)
            print(f"Path {i+1}: {path} - {'✅' if exists else '❌'}")
            if exists:
                size = os.path.getsize(path)
                print(f"  File size: {size} bytes")
                break
        else:
            print("❌ No valid path found for this image!")
            
            # List actual files in media directory
            media_dir = settings.MEDIA_ROOT
            if os.path.exists(media_dir):
                print(f"Files in {media_dir}:")
                for root, dirs, files in os.walk(media_dir):
                    for file in files[:10]:  # Limit to first 10 files
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, media_dir)
                        print(f"  {rel_path}")
    
    return True

if __name__ == "__main__":
    test_file_paths()