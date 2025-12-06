import os
from PyPDF2 import PdfReader
import pdfplumber
from PIL import Image
import pytesseract
import io

def extract_text_from_pdf(file_path):
    """Extract text from PDF using multiple methods"""
    text = ""
    errors = []
    
    # Try pdfplumber first
    try:
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                errors.append("PDF has no pages")
            else:
                for i, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as page_error:
                        errors.append(f"Page {i+1} extraction failed: {str(page_error)}")
                        continue
    except Exception as e:
        errors.append(f"pdfplumber error: {str(e)}")
    
    # Fallback to PyPDF2 if pdfplumber failed
    if not text.strip():
        try:
            reader = PdfReader(file_path)
            if len(reader.pages) == 0:
                errors.append("PDF has no pages (PyPDF2)")
            else:
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as page_error:
                        errors.append(f"Page {i+1} extraction failed (PyPDF2): {str(page_error)}")
                        continue
        except Exception as e:
            errors.append(f"PyPDF2 error: {str(e)}")
    
    if errors:
        print(f"PDF extraction warnings/errors: {'; '.join(errors)}")
    
    return text.strip()

def extract_text_from_images_in_pdf(file_path):
    """Extract text from images in PDF using OCR"""
    text = ""
    errors = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # Try to convert entire page to image if no embedded images
                    page_image = page.to_image(resolution=150)
                    pil_image = page_image.original
                    
                    try:
                        ocr_text = pytesseract.image_to_string(pil_image, config='--psm 1')
                        if ocr_text.strip():
                            text += ocr_text + "\n"
                    except Exception as ocr_error:
                        errors.append(f"OCR failed on page {page_num + 1}: {str(ocr_error)}")
                        
                except Exception as page_error:
                    errors.append(f"Image conversion failed on page {page_num + 1}: {str(page_error)}")
                    continue
                    
    except Exception as e:
        errors.append(f"OCR extraction error: {str(e)}")
    
    if errors:
        print(f"OCR warnings/errors: {'; '.join(errors)}")
    
    return text.strip()

def process_pdf_file(file_path):
    """Process PDF file with text extraction and OCR"""
    text = extract_text_from_pdf(file_path)
    
    if not text or len(text) < 100:
        ocr_text = extract_text_from_images_in_pdf(file_path)
        if ocr_text:
            text = text + "\n" + ocr_text if text else ocr_text
    
    return text

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_text(text):
    """Clean and normalize text"""
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)
