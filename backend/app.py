from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
import logging
import requests
import configparser
from utils.file_processor import process_image, process_pdf, process_djvu, get_supported_languages
import PyPDF2
from utils.wikisource_utils import extract_direct_file_url
from reportlab.pdfgen import canvas
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read config.ini for Wikimedia Commons credentials
config = configparser.ConfigParser()
config.read('config.ini')
WIKI_USERNAME = config.get('wiki', 'username', fallback=None)
WIKI_PASSWORD = config.get('wiki', 'password', fallback=None)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'pdf', 'djvu'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BATCH_SIZE_DEFAULT = 5

# Register Unicode fonts for Indian scripts
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
FONT_MAP = {
    'hin': ('NotoSansDevanagari', os.path.join(FONTS_DIR, 'NotoSansDevanagari-Regular.ttf')),
    'ben': ('NotoSansBengali', os.path.join(FONTS_DIR, 'NotoSansBengali-Regular.ttf')),
    'guj': ('NotoSansGujarati', os.path.join(FONTS_DIR, 'NotoSansGujarati-Regular.ttf')),
    'kan': ('NotoSansKannada', os.path.join(FONTS_DIR, 'NotoSansKannada-Regular.ttf')),
    'mal': ('NotoSansMalayalam', os.path.join(FONTS_DIR, 'NotoSansMalayalam-Regular.ttf')),
    'mar': ('NotoSansDevanagari', os.path.join(FONTS_DIR, 'NotoSansDevanagari-Regular.ttf')),
    'ori': ('NotoSansOriya', os.path.join(FONTS_DIR, 'NotoSansOriya-Regular.ttf')),
    'tam': ('NotoSansTamil', os.path.join(FONTS_DIR, 'NotoSansTamil-Regular.ttf')),
    'tel': ('NotoSansTelugu', os.path.join(FONTS_DIR, 'NotoSansTelugu-Regular.ttf')),
    'eng': ('Helvetica', None),
}
for font_name, font_path in FONT_MAP.values():
    if font_path and os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception:
            pass

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_commons_url(url):
    return 'upload.wikimedia.org' in url or 'commons.wikimedia.org' in url

