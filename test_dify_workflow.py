#!/usr/bin/env python3
"""
Test Dify workflow specifically
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
import requests

def test_dify_workflow():
    """Test Dify workflow with a simple image"""
    print("=== Dify Workflow Test ===")
    
    # First, let's check if we can get workflow info
    try:
        # Try to get app info (this might give us more details)
        url = f"{settings.DIFY_SERVER}/v1/parameters"
        headers = {'Authorization': f'Bearer {settings.DIFY_API_KEY}'}
        
        print(f"Testing app parameters: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Parameters response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ App is accessible")
            data = response.json()
            print(f"App data: {data}")
        else:
            print(f"❌ App parameters failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Parameters test failed: {str(e)}")
    
    # Test workflow with minimal data
    try:
        url = f"{settings.DIFY_SERVER}/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {settings.DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try without file first to see what error we get
        data = {
            "inputs": {},
            "user": settings.DIFY_USER,
            "response_mode": "blocking"
        }
        
        print(f"Testing workflow without inputs: {url}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Workflow response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            resp_json = response.json()
            print(f"Workflow status: {resp_json.get('data', {}).get('status')}")
        
    except Exception as e:
        print(f"❌ Workflow test failed: {str(e)}")

if __name__ == "__main__":
    test_dify_workflow()