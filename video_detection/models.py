from django.db import models
from django.contrib.auth.models import User
import json

class VideoDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_detections', default=1)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text='Upload video file')
    source_type = models.CharField(max_length=20, choices=[
        ('file', 'File Upload'),
        ('webcam', 'Browser Webcam'),
    ], default='file')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    total_frames = models.IntegerField(default=0)
    processed_frames = models.IntegerField(default=0)
    
    def __str__(self):
        if self.video_file:
            return f"Video: {self.video_file.name}"
        return f"Webcam Detection - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']

class DetectionResult(models.Model):
    video_detection = models.ForeignKey(VideoDetection, on_delete=models.CASCADE, related_name='results')
    frame_number = models.IntegerField()
    timestamp = models.FloatField(help_text='Timestamp in seconds')
    detections = models.JSONField(default=list, help_text='List of detected objects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Frame {self.frame_number} - {len(self.detections)} objects"
    
    def get_detection_summary(self):
        """Get summary of detected objects"""
        summary = {}
        for detection in self.detections:
            obj_class = detection.get('class', 'unknown')
            summary[obj_class] = summary.get(obj_class, 0) + 1
        return summary
    
    class Meta:
        ordering = ['frame_number']