def get_commons_session():
    """Return a requests.Session() logged in to Wikimedia Commons if credentials are set, else None."""
    if not WIKI_USERNAME or not WIKI_PASSWORD or 'your_username_here' in WIKI_USERNAME:
        return None
    session = requests.Session()
    # Step 1: Get login token
    r1 = session.get('https://commons.wikimedia.org/w/api.php', params={
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    })
    login_token = r1.json()['query']['tokens']['logintoken']
    # Step 2: Post login request
    r2 = session.post('https://commons.wikimedia.org/w/api.php', data={
        'action': 'login',
        'lgname': WIKI_USERNAME,
        'lgpassword': WIKI_PASSWORD,
        'lgtoken': login_token,
        'format': 'json'
    })
    if r2.json().get('login', {}).get('result') == 'Success':
        return session
    else:
        logger.warning('Wikimedia Commons login failed, falling back to anonymous download.')
        return None

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages."""
    return jsonify(get_supported_languages())

@app.route('/api/ocr', methods=['POST'])
def process_ocr():
    file = request.files.get('file')
    file_url = request.form.get('file_url')
    language = request.form.get('language', 'eng')
    batch = int(request.form.get('batch', 1))
    batch_size = int(request.form.get('batch_size', BATCH_SIZE_DEFAULT))

    if file and file_url:
        return jsonify({'error': 'Please provide either a file or a file URL, not both.'}), 400
    if not file and not file_url:
        return jsonify({'error': 'No file or file URL provided.'}), 400

    temp_filepath = None
    filename = None
    try:
        if file_url:
            # If the URL is a Wikisource file page, extract the direct file URL
            if "wikisource.org/wiki/File:" in file_url:
                direct_url = extract_direct_file_url(file_url)
                if not direct_url:
                    return jsonify({'error': 'Could not extract direct file URL from Wikisource page.'}), 400
                file_url = direct_url
            headers = {'User-Agent': 'Mozilla/5.0 (Wikisource OCR/1.0)'}
            session = None
            if is_commons_url(file_url):
                session = get_commons_session()
            if session:
                try:
                    r = session.get(file_url, stream=True, headers=headers, allow_redirects=True, timeout=60)
                except Exception as e:
                    return jsonify({'error': f'Error downloading file (Commons, authenticated): {str(e)}'}), 400
            else:
                try:
                    r = requests.get(file_url, stream=True, headers=headers, allow_redirects=True, timeout=60)
                except Exception as e:
                    return jsonify({'error': f'Error downloading file: {str(e)}'}), 400
            if r.status_code != 200:
                return jsonify({'error': f'Failed to download file from URL. HTTP status: {r.status_code}'}), 400
            filename = file_url.split('/')[-1]
            if not allowed_file(filename):
                return jsonify({'error': 'File type not allowed.'}), 400
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                temp_filepath = tmp.name
        elif file:
            filename = secure_filename(file.filename)
            if not allowed_file(filename):
                return jsonify({'error': 'File type not allowed.'}), 400
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)

        # Process the file based on its type
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            text = process_image(temp_filepath, language)
            result = {'text': text, 'pages': 1, 'batch': 1, 'batch_size': 1, 'total_pages': 1}
        elif filename.lower().endswith('.pdf'):
            # Batch processing for PDF
            # Get total pages
            with open(temp_filepath, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
            start_idx = (batch - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_pages)
            # PDF pages are 1-indexed for convert_from_path
            batch_texts = process_pdf(temp_filepath, language, start_page=start_idx+1, end_page=end_idx)
            result = {
                'text': '\n\n--- Page Break ---\n\n'.join(batch_texts),
                'pages': len(batch_texts),
                'batch': batch,
                'batch_size': batch_size,
                'total_pages': total_pages
            }
        elif filename.lower().endswith('.djvu'):
            # Batch processing for DjVu
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, 'output.pdf')
                if not convert_djvu_to_pdf(temp_filepath, pdf_path):
                    return jsonify({'error': 'Failed to convert DjVu to PDF'}), 400
                with open(pdf_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    total_pages = len(reader.pages)
                start_idx = (batch - 1) * batch_size
                end_idx = min(start_idx + batch_size, total_pages)
                batch_texts = process_pdf(pdf_path, language, start_page=start_idx+1, end_page=end_idx)
            result = {
                'text': '\n\n--- Page Break ---\n\n'.join(batch_texts),
                'pages': len(batch_texts),
                'batch': batch,
                'batch_size': batch_size,
                'total_pages': total_pages
            }
        else:
            return jsonify({'error': 'Unsupported file type.'}), 400

        return jsonify({'success': True, **result})
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass

@app.route('/api/ocr/pdf', methods=['POST'])
def process_ocr_pdf():
    file = request.files.get('file')
    file_url = request.form.get('file_url')
    language = request.form.get('language', 'eng')
    batch = int(request.form.get('batch', 1))
    batch_size = int(request.form.get('batch_size', BATCH_SIZE_DEFAULT))

    if file and file_url:
        return jsonify({'error': 'Please provide either a file or a file URL, not both.'}), 400
    if not file and not file_url:
        return jsonify({'error': 'No file or file URL provided.'}), 400

    temp_filepath = None
    filename = None
    try:
        if file_url:
            # If the URL is a Wikisource file page, extract the direct file URL
            if "wikisource.org/wiki/File:" in file_url:
                direct_url = extract_direct_file_url(file_url)
                if not direct_url:
                    return jsonify({'error': 'Could not extract direct file URL from Wikisource page.'}), 400
                file_url = direct_url
            headers = {'User-Agent': 'Mozilla/5.0 (Wikisource OCR/1.0)'}
            session = None
            if is_commons_url(file_url):
                session = get_commons_session()
            if session:
                try:
                    r = session.get(file_url, stream=True, headers=headers, allow_redirects=True, timeout=60)
                except Exception as e:
                    return jsonify({'error': f'Error downloading file (Commons, authenticated): {str(e)}'}), 400
            else:
                try:
                    r = requests.get(file_url, stream=True, headers=headers, allow_redirects=True, timeout=60)
                except Exception as e:
                    return jsonify({'error': f'Error downloading file: {str(e)}'}), 400
            if r.status_code != 200:
                return jsonify({'error': f'Failed to download file from URL. HTTP status: {r.status_code}'}), 400
            filename = file_url.split('/')[-1]
            if not allowed_file(filename):
                return jsonify({'error': 'File type not allowed.'}), 400
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                temp_filepath = tmp.name
        elif file:
            filename = secure_filename(file.filename)
            if not allowed_file(filename):
                return jsonify({'error': 'File type not allowed.'}), 400
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)

        # Process the file based on its type
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            ocr_text = process_image(temp_filepath, language)
            total_pages = 1
            batch = 1
            batch_size = 1
        elif filename.lower().endswith('.pdf'):
            with open(temp_filepath, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
            start_idx = (batch - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_pages)
            batch_texts = process_pdf(temp_filepath, language, start_page=start_idx+1, end_page=end_idx)
            ocr_text = '\n\n--- Page Break ---\n\n'.join(batch_texts)
        elif filename.lower().endswith('.djvu'):
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, 'output.pdf')
                if not convert_djvu_to_pdf(temp_filepath, pdf_path):
                    return jsonify({'error': 'Failed to convert DjVu to PDF'}), 400
                with open(pdf_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    total_pages = len(reader.pages)
                start_idx = (batch - 1) * batch_size
                end_idx = min(start_idx + batch_size, total_pages)
                batch_texts = process_pdf(pdf_path, language, start_page=start_idx+1, end_page=end_idx)
            ocr_text = '\n\n--- Page Break ---\n\n'.join(batch_texts)
        else:
            return jsonify({'error': 'Unsupported file type.'}), 400

        # Generate PDF in memory
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer)
        # Choose font based on language
        font_name = FONT_MAP.get(language, ('Helvetica', None))[0]
        try:
            c.setFont(font_name, 14)
        except Exception:
            c.setFont('Helvetica', 14)
        textobject = c.beginText(40, 800)
        for line in ocr_text.splitlines():
            textobject.textLine(line)
            if textobject.getY() < 40:
                c.drawText(textobject)
                c.showPage()
                textobject = c.beginText(40, 800)
                try:
                    c.setFont(font_name, 14)
                except Exception:
                    c.setFont('Helvetica', 14)
        c.drawText(textobject)
        c.save()
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, as_attachment=True, download_name='ocr_result.pdf', mimetype='application/pdf')
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 