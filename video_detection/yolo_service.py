import base64
import json
from .models import VideoDetection, DetectionResult

class YOLODetectionService:
    def __init__(self):
        self.model = None
    
    def _load_model(self):
        """Lazy load YOLO model to avoid import errors during migration"""
        if self.model is None:
            try:
                import cv2
                import numpy as np
                from ultralytics import YOLO
                self.model = YOLO('yolov8n.pt')  # nano version for speed
                self.cv2 = cv2
                self.np = np
            except ImportError as e:
                raise ImportError(f"Required packages not installed: {e}")
        return self.model
        
    def detect_objects(self, frame):
        """Detect objects in a single frame"""
        model = self._load_model()
        results = model(frame)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names[class_id]
                    
                    detection = {
                        'class': class_name,
                        'confidence': float(confidence),
                        'bbox': [float(x1), float(y1), float(x2), float(y2)]
                    }
                    detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame, detections):
        """Draw detection boxes on frame"""
        self._load_model()  # Ensure cv2 is loaded
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Draw bounding box
            x1, y1, x2, y2 = map(int, bbox)
            self.cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            self.cv2.putText(frame, label, (x1, y1-10), self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def process_video_file(self, video_detection_id):
        """Process uploaded video file"""
        try:
            video_detection = VideoDetection.objects.get(id=video_detection_id)
            video_detection.status = 'processing'
            video_detection.save()
            
            self._load_model()  # Ensure cv2 is loaded
            
            cap = self.cv2.VideoCapture(video_detection.video_file.path)
            total_frames = int(cap.get(self.cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(self.cv2.CAP_PROP_FPS)
            
            video_detection.total_frames = total_frames
            video_detection.save()
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 5th frame for speed
                if frame_count % 5 == 0:
                    detections = self.detect_objects(frame)
                    timestamp = frame_count / fps
                    
                    # Save detection result
                    DetectionResult.objects.create(
                        video_detection=video_detection,
                        frame_number=frame_count,
                        timestamp=timestamp,
                        detections=detections
                    )
                
                frame_count += 1
                video_detection.processed_frames = frame_count
                video_detection.save()
            
            cap.release()
            
            # Delete video file after processing
            if video_detection.video_file:
                video_detection.video_file.delete()
            
            video_detection.status = 'completed'
            video_detection.save()
            
        except Exception as e:
            video_detection.status = 'failed'
            video_detection.save()
            print(f"Video processing failed: {str(e)}")
    
    def process_frame_base64(self, frame_data):
        """Process single frame from webcam (base64 encoded)"""
        try:
            self._load_model()  # Ensure cv2 and np are loaded
            
            # Decode base64 image
            img_data = base64.b64decode(frame_data.split(',')[1])
            nparr = self.np.frombuffer(img_data, self.np.uint8)
            frame = self.cv2.imdecode(nparr, self.cv2.IMREAD_COLOR)
            
            # Detect objects
            detections = self.detect_objects(frame)
            
            # Draw detections
            result_frame = self.draw_detections(frame.copy(), detections)
            
            # Encode result back to base64
            _, buffer = self.cv2.imencode('.jpg', result_frame)
            result_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'success': True,
                'result_image': f"data:image/jpeg;base64,{result_base64}",
                'detections': detections
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }