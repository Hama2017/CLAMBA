"""
PDF text extraction utilities for CLAMBA
"""

from pathlib import Path
from typing import Optional

import PyPDF2

from ..utils.logger import get_logger


class PDFExtractor:
    """
    PDF text extractor with robust error handling
    """
    
    def __init__(self):
        """Initialize PDF extractor"""
        self.logger = get_logger(__name__)
    
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
            
        Raises:
            ValueError: If PDF cannot be read or no text extracted
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if len(reader.pages) == 0:
                    raise ValueError("PDF file has no pages")
                
                text = ""
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        else:
                            self.logger.warning(f"No text extracted from page {page_num + 1}")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                if not text.strip():
                    raise ValueError("No text could be extracted from PDF")
                
                self.logger.info(f"Extracted {len(text)} characters from {len(reader.pages)} pages")
                return text.strip()
                
        except PyPDF2.errors.PdfReadError as e:
            raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def get_pdf_info(self, pdf_path: Path) -> dict:
        """
        Get information about PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        info = {
            "file_path": str(pdf_path),
            "file_size": 0,
            "page_count": 0,
            "has_text": False,
            "error": None
        }
        
        try:
            # File size
            info["file_size"] = pdf_path.stat().st_size
            
            # PDF information
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                info["page_count"] = len(reader.pages)
                
                # Check if first page has text
                if reader.pages:
                    first_page_text = reader.pages[0].extract_text()
                    info["has_text"] = bool(first_page_text and first_page_text.strip())
                
                # Metadata if available
                if reader.metadata:
                    info["title"] = reader.metadata.get("/Title", "")
                    info["author"] = reader.metadata.get("/Author", "")
                    info["creator"] = reader.metadata.get("/Creator", "")
                    info["producer"] = reader.metadata.get("/Producer", "")
                    
        except Exception as e:
            info["error"] = str(e)
            self.logger.error(f"Failed to get PDF info: {str(e)}")
        
        return info
    
    def validate_pdf(self, pdf_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate PDF file for text extraction
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file exists
            if not pdf_path.exists():
                return False, f"File not found: {pdf_path}"
            
            # Check file extension
            if not pdf_path.suffix.lower() == '.pdf':
                return False, f"File is not a PDF: {pdf_path}"
            
            # Check file size (minimum 100 bytes, maximum 100MB)
            file_size = pdf_path.stat().st_size
            if file_size < 100:
                return False, "PDF file is too small"
            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, "PDF file is too large (>100MB)"
            
            # Try to open and read basic structure
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if len(reader.pages) == 0:
                    return False, "PDF has no pages"
                
                if len(reader.pages) > 1000:  # Reasonable limit
                    return False, "PDF has too many pages (>1000)"
                
                # Try to extract text from first page
                try:
                    first_page_text = reader.pages[0].extract_text()
                    if not first_page_text or len(first_page_text.strip()) < 10:
                        return False, "PDF appears to contain no readable text"
                except:
                    return False, "Cannot extract text from PDF"
            
            return True, None
            
        except PyPDF2.errors.PdfReadError:
            return False, "Invalid or corrupted PDF file"
        except Exception as e:
            return False, f"PDF validation error: {str(e)}"