from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VideoDetection, DetectionResult
from .forms import VideoUploadForm
from .yolo_service import YOLODetectionService
import threading
import json

@login_required
def video_detection_home(request):
    """Video detection main page"""
    # Get recent detections for current user
    if request.user.is_superuser:
        recent_detections = VideoDetection.objects.all()[:5]
    else:
        recent_detections = VideoDetection.objects.filter(user=request.user)[:5]
    
    return render(request, 'video_detection/home.html', {
        'recent_detections': recent_detections
    })

@login_required
def upload_video(request):
    """Upload video for detection"""
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_detection = form.save(commit=False)
            video_detection.user = request.user
            video_detection.source_type = 'file'
            video_detection.save()
            
            # Start processing in background
            yolo_service = YOLODetectionService()
            thread = threading.Thread(target=yolo_service.process_video_file, args=(video_detection.id,))
            thread.start()
            
            messages.success(request, 'Video uploaded and processing started!')
            return redirect('detection_detail', pk=video_detection.pk)
    else:
        form = VideoUploadForm()
    
    return render(request, 'video_detection/upload.html', {'form': form})

@login_required
def webcam_detection(request):
    """Real-time webcam detection page"""
    return render(request, 'video_detection/webcam.html')

@csrf_exempt
@login_required
def process_webcam_frame(request):
    """Process single frame from webcam"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            frame_data = data.get('frame')
            
            yolo_service = YOLODetectionService()
            result = yolo_service.process_frame_base64(frame_data)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def detection_detail(request, pk):
    """View detection results"""
    detection = get_object_or_404(VideoDetection, pk=pk)
    if not request.user.is_superuser and detection.user != request.user:
        messages.error(request, 'You can only view your own detections.')
        return redirect('detection_list')
    
    results = detection.results.all()
    
    # Calculate statistics
    total_detections = sum(len(result.detections) for result in results)
    object_summary = {}
    for result in results:
        for detection in result.detections:
            obj_class = detection.get('class', 'unknown')
            object_summary[obj_class] = object_summary.get(obj_class, 0) + 1
    
    return render(request, 'video_detection/detail.html', {
        'detection': detection,
        'results': results,
        'total_detections': total_detections,
        'object_summary': object_summary
    })

@login_required
def detection_list(request):
    """List all video detections"""
    if request.user.is_superuser:
        detections = VideoDetection.objects.all()
    else:
        detections = VideoDetection.objects.filter(user=request.user)
    
    return render(request, 'video_detection/list.html', {'detections': detections})