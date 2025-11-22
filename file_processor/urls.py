from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(next_page='/auth/login/'), name='logout'),
    path('auth/register/', views.register, name='register'),
    
    # PDF Conversion URLs
    path('pdf/upload/', views.upload_pdf, name='upload_pdf'),
    path('pdf/list/', views.conversion_list, name='conversion_list'),
    path('pdf/detail/<int:pk>/', views.conversion_detail, name='conversion_detail'),
    
    # Image Analysis URLs
    path('analysis/', views.image_analysis, name='image_analysis'),
    path('analysis/list/', views.analysis_list, name='analysis_list'),
    path('analysis/detail/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    
    # OCR URLs
    path('extract-text/<int:pk>/', views.extract_text, name='extract_text'),
    path('download-ocr/<int:pk>/', views.download_ocr_json, name='download_ocr_json'),
]