import requests
import base64
import json
import os
from django.conf import settings
from .models import ImageAnalysis, AnalysisResult

class ZhipuVisionService:
    def __init__(self):
        self.api_key = os.getenv('ZHIPU_API_KEY')
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
    def _encode_image_to_base64(self, image_path):
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _get_system_prompt(self):
        """Load system prompt from file"""
        prompt_file = os.path.join(settings.BASE_DIR, 'vision_model_system_prompt.txt')
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return """你是一个专业的发票信息提取助手。请从图片中提取发票信息，并以JSON格式输出。"""
    
    def analyze_single_image(self, image_path):
        """Analyze single invoice image using ZHIPU AI GLM-4V"""
        try:
            # Encode image to base64
            base64_image = self._encode_image_to_base64(image_path)
            
            # Prepare request payload
            payload = {
                "model": "glm-4v-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{self._get_system_prompt()}\n\n请分析这张发票图片，提取所有关键信息并按照指定的JSON格式输出。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response (in case there's extra text)
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    parsed_data = json.loads(json_str)
                else:
                    parsed_data = {"raw_response": content, "error": "No valid JSON found"}
            except json.JSONDecodeError:
                parsed_data = {"raw_response": content, "error": "JSON parsing failed"}
            
            return {
                'success': True,
                'data': parsed_data,
                'raw_response': content
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    def analyze_images(self, analysis_id):
        """Analyze multiple images for an ImageAnalysis"""
        try:
            analysis = ImageAnalysis.objects.get(id=analysis_id)
            analysis.status = 'processing'
            analysis.save()
            
            images = analysis.images.all()
            
            for image in images:
                result = self.analyze_single_image(image.image_file.path)
                
                # Save result
                AnalysisResult.objects.create(
                    analysis=analysis,
                    image=image,
                    result_data=result
                )
            
            analysis.status = 'completed'
            analysis.save()
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.save()
            print(f"ZHIPU Vision analysis failed: {str(e)}")