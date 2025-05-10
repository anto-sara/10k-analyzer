from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import PyPDF2
import io
import os
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
    
    def load_document(self, file_path: str) -> Dict[str, Any]:
        """Load a document from file path."""
        try:
            # Extract file info
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1].lower()
            
            # Handle different file types
            if file_type in ['.txt', '.md', '.py', '.json', '.csv']:
                loader = TextLoader(file_path)
                docs = loader.load()
                
                # For simple text files, combine all content
                full_text = '\n\n'.join([doc.page_content for doc in docs])
                
                return {
                    'title': file_name,
                    'content': full_text,
                    'file_type': file_type,
                    'status': 'success'
                }
            elif file_type == '.pdf':
                try:
                    # Use PyPDFLoader for PDFs
                    loader = PyPDFLoader(file_path)
                    documents = loader.load()
                    
                    # Combine the content from all pages
                    full_text = '\n\n'.join([doc.page_content for doc in documents])
                    
                    return {
                        'title': file_name,
                        'content': full_text,
                        'file_type': file_type,
                        'status': 'success'
                    }
                except Exception as e:
                    return {
                        'status': 'error',
                        'message': f'Error processing PDF: {str(e)}'
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported file type: {file_type}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error loading document: {str(e)}'
            }
    
    def split_document(self, content: str) -> List[Dict[str, Any]]:
        """Split document content into chunks."""
        try:
            chunks = self.text_splitter.split_text(content)
            
            return [{
                'chunk_text': chunk,
                'chunk_index': i
            } for i, chunk in enumerate(chunks)]
            
        except Exception as e:
            return [{
                'status': 'error',
                'message': f'Error splitting document: {str(e)}'
            }]