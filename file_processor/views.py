from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from .models import PDFConversion, ConvertedImage, ImageAnalysis, AnalysisResult
from .forms import PDFUploadForm, CustomUserCreationForm, ImageSelectionForm
from .services import DifyAPIService
from .ocr_service import OCRService
import fitz  # PyMuPDF
import os
from django.conf import settings
import threading
import json

def home(request):
    return render(request, 'file_processor/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_conversion = form.save(commit=False)
            pdf_conversion.user = request.user
            pdf_conversion.save()
            # Start conversion in background
            thread = threading.Thread(target=convert_pdf_to_images, args=(pdf_conversion,))
            thread.start()
            messages.success(request, 'PDF uploaded and conversion started!')
            return redirect('conversion_detail', pk=pdf_conversion.pk)
    else:
        form = PDFUploadForm()
    
    return render(request, 'file_processor/upload.html', {'form': form})

@login_required
def conversion_detail(request, pk):
    conversion = get_object_or_404(PDFConversion, pk=pk)
    if not request.user.is_superuser and conversion.user != request.user:
        messages.error(request, 'You can only view your own conversions.')
        return redirect('conversion_list')
    
    images = conversion.images.all()
    
    # OCR summary if available
    ocr_summary = None
    if conversion.ocr_text:
        ocr_service = OCRService()
        ocr_summary = ocr_service.get_text_summary(conversion.ocr_text)
    
    return render(request, 'file_processor/conversion_detail.html', {
        'conversion': conversion,
        'images': images,
        'ocr_summary': ocr_summary
    })

@login_required
def conversion_list(request):
    if request.user.is_superuser:
        conversions = PDFConversion.objects.all()
    else:
        conversions = PDFConversion.objects.filter(user=request.user)
    return render(request, 'file_processor/conversion_list.html', {'conversions': conversions})

@login_required
def image_analysis(request):
    if request.method == 'POST':
        form = ImageSelectionForm(request.user, request.POST)
        if form.is_valid():
            selected_images = form.cleaned_data['selected_images']
            analysis_type = form.cleaned_data['analysis_type']
            
            # Create analysis record
            analysis = ImageAnalysis.objects.create(
                user=request.user,
                analysis_type=analysis_type
            )
            analysis.images.set(selected_images)
            
            # Start analysis in background based on selected type
            if analysis_type == 'zhipu':
                from .zhipu_service import ZhipuVisionService
                service = ZhipuVisionService()
            else:
                service = DifyAPIService()
            
            thread = threading.Thread(target=service.analyze_images, args=(analysis.id,))
            thread.start()
            
            model_name = 'ZHIPU Vision' if analysis_type == 'zhipu' else 'Dify API'
            messages.success(request, f'{model_name} analysis started for {selected_images.count()} images!')
            return redirect('analysis_detail', pk=analysis.pk)
    else:
        form = ImageSelectionForm(request.user)
    
    return render(request, 'file_processor/image_analysis.html', {'form': form})

@login_required
def analysis_detail(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if not request.user.is_superuser and analysis.user != request.user:
        messages.error(request, 'You can only view your own analyses.')
        return redirect('analysis_list')
    
    results = analysis.results.all()
    return render(request, 'file_processor/analysis_detail.html', {
        'analysis': analysis,
        'results': results
    })

@login_required
def analysis_list(request):
    if request.user.is_superuser:
        analyses = ImageAnalysis.objects.all()
    else:
        analyses = ImageAnalysis.objects.filter(user=request.user)
    return render(request, 'file_processor/analysis_list.html', {'analyses': analyses})

def convert_pdf_to_images(pdf_conversion):
    """Convert PDF to PNG images"""
    try:
        pdf_conversion.status = 'processing'
        pdf_conversion.save()
        
        # Open PDF file
        pdf_path = pdf_conversion.pdf_file.path
        pdf_document = fitz.open(pdf_path)
        pdf_conversion.total_pages = len(pdf_document)
        pdf_conversion.save()
        
        # Convert each page to PNG
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            
            # Save image
            img_name = f"{os.path.splitext(os.path.basename(pdf_conversion.pdf_file.name))[0]}_page_{page_num + 1}.png"
            img_path = os.path.join(settings.MEDIA_ROOT, 'images', img_name)
            
            # Ensure images directory exists
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            
            with open(img_path, 'wb') as f:
                f.write(img_data)
            
            # Create ConvertedImage record
            ConvertedImage.objects.create(
                pdf_conversion=pdf_conversion,
                image_file=f'images/{img_name}',
                page_number=page_num + 1
            )
        
        pdf_document.close()
        pdf_conversion.status = 'completed'
        pdf_conversion.save()
        
    except Exception as e:
        pdf_conversion.status = 'failed'
        pdf_conversion.save()
        print(f"Conversion failed: {str(e)}")

@login_required
def extract_text(request, pk):
    """Start OCR text extraction for a PDF"""
    conversion = get_object_or_404(PDFConversion, pk=pk)
    if not request.user.is_superuser and conversion.user != request.user:
        messages.error(request, 'You can only extract text from your own files.')
        return redirect('conversion_list')
    
    if conversion.status != 'completed':
        messages.error(request, 'PDF conversion must be completed first.')
        return redirect('conversion_detail', pk=pk)
    
    # Reset OCR status and clear previous results if retrying
    conversion.ocr_status = 'processing'
    conversion.ocr_text = {}
    conversion.save()
    
    # Start OCR in background
    ocr_service = OCRService()
    thread = threading.Thread(target=ocr_service.extract_text_from_pdf, args=(conversion.id,))
    thread.start()
    
    messages.success(request, 'Text extraction started!')
    return redirect('conversion_detail', pk=pk)

@login_required
def download_ocr_json(request, pk):
    """Download OCR results as JSON"""
    conversion = get_object_or_404(PDFConversion, pk=pk)
    if not request.user.is_superuser and conversion.user != request.user:
        messages.error(request, 'You can only download your own files.')
        return redirect('conversion_list')
    
    if not conversion.ocr_text:
        messages.error(request, 'No OCR text available. Please extract text first.')
        return redirect('conversion_detail', pk=pk)
    
    # Create JSON response
    response = JsonResponse(conversion.ocr_text, json_dumps_params={'indent': 2, 'ensure_ascii': False})
    filename = f"{os.path.splitext(os.path.basename(conversion.pdf_file.name))[0]}_ocr_text.json"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
