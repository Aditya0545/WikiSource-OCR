# Wikisource OCR - Product Requirements Document

## Overview
Wikisource OCR is a modern, open-source web application designed to perform Optical Character Recognition (OCR) on PDF/DjVu files and prepare them for upload to Wikisource. The tool uses Tesseract OCR to process documents and generate text files locally, with support for multiple languages and numeral systems. The application is designed to be user-friendly, privacy-focused, and fully functional without external cloud services.

## Target Users
- Wikisource contributors
- Wikimedia digitization volunteers
- Archivists and researchers working with public domain texts
- Library and museum digitization teams
- Academic researchers

## Core Features

### 1. File Processing
- Drag-and-drop or file picker for image/PDF input
- Support for multiple file formats (PNG, JPG, TIFF, PDF, DjVu)
- Multi-page document support
- Batch processing capability

### 2. OCR Processing
- Tesseract.js integration for client-side OCR
- Multiple language support
- Configurable OCR parameters
- Progress tracking and status updates

### 3. Text Processing
- Real-time text preview
- In-browser text editing
- Automatic text cleanup
- Multi-column text handling
- Special character preservation

### 4. Output Options
- Copy to clipboard functionality
- Download as TXT file
- Direct Wikisource format export
- Backup file generation
- Log file creation

### 5. User Interface
- Clean, intuitive design
- Dark/Light mode toggle
- Responsive layout for mobile and desktop
- Progress indicators
- Error notifications

## Technical Requirements

### Frontend
- HTML5, CSS3, JavaScript
- React.js framework
- Responsive design
- Progressive Web App capabilities

### Backend (Optional)
- Flask (Python) or Node.js
- RESTful API design
- File handling and processing
- Error logging and monitoring

### OCR Engine
- Tesseract.js for client-side processing
- Tesseract API for server-side processing
- Language pack management
- Performance optimization

### Hosting
- GitHub Pages for static deployment
- Lightweight VPS for backend services
- CDN for static assets

## Performance Requirements
- OCR processing time: < 5 seconds per page
- Memory usage: < 500MB per document
- Concurrent processing: Up to 4 pages
- Browser compatibility: Latest 2 versions of major browsers

## Privacy and Security
- No external API dependencies
- Local processing of all files
- No data storage on servers
- Secure file handling
- Regular security audits

## User Flow
1. User opens the web application
2. Uploads document(s) via drag-drop or file picker
3. Selects language and processing options
4. Initiates OCR processing
5. Reviews and edits extracted text
6. Exports or copies processed text
7. Uploads to Wikisource

## Acceptance Criteria

### Image Processing
- Supports PNG, JPG, TIFF formats
- Handles multi-page documents
- Maintains image quality
- Proper error handling

### OCR Quality
- 90%+ accuracy for clean printed text
- Proper handling of special characters
- Support for multiple languages
- Accurate column detection

### User Interface
- Intuitive navigation
- Clear progress indicators
- Helpful error messages
- Responsive design

### Export Functionality
- Working clipboard integration
- TXT file export
- Wikisource format export
- Backup file generation

## Timeline

### Phase 1: Core Development (Weeks 1-3)
- UI/UX design and implementation
- Basic file handling
- Tesseract integration
- Text preview and editing

### Phase 2: Enhancement (Weeks 4-6)
- Multi-language support
- Advanced text processing
- Export functionality
- Performance optimization

### Phase 3: Testing and Deployment (Weeks 7-8)
- User testing
- Bug fixes
- Documentation
- Deployment

## Future Enhancements
1. PDF support and batch processing
2. Wikisource syntax templates
3. Wikimedia API integration
4. Text-to-speech verification
5. Machine learning-based improvements
6. Collaborative editing features
7. Version control integration
8. Custom OCR training support

## System Requirements

### Operating System
- Ubuntu 24.04 LTS or later
- Other Linux distributions may work but are not officially supported

### System Dependencies
The following system packages need to be installed:
```bash
# PDF and DjVu processing tools
sudo apt-get install djvulibre-bin libdjvulibre21 libtiff-tools mupdf mupdf-tools pdftk poppler-utils git djview

# Tesseract OCR and its dependencies
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng  # For English
sudo apt-get install tesseract-ocr-fra  # For French
sudo apt-get install tesseract-ocr-deu  # For German
sudo apt-get install tesseract-ocr-spa  # For Spanish
sudo apt-get install tesseract-ocr-ben  # For Bengali
# Add more language packs as needed

# Python package management
sudo apt-get install python-software-properties

# Additional repositories
sudo add-apt-repository -y ppa:ubuntuhandbook1/apps
sudo add-apt-repository ppa:malteworld/ppa -y
sudo apt update
```

### Python Dependencies
Required Python packages:
```bash
pip install pytesseract
pip install Pillow
pip install requests wikitools
```

## Configuration

1. Create a `config.ini` file with the following settings:
```ini
[settings]
file_url = <URL of the PDF/DjVu file>
columns = <number of columns in the document>
wiki_username = <your Wikisource username>
wiki_password = <your Wikisource password>
wikisource_language_code = <language code, e.g., 'en' for English, 'bn' for Bengali>
tesseract_language = <language code for Tesseract, e.g., 'eng' for English, 'ben' for Bengali>
dpi = <DPI for image conversion, default 400>
```

## Usage

1. Clone the repository:
```bash
git clone <repository-url>
cd wikisource-ocr
```

2. Run the setup script:
```bash
bash ./setup.sh
```

3. Run the OCR process:
```bash
python3 do_ocr.py
```

