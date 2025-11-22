from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_detection_home, name='video_detection_home'),
    path('upload/', views.upload_video, name='upload_video'),
    path('webcam/', views.webcam_detection, name='webcam_detection'),
    path('process-frame/', views.process_webcam_frame, name='process_webcam_frame'),
    path('list/', views.detection_list, name='detection_list'),
    path('detail/<int:pk>/', views.detection_detail, name='detection_detail'),
]