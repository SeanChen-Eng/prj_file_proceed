from django.contrib import admin
from .models import VideoDetection, DetectionResult

class DetectionResultInline(admin.TabularInline):
    model = DetectionResult
    extra = 0
    readonly_fields = ('frame_number', 'timestamp', 'detections', 'created_at')

@admin.register(VideoDetection)
class VideoDetectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'source_type', 'status', 'total_frames', 'processed_frames', 'created_at')
    list_filter = ('source_type', 'status', 'created_at', 'user')
    readonly_fields = ('total_frames', 'processed_frames', 'status', 'created_at')
    inlines = [DetectionResultInline]

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'video_detection', 'frame_number', 'timestamp', 'created_at')
    list_filter = ('created_at', 'video_detection__user')
    readonly_fields = ('detections', 'created_at')