## Process Flow

1. **File Download and Preparation**
   - Downloads the specified PDF/DjVu file
   - Converts DjVu to PDF if necessary
   - Splits PDF into pages based on column configuration

2. **Image Conversion**
   - Creates a temporary directory for processing
   - Converts PDF pages to JPEG images using Ghostscript
   - Quality settings: 400 DPI, JPEG quality 95
   - Optional image preprocessing for better OCR results:
     - Deskewing
     - Noise removal
     - Contrast enhancement

3. **Tesseract OCR Processing**
   - Processes each JPEG image using Tesseract OCR
   - Supports multiple languages
   - Configurable OCR parameters:
     - Page segmentation mode
     - OCR engine mode
     - Language selection
     - DPI settings

4. **Text Processing**
   - Processes OCRed text files
   - Handles multi-column documents
   - Creates final text files for each page
   - Generates a combined text file
   - Post-processing options:
     - Line break handling
     - Paragraph detection
     - Special character handling

5. **Cleanup**
   - Moves temporary files to the temp directory
   - Creates a backup of text files

## Data Flow Diagrams

[Moved to work.md]

## Indian Numerals Support

### Supported Numeral Systems
The system supports multiple Indian numeral systems through the `indian_numerals.ini` configuration file:

1. **Bengali (bn)**
   - Uses: ০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯
   - Used in: Bengali, Assamese

2. **Odia (or)**
   - Uses: ୦, ୧, ୨, ୩, ୪, ୫, ୬, ୭, ୮, ୯
   - Used in: Odia language

3. **Gujarati (gu)**
   - Uses: ૦, ૧, ૨, ૩, ૪, ૫, ૬, ૭, ૮, ૯
   - Used in: Gujarati language

4. **Kannada (kn)**
   - Uses: ೦, ೧, ೨, ೩, ೪, ೫, ೬, ೭, ೮, ೯
   - Used in: Kannada language

5. **Malayalam (ml)**
   - Uses: ൦, ൧, ൨, ൩, ൪, ൫, ൬, ൭, ൮, ൯
   - Used in: Malayalam language

6. **Sanskrit (sa)**
   - Uses: ०, १, २, ३, ४, ५, ६, ७, ८, ९
   - Used in: Sanskrit, Marathi, Hindi

7. **Assamese (as)**
   - Uses: ০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯
   - Similar to Bengali numerals

8. **Marathi (mr)**
   - Uses: ०, १, २, ३, ४, ५, ६, ७, ८, ९
   - Similar to Sanskrit numerals

### Implementation

1. **Configuration**
   ```ini
   [language_code]
   0 = <numeral_0>
   1 = <numeral_1>
   ...
   9 = <numeral_9>
   ```

2. **Usage in OCR Processing**
   - Automatic detection of numeral system based on language
   - Conversion between different numeral systems
   - Preservation of original numerals in output

3. **Text Processing**
   - Normalization of numerals
   - Handling of mixed numeral systems
   - Special handling for mathematical expressions

### Data Flow for Numeral Processing
```
[OCR Text] --> [Numeral Detection] --> [Numeral Conversion] --> [Formatted Text]
              |
              v
[Language Detection] --> [Numeral System Selection]
```

### Error Handling for Numerals
1. **Common Issues**
   - Mixed numeral systems
   - Incorrect numeral recognition
   - Special character confusion

2. **Solutions**
   - Language-specific numeral validation
   - Context-aware numeral conversion
   - Fallback to standard numerals

### Best Practices
1. **Configuration**
   - Keep numeral mappings up to date
   - Validate numeral configurations
   - Document language-specific rules

2. **Processing**
   - Preserve original numerals when possible
   - Use appropriate numeral system for each language
   - Handle mixed content appropriately

3. **Output**
   - Maintain consistency in numeral usage
   - Document numeral system used
   - Provide conversion options if needed

## Error Handling

The script includes error handling for:
- File download failures
- PDF conversion errors
- Tesseract OCR processing errors
- Text file encoding issues
- Image preprocessing failures
- Memory management for large files

## Output

The script generates:
1. Individual text files for each page
2. A combined text file with all pages
3. A backup directory with all text files
4. Log files in the `./log` directory
5. Optional debug images showing OCR regions

## Troubleshooting

Common issues and solutions:
1. **Tesseract OCR Issues**
   - Verify Tesseract installation: `tesseract --version`
   - Check language pack installation
   - Adjust DPI settings if OCR quality is poor
   - Try different page segmentation modes
   - For Bengali text:
     - Ensure proper font rendering
     - Check for correct character encoding
     - Verify conjunct formation
     - Use appropriate page segmentation mode for Bengali script

2. **PDF Processing**
   - Verify PDF file integrity
   - Check if Ghostscript is properly installed
   - Ensure sufficient disk space
   - Verify image quality after conversion

3. **OCR Quality**
   - Adjust image preprocessing parameters
   - Try different DPI settings
   - Check image contrast and clarity
   - Verify column settings
   - Use appropriate language pack

## Maintenance

Regular maintenance tasks:
1. Update Tesseract and language packs
2. Monitor disk space usage
3. Clean up temporary files
4. Update Python packages
5. Check for new language pack releases

## Future Improvements

Potential enhancements:
1. Support for more file formats
2. Improved error handling
3. Progress reporting
4. Batch processing capability
5. Web interface
6. Support for more languages
7. Advanced image preprocessing options
8. Machine learning-based post-processing
9. Parallel processing for faster OCR
10. Custom OCR training support 