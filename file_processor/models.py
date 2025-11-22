from django.db import models
from django.contrib.auth.models import User
import os
import json

class PDFConversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_conversions', default=1)
    pdf_file = models.FileField(upload_to='pdfs/', help_text='Upload PDF file')
    created_at = models.DateTimeField(auto_now_add=True)
    total_pages = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    ocr_text = models.JSONField(default=dict, blank=True, help_text='Extracted text from PDF pages')
    ocr_status = models.CharField(max_length=20, default='not_started', choices=[
        ('not_started', 'Not Started'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    
    def __str__(self):
        return f"PDF: {os.path.basename(self.pdf_file.name)}"
    
    class Meta:
        ordering = ['-created_at']

class ConvertedImage(models.Model):
    pdf_conversion = models.ForeignKey(PDFConversion, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to='images/')
    page_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Page {self.page_number} of {self.pdf_conversion}"
    
    class Meta:
        ordering = ['page_number']

class ImageAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_analyses', default=1)
    images = models.ManyToManyField(ConvertedImage, related_name='analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    analysis_type = models.CharField(max_length=20, default='dify', choices=[
        ('dify', 'Dify API'),
        ('zhipu', 'ZHIPU Vision'),
    ])
    
    def __str__(self):
        return f"Analysis by {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']

class AnalysisResult(models.Model):
    analysis = models.ForeignKey(ImageAnalysis, on_delete=models.CASCADE, related_name='results')
    image = models.ForeignKey(ConvertedImage, on_delete=models.CASCADE)
    result_data = models.JSONField(default=dict, help_text='Dify API response data')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result for {self.image}"
    
    def get_formatted_result(self):
        return json.dumps(self.result_data, indent=2, ensure_ascii=False)
    
    class Meta:
        ordering = ['image__page_number']
