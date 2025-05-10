from bs4 import BeautifulSoup
import requests
import re
import pdfplumber
from typing import Dict, Any, List
import os

class SECFilingProcessor:
    """Specialized processor for SEC filings, particularly 10-K reports"""
    
    def __init__(self):
        self.section_patterns = {
            "business": r"Item\s*1\.?\s*Business",
            "risk_factors": r"Item\s*1A\.?\s*Risk\s*Factors",
            "management_discussion": r"Item\s*7\.?\s*Management'?s?\s*Discussion",
            "financial_statements": r"Item\s*8\.?\s*Financial\s*Statements",
            # Add more section patterns as needed
        }
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load and process a local SEC filing file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._process_pdf(file_path)
        elif file_extension in ['.html', '.htm']:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return self._process_html(html_content)
        else:
            # Fall back to regular document processing
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'title': os.path.basename(file_path),
                'content': content,
                'file_type': file_extension,
                'status': 'success'
            }
    
    def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a 10-K PDF file"""
        sections = {}
        current_section = "general"
        sections[current_section] = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    
                    # Identify sections based on patterns
                    for section_name, pattern in self.section_patterns.items():
                        if re.search(pattern, text, re.IGNORECASE):
                            current_section = section_name
                            if current_section not in sections:
                                sections[current_section] = []
                    
                    # Add text to current section
                    sections[current_section].append(text)
            
            # Combine text for each section
            combined_sections = {k: '\n'.join(v) for k, v in sections.items()}
            
            # Also keep full content for standard processing
            full_content = '\n'.join(['\n'.join(section) for section in sections.values()])
            
            return {
                'title': os.path.basename(pdf_path),
                'content': full_content,
                'sections': combined_sections,
                'file_type': '.pdf',
                'status': 'success'
            }
        except Exception as e:
            # Fall back to standard method if pdfplumber fails
            try:
                with open(pdf_path, 'rb') as f:
                    # Just return basic info
                    return {
                        'title': os.path.basename(pdf_path),
                        'content': f"PDF content could not be fully extracted: {str(e)}",
                        'file_type': '.pdf',
                        'status': 'success'
                    }
            except Exception as file_error:
                return {
                    'status': 'error',
                    'message': f'Error processing PDF: {str(file_error)}'
                }
    
    def _process_html(self, html_content: str) -> Dict[str, Any]:
        """Process HTML content from an SEC filing"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Try to extract sections
            sections = {"general": text_content}
            
            # Look for section headers in the text
            for section_name, pattern in self.section_patterns.items():
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    start_pos = match.start()
                    # Find the next section start or use end of text
                    next_section_starts = [
                        text_content.find(p, start_pos + 1) 
                        for p in self.section_patterns.values() 
                        if text_content.find(p, start_pos + 1) != -1
                    ]
                    
                    end_pos = min(next_section_starts) if next_section_starts else len(text_content)
                    sections[section_name] = text_content[start_pos:end_pos].strip()
            
            return {
                'sections': sections,
                'content': text_content,
                'file_type': '.html',
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error', 
                'message': f'Error processing HTML: {str(e)}'
            }