import os
import subprocess
import tempfile
import json
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)

# Default supported languages
DEFAULT_LANGUAGES = [
    {
        "code": "eng",
        "name": "English",
        "script": "Latin"
    }
]

# Load supported languages
try:
    LANGUAGES_CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'languages.json')
    with open(LANGUAGES_CONFIG, 'r') as f:
        SUPPORTED_LANGUAGES = json.load(f)['languages']
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.warning(f"Could not load languages.json: {str(e)}. Using default languages.")
    SUPPORTED_LANGUAGES = DEFAULT_LANGUAGES

def get_supported_languages():
    """Get list of supported languages."""
    return SUPPORTED_LANGUAGES

def convert_djvu_to_pdf(djvu_path, output_path):
    """Convert DjVu file to PDF using ddjvu command line tool."""
    try:
        subprocess.run(['ddjvu', '-format=pdf', djvu_path, output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting DjVu to PDF: {str(e)}")
        return False
    except FileNotFoundError:
        logger.error("ddjvu command not found. Please install djvulibre-bin")
        return False

def process_pdf(pdf_path, language='eng', dpi=300, start_page=None, end_page=None):
    """Process PDF file and return list of extracted text from each page. Only process pages in the given range if specified."""
    try:
        # Convert only the needed pages for the batch
        convert_kwargs = {'dpi': 300}
        if start_page is not None and end_page is not None:
            convert_kwargs['first_page'] = start_page
            convert_kwargs['last_page'] = end_page
        images = convert_from_path(pdf_path, **convert_kwargs)
        
        # Process each page
        texts = []
        for i, image in enumerate(images):
            image = image.convert('L')
            logger.info(f"Processing PDF page {start_page + i if start_page else i+1} with language: {language}")
            text = pytesseract.image_to_string(image, lang=language, config='--psm 3')
            texts.append(text)
        
        return texts
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise

def process_djvu(djvu_path, language='eng', dpi=300, start_page=None, end_page=None):
    """Process DjVu file and return list of extracted text from each page. Only process pages in the given range if specified."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, 'output.pdf')
            if not convert_djvu_to_pdf(djvu_path, pdf_path):
                raise Exception("Failed to convert DjVu to PDF")
            return process_pdf(pdf_path, language, dpi, start_page, end_page)
    except Exception as e:
        logger.error(f"Error processing DjVu: {str(e)}")
        raise

def process_image(image_path, language='eng'):
    """Process image file and return extracted text."""
    try:
        image = Image.open(image_path)
        image = image.convert('L')  # Grayscale for better OCR
        logger.info(f"Processing image {image_path} with language: {language}")
        text = pytesseract.image_to_string(image, lang=language, config='--psm 3')
        return text
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise 