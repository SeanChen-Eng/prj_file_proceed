import os
import requests
from django.conf import settings
from .models import ImageAnalysis, AnalysisResult

class DifyAPIService:
    def __init__(self):
        self.api_key = settings.DIFY_API_KEY
        self.user = settings.DIFY_USER
        self.server = settings.DIFY_SERVER
        # timeout for requests to Dify (seconds)
        self.timeout = int(os.getenv('DIFY_TIMEOUT', '60'))
    
    def upload_image(self, image_path):
        """Upload image to Dify and return file_id"""
        url = f'{self.server}/v1/files/upload'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        print(f"Uploading file: {image_path}")
        print(f"File exists: {os.path.exists(image_path)}")
        
        if not os.path.exists(image_path):
            raise Exception(f"File not found: {image_path}")
        
        file_size = os.path.getsize(image_path)
        print(f"File size: {file_size} bytes")
        
        ext = os.path.splitext(image_path)[-1].lower()
        mime = 'image/png' if ext == '.png' else 'image/jpeg'
        print(f"File extension: {ext}, MIME type: {mime}")
        
        try:
            with open(image_path, 'rb') as file:
                files = {'file': (os.path.basename(image_path), file, mime)}
                data = {'user': self.user}
                print(f"Sending request to: {url}")
                response = requests.post(url, headers=headers, files=files, data=data, timeout=self.timeout)

            print(f"Upload response status: {response.status_code}")
            if response.status_code == 201:
                file_id = response.json().get('id')
                print(f"Upload successful, file_id: {file_id}")
                return file_id
            else:
                print(f"Upload failed response: {response.text}")
                raise Exception(f"Upload failed: {response.status_code} - {response.text}")
        except FileNotFoundError:
            raise Exception(f"File not found: {image_path}")
        except PermissionError:
            raise Exception(f"Permission denied accessing file: {image_path}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Upload request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error uploading file: {str(e)}")
    
    def run_workflow(self, file_id, max_retries=3):
        """Run Dify workflow and return analysis result with retry mechanism"""
        url = f"{self.server}/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Try different input formats
        data_formats = [
            # Format 1: Original format
            {
                "inputs": {
                    "upload": {
                        "type": "image",
                        "transfer_method": "local_file",
                        "upload_file_id": file_id
                    }
                },
                "user": self.user,
                "response_mode": "blocking"
            },
            # Format 2: Simplified format
            {
                "inputs": {
                    "image": file_id
                },
                "user": self.user,
                "response_mode": "blocking"
            },
            # Format 3: Direct file_id
            {
                "inputs": {
                    "file_id": file_id
                },
                "user": self.user,
                "response_mode": "blocking"
            }
        ]
        
        data = data_formats[0]  # Start with original format
        
        for attempt in range(max_retries):
            try:
                print(f"Workflow attempt {attempt + 1}/{max_retries}")
                response = requests.post(url, headers=headers, json=data, timeout=self.timeout)

                if response.status_code == 200:
                    resp_json = response.json()
                    wf_status = resp_json.get("data", {}).get("status")
                    if wf_status == "succeeded":
                        outputs = resp_json.get("data", {}).get("outputs", {})
                        return True, outputs.get("result", {}), ""
                    else:
                        error_info = resp_json.get("data", {}).get("error") or resp_json.get("message")
                        if attempt < max_retries - 1 and "internal_server_error" in str(error_info).lower():
                            print(f"Server error, retrying in 5 seconds...")
                            import time
                            time.sleep(5)
                            continue
                        return False, {}, error_info
                elif response.status_code == 500:
                    # Server error - retry
                    if attempt < max_retries - 1:
                        print(f"Server 500 error, retrying in 5 seconds...")
                        import time
                        time.sleep(5)
                        continue
                    return False, {}, f"Dify server error after {max_retries} attempts: {response.text}"
                else:
                    # Other errors - don't retry
                    return False, {}, f"Workflow failed: {response.status_code} - {response.text}"
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Request failed, retrying in 5 seconds: {str(e)}")
                    import time
                    time.sleep(5)
                    continue
                return False, {}, f"Workflow request failed after {max_retries} attempts: {str(e)}"
        
        return False, {}, "Max retries exceeded"
    
    def analyze_images(self, analysis_id):
        """Analyze multiple images for a given analysis"""
        try:
            analysis = ImageAnalysis.objects.get(id=analysis_id)
            analysis.status = 'processing'
            analysis.save()
            
            print(f"Starting analysis for {analysis.images.count()} images")
            print(f"Dify API Key: {self.api_key[:10]}..." if self.api_key else "No API Key")
            print(f"Dify Server: {self.server}")
            print(f"Dify User: {self.user}")
            
            for image in analysis.images.all():
                try:
                    file_path = image.image_file.path
                    print(f"Processing image: {file_path}")
                    
                    # Verify file exists
                    if not os.path.exists(file_path):
                        raise Exception(f"Image file not found: {file_path}")
                    
                    # Upload image to Dify
                    print(f"Uploading image to Dify...")
                    file_id = self.upload_image(file_path)
                    print(f"Upload successful, file_id: {file_id}")
                    
                    # Run workflow
                    print(f"Running workflow...")
                    success, result_data, error_msg = self.run_workflow(file_id)
                    
                    if success:
                        print(f"Workflow successful")
                        # Save result to database
                        AnalysisResult.objects.create(
                            analysis=analysis,
                            image=image,
                            result_data=result_data
                        )
                    else:
                        print(f"Workflow failed: {error_msg}")
                        # Create user-friendly error message
                        if "internal_server_error" in error_msg.lower() or "500" in error_msg:
                            friendly_error = {
                                "error": "AI Analysis Service Configuration Issue",
                                "message": "The Dify workflow has a configuration problem that needs to be fixed.",
                                "technical_details": error_msg,
                                "suggestions": [
                                    "Check Dify workflow configuration in the dashboard",
                                    "Verify all workflow nodes are properly connected",
                                    "Ensure the workflow input parameter matches 'upload' or 'image'",
                                    "Test the workflow manually in Dify dashboard first"
                                ],
                                "status": "workflow_error"
                            }
                        else:
                            friendly_error = {
                                "error": "Analysis failed",
                                "technical_details": error_msg,
                                "suggestion": "Please check if the image contains a valid Chinese e-invoice.",
                                "status": "analysis_error"
                            }
                        
                        # Save error result
                        AnalysisResult.objects.create(
                            analysis=analysis,
                            image=image,
                            result_data=friendly_error
                        )
                
                except Exception as e:
                    print(f"Exception processing image {image}: {str(e)}")
                    # Save exception result
                    AnalysisResult.objects.create(
                        analysis=analysis,
                        image=image,
                        result_data={"error": str(e)}
                    )
            
            analysis.status = 'completed'
            analysis.save()
            print(f"Analysis completed")
            
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            try:
                analysis.status = 'failed'
                analysis.save()
            except:
                pass