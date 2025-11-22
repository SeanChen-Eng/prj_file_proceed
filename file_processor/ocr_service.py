import fitz
import json
from PIL import Image
import io
from .models import PDFConversion

class OCRService:
    def __init__(self):
        self.ocr_engine = None
    
    def _load_ocr_engine(self):
        """Lazy load OCR engine to avoid import errors during migration"""
        if self.ocr_engine is None:
            try:
                import easyocr
                self.ocr_engine = easyocr.Reader(['ch_sim', 'en'])  # Chinese and English
            except ImportError as e:
                raise ImportError(f"EasyOCR not installed: {e}")
        return self.ocr_engine
    
    def extract_text_from_pdf(self, pdf_conversion_id):
        """Extract text from PDF using OCR"""
        pdf_conversion = None
        try:
            pdf_conversion = PDFConversion.objects.get(id=pdf_conversion_id)
            pdf_conversion.ocr_status = 'processing'
            pdf_conversion.save()
            
            # Load OCR engine
            reader = self._load_ocr_engine()
            
            # Open PDF
            doc = fitz.open(pdf_conversion.pdf_file.path)
            extracted_text = {}
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # Higher resolution for better OCR
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image then to numpy array
                image = Image.open(io.BytesIO(img_data))
                import numpy as np
                image_array = np.array(image)
                
                # Perform OCR
                results = reader.readtext(image_array)
                
                # Extract text and confidence
                page_text = []
                for (bbox, text, confidence) in results:
                    if confidence > 0.5:  # Filter low confidence results
                        # Convert bbox coordinates to regular Python lists/floats
                        bbox_coords = [[float(x), float(y)] for x, y in bbox]
                        page_text.append({
                            'text': text.strip(),
                            'confidence': float(confidence),
                            'bbox': bbox_coords
                        })
                
                extracted_text[f'page_{page_num + 1}'] = {
                    'page_number': page_num + 1,
                    'text_blocks': page_text,
                    'full_text': ' '.join([block['text'] for block in page_text])
                }
            
            doc.close()
            
            # Save results
            pdf_conversion.ocr_text = extracted_text
            pdf_conversion.ocr_status = 'completed'
            pdf_conversion.save()
            
            return extracted_text
            
        except Exception as e:
            if pdf_conversion:
                pdf_conversion.ocr_status = 'failed'
                pdf_conversion.save()
            print(f"OCR processing failed: {str(e)}")
            return None
    
    def get_text_summary(self, extracted_text):
        """Generate summary of extracted text"""
        if not extracted_text:
            return {}
        
        total_pages = len(extracted_text)
        total_text_blocks = sum(len(page_data['text_blocks']) for page_data in extracted_text.values())
        total_characters = sum(len(page_data['full_text']) for page_data in extracted_text.values())
        
        return {
            'total_pages': total_pages,
            'total_text_blocks': total_text_blocks,
            'total_characters': total_characters,
            'average_confidence': self._calculate_average_confidence(extracted_text)
        }
    
    def _calculate_average_confidence(self, extracted_text):
        """Calculate average confidence score"""
        all_confidences = []
        for page_data in extracted_text.values():
            for block in page_data['text_blocks']:
                all_confidences.append(block['confidence'])
        
        return sum(all_confidences) / len(all_confidences) if all_confidences else 0