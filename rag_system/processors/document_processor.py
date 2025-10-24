"""
Document Processor for RAG System
Handles PDF, TXT, MD, and CSV file processing
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# PDF processing
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processor for multiple file types"""
    
    def __init__(self, max_file_size_mb: int = 50):
        self.max_file_size_mb = max_file_size_mb
        self.supported_extensions = ['.pdf', '.txt', '.md', '.csv']
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file and return structured document data
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dict containing:
            - content: Extracted text content
            - metadata: File information
            - chunks: List of text chunks
            - success: Boolean indicating success
            - error: Error message if failed
        """
        try:
            # Validate file
            validation_result = self._validate_file(file_path)
            if not validation_result['valid']:
                return {
                    'content': '',
                    'metadata': {},
                    'chunks': [],
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            # Process based on file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                content = self._process_pdf(file_path)
            elif file_ext == '.txt':
                content = self._process_txt(file_path)
            elif file_ext == '.md':
                content = self._process_markdown(file_path)
            elif file_ext == '.csv':
                content = self._process_csv(file_path)
            else:
                return {
                    'content': '',
                    'metadata': file_info,
                    'chunks': [],
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}'
                }
            
            # Create chunks
            chunks = self._create_chunks(content)
            
            return {
                'content': content,
                'metadata': file_info,
                'chunks': chunks,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return {
                'content': '',
                'metadata': {},
                'chunks': [],
                'success': False,
                'error': str(e)
            }
    
    def _validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate file exists, size, and type"""
        if not os.path.exists(file_path):
            return {'valid': False, 'error': 'File does not exist'}
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            return {
                'valid': False, 
                'error': f'File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB'
            }
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_extensions:
            return {
                'valid': False,
                'error': f'Unsupported file type: {file_ext}. Supported: {self.supported_extensions}'
            }
        
        return {'valid': True, 'error': None}
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Extract file metadata"""
        file_path_obj = Path(file_path)
        stat = file_path_obj.stat()
        
        return {
            'filename': file_path_obj.name,
            'file_type': file_path_obj.suffix.lower(),
            'file_size_bytes': stat.st_size,
            'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created_time': stat.st_ctime,
            'modified_time': stat.st_mtime,
            'full_path': str(file_path_obj.absolute())
        }
    
    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
        
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():  # Only add non-empty pages
                        text_content.append(f"--- Page {page_num + 1} ---\\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1} from {file_path}: {e}")
                    continue
        
        return "\\n\\n".join(text_content)
    
    def _process_txt(self, file_path: str) -> str:
        """Process plain text file"""
        encodings_to_try = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error reading text file {file_path} with encoding {encoding}: {e}")
                continue
        
        raise ValueError(f"Could not decode text file {file_path} with any supported encoding")
    
    def _process_markdown(self, file_path: str) -> str:
        """Process Markdown file (treat as text for now)"""
        # For now, treat as text. Could be enhanced with markdown parsing
        return self._process_txt(file_path)
    
    def _process_csv(self, file_path: str) -> str:
        """Convert CSV to natural language text"""
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Create descriptive text
            text_content = []
            text_content.append(f"CSV Data Summary:")
            text_content.append(f"Number of rows: {len(df)}")
            text_content.append(f"Number of columns: {len(df.columns)}")
            text_content.append(f"Columns: {', '.join(df.columns)}")
            text_content.append("")
            
            # Convert each row to natural language
            text_content.append("Data Records:")
            for index, row in df.iterrows():
                row_text = f"Record {index + 1}: "
                row_descriptions = []
                for col, value in row.items():
                    if pd.notna(value):  # Skip NaN values
                        row_descriptions.append(f"{col} is {value}")
                row_text += ", ".join(row_descriptions)
                text_content.append(row_text)
                
                # Limit to prevent huge files
                if index >= 1000:  # Max 1000 rows
                    text_content.append(f"... (showing first 1000 rows of {len(df)} total rows)")
                    break
            
            return "\\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {e}")
            raise
    
    def _create_chunks(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split content into overlapping chunks
        
        Args:
            content: Text content to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not content or len(content) <= chunk_size:
            return [content] if content else []
        
        chunks = []
        start = 0
        
        while start < len(content):
            # Find the end of this chunk
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence or paragraph
            if end < len(content):
                # Look for good break points (paragraph, sentence, word boundaries)
                break_points = [
                    content.rfind('\\n\\n', start, end),  # Paragraph break
                    content.rfind('. ', start, end),      # Sentence break
                    content.rfind('\\n', start, end),     # Line break
                    content.rfind(' ', start, end)        # Word break
                ]
                
                # Use the best available break point
                for break_point in break_points:
                    if break_point > start:
                        end = break_point + 1
                        break
            
            # Extract chunk
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position (with overlap)
            start = max(start + 1, end - overlap)
        
        return chunks

    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Process all supported files in a directory
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of processing results for each file
        """
        results = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return results
        
        # Find all supported files
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                logger.info(f"Processing file: {file_path.name}")
                result = self.process_file(str(file_path))
                result['file_path'] = str(file_path)
                results.append(result)
        
        return results