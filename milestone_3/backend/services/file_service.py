"""
File processing service for PDF and document handling
"""
import os
import PyPDF2
import pdfplumber
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import tempfile

class FileService:
    """Service class for file processing operations"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def is_allowed_file(filename):
        """Check if file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file(file):
        """Validate uploaded file"""
        if not file:
            return {'success': False, 'error': 'No file provided'}
        
        if file.filename == '':
            return {'success': False, 'error': 'No file selected'}
        
        if not FileService.is_allowed_file(file.filename):
            return {
                'success': False, 
                'error': f'File type not allowed. Allowed types: {", ".join(FileService.ALLOWED_EXTENSIONS)}'
            }
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > FileService.MAX_FILE_SIZE:
            return {
                'success': False, 
                'error': f'File too large. Maximum size: {FileService.MAX_FILE_SIZE // (1024*1024)}MB'
            }
        
        return {'success': True}
    
    @staticmethod
    def extract_text_from_pdf(file_storage):
        """Extract text from PDF file using multiple methods"""
        try:
            text_content = ""
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file_storage.save(temp_file.name)
                temp_file_path = temp_file.name
            
            try:
                # Method 1: Try pdfplumber first (better for complex layouts)
                with pdfplumber.open(temp_file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                
                # If pdfplumber didn't extract much text, try PyPDF2
                if len(text_content.strip()) < 100:
                    text_content = ""
                    with open(temp_file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text_content += page_text + "\n"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
            if not text_content.strip():
                return {
                    'success': False,
                    'error': 'Could not extract text from PDF. The file might be image-based or corrupted.'
                }
            
            return {
                'success': True,
                'text': text_content.strip(),
                'word_count': len(text_content.split()),
                'char_count': len(text_content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error extracting text from PDF: {str(e)}'
            }
    
    @staticmethod
    def extract_text_from_txt(file_storage):
        """Extract text from plain text file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            text_content = None
            
            for encoding in encodings:
                try:
                    file_storage.seek(0)
                    text_content = file_storage.read().decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                return {
                    'success': False,
                    'error': 'Could not decode text file. Unsupported encoding.'
                }
            
            return {
                'success': True,
                'text': text_content.strip(),
                'word_count': len(text_content.split()),
                'char_count': len(text_content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error reading text file: {str(e)}'
            }
    
    @staticmethod
    def process_uploaded_file(file):
        """Process uploaded file and extract text"""
        try:
            # Validate file
            validation_result = FileService.validate_file(file)
            if not validation_result['success']:
                return validation_result
            
            # Get file info
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Extract text based on file type
            if file_extension == 'pdf':
                extraction_result = FileService.extract_text_from_pdf(file)
            elif file_extension == 'txt':
                extraction_result = FileService.extract_text_from_txt(file)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_extension}'
                }
            
            if not extraction_result['success']:
                return extraction_result
            
            return {
                'success': True,
                'filename': filename,
                'file_type': file_extension,
                'text': extraction_result['text'],
                'word_count': extraction_result['word_count'],
                'char_count': extraction_result['char_count'],
                'file_size': len(file.read()) if hasattr(file, 'read') else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    @staticmethod
    def clean_extracted_text(text):
        """Clean and normalize extracted text"""
        try:
            # Remove excessive whitespace
            import re
            
            # Replace multiple spaces with single space
            text = re.sub(r'\s+', ' ', text)
            
            # Remove excessive newlines
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            # Remove special characters that might interfere with processing
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return {
                'success': True,
                'cleaned_text': text,
                'original_length': len(text),
                'cleaned_length': len(text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error cleaning text: {str(e)}'
            }
    
    @staticmethod
    def get_file_preview(text, max_length=500):
        """Get a preview of the extracted text"""
        try:
            if len(text) <= max_length:
                return text
            
            # Find a good breaking point (end of sentence or word)
            preview = text[:max_length]
            
            # Try to break at sentence end
            last_period = preview.rfind('.')
            last_exclamation = preview.rfind('!')
            last_question = preview.rfind('?')
            
            sentence_end = max(last_period, last_exclamation, last_question)
            
            if sentence_end > max_length * 0.7:  # If sentence end is not too far back
                preview = preview[:sentence_end + 1]
            else:
                # Break at word boundary
                last_space = preview.rfind(' ')
                if last_space > max_length * 0.8:
                    preview = preview[:last_space]
            
            return preview + "..."
            
        except Exception:
            return text[:max_length] + "..." if len(text) > max_length else text