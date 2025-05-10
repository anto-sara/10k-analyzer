from .processing.document_processor import DocumentProcessor
from .processing.sec_document_processor import SECFilingProcessor
from .analysis.enhanced_report_summarizer import EnhancedReportSummarizer
from .analysis.financial_flow_analyzer import FinancialFlowAnalyzer
from .embedding.embedding_generator import EmbeddingGenerator
from .analysis.document_analyzer import DocumentAnalyzer
from .processing.table_extractor import FinancialTableExtractor  # Add this new import
from .processing.financial_parsers import FinancialStatementParser  # Add this new import
from .analysis.report_summarizer import ReportSummarizer  # Add this new import
from ..utils.pgvector_db import PgVectorDB
from typing import Dict, Any, List, Optional
import json
import time
import asyncio
import os

class MLManager:
    def __init__(self):
        # Existing initialization
        self.document_processor = DocumentProcessor()
        self.sec_processor = SECFilingProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.document_analyzer = DocumentAnalyzer()
        self.table_extractor = FinancialTableExtractor()
        self.financial_parser = FinancialStatementParser()
        self.report_summarizer = ReportSummarizer()
        
        # New components
        self.enhanced_summarizer = EnhancedReportSummarizer()
        self.flow_analyzer = FinancialFlowAnalyzer()
        
        # Database connection
        self.db = PgVectorDB(
            host='localhost',
            port='5433',  # Using our Docker PostgreSQL port
            dbname='my_project_db',
            user='postgres',
            password=os.environ.get('DB_PASSWORD', 'postgres')  # Use environment variable
        )
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and store it in the database."""
        # Determine if this is a standard document or an SEC filing
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Check if it's potentially an SEC filing (based on filename or content)
        is_sec_filing = self._is_sec_filing(file_path)
        
        if is_sec_filing:
            return self.process_sec_filing(file_path)
        else:
            return self._process_standard_document(file_path)
    
    def process_sec_filing_background(self, file_path: str, document_id: int) -> None:
        """Process an SEC filing in the background."""
        try:
            # Get the document info
            doc_info = self.sec_processor.load_from_file(file_path)
            
            if doc_info.get('status') != 'success':
                print(f"Error loading document: {doc_info.get('message')}")
                return
                
            # Update document content with sections
            if 'sections' in doc_info:
                self.db.update_document(
                    document_id=document_id,
                    content=json.dumps(doc_info['sections'])
                )
            
            # Extract tables from the document
            tables = []
            
            if file_path.endswith('.pdf'):
                tables = self.table_extractor.extract_tables_from_pdf(file_path)
            elif file_path.endswith(('.html', '.htm')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                tables = self.table_extractor.extract_tables_from_html(html_content)
            
            # Process and store tables
            financial_data = {}
            
            for idx, table in enumerate(tables):
                # Clean the table
                clean_table = self.table_extractor.clean_financial_table(table)
                
                # Identify table type
                table_type = self.table_extractor.identify_statement_type(clean_table)
                
                # Parse table based on type
                if table_type == "income_statement":
                    parsed_data = self.financial_parser.parse_income_statement(clean_table)
                    financial_data['income_statement'] = parsed_data
                # Add similar parsing for balance_sheet and cash_flow
            
            # Generate TLDR summary
            tldr_summary = self.report_summarizer.create_tldr(doc_info.get('sections', {}))
            
            # Store sections as chunks for vector search
            chunks = []
            for section_name, section_text in doc_info.get('sections', {}).items():
                section_chunks = self.document_processor.split_document(section_text)
                
                for chunk in section_chunks:
                    # Store the chunk
                    chunk_id = self.db.store_document_chunk(
                        document_id=document_id,
                        chunk_text=f"{section_name}: {chunk['chunk_text']}",
                        chunk_index=len(chunks)
                    )
                    
                    if not chunk_id:
                        continue
                    
                    # Generate embedding for the chunk
                    embedding = self.embedding_generator.generate_embedding(chunk['chunk_text'])
                    
                    # Store the embedding
                    self.db.store_embedding(chunk_id=chunk_id, embedding=embedding)
                    
                    chunks.append(chunk)
            
            # Store analysis results
            self.db.store_analysis_result(
                document_id=document_id,
                analysis_type='sec_filing',
                analysis_result=json.dumps({
                    'financial_data': financial_data,
                    'tldr_summary': tldr_summary,
                    'processing_status': 'complete'
                })
            )
            
            # Clean up the temp file
            if os.path.exists(file_path):
                os.remove(file_path)
                
            print(f"Background processing completed for document {document_id}")
            
        except Exception as e:
            # Log the error
            print(f"Error in background processing: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Clean up the temp file
            if os.path.exists(file_path):
                os.remove(file_path)

    def _is_sec_filing(self, file_path: str) -> bool:
        """Determine if a file is an SEC filing based on name or content."""
        file_name = os.path.basename(file_path).lower()
        
        # Check filename patterns common in SEC filings
        if "10-k" in file_name or "10k" in file_name or "annual" in file_name:
            return True
            
        # For more accurate detection, we could:
        # 1. Check file contents for SEC-specific language
        # 2. Look for EDGAR submission numbers
        # 3. Check for standard SEC form structure
        
        # For now, we'll also treat PDFs as potential SEC filings
        if file_path.endswith('.pdf'):
            return True
            
        return False
    
    def _process_standard_document(self, file_path: str) -> Dict[str, Any]:
        """Process a standard document (non-SEC filing)."""
        # Step 1: Load the document
        doc_info = self.document_processor.load_document(file_path)
        
        if doc_info.get('status') == 'error':
            return doc_info
        
        # Step 2: Store the document in the database
        document_id = self.db.store_document(
            title=doc_info['title'],
            content=doc_info['content'],
            file_type=doc_info['file_type']
        )
        
        if not document_id:
            return {'status': 'error', 'message': 'Failed to store document in database'}
        
        doc_info['id'] = document_id
        
        # Step 3: Split the document into chunks
        chunks = self.document_processor.split_document(doc_info['content'])
        
        # Step 4: Store each chunk and its embedding
        for chunk in chunks:
            # Store the chunk
            chunk_id = self.db.store_document_chunk(
                document_id=document_id,
                chunk_text=chunk['chunk_text'],
                chunk_index=chunk['chunk_index']
            )
            
            if not chunk_id:
                continue
            
            # Generate embedding for the chunk
            embedding = self.embedding_generator.generate_embedding(chunk['chunk_text'])
            
            # Store the embedding
            self.db.store_embedding(chunk_id=chunk_id, embedding=embedding)
        
        # Step 5: Analyze the document
        analysis_result = self.document_analyzer.analyze_document(doc_info)
        
        # Step 6: Store the analysis results
        if analysis_result:
            self.db.store_analysis_result(
                document_id=document_id,
                analysis_type='comprehensive',
                analysis_result=json.dumps(analysis_result)
            )
        
        return {
            'status': 'success',
            'document_id': document_id,
            'title': doc_info['title'],
            'chunks_processed': len(chunks),
            'analysis': analysis_result
        }
    
    def process_sec_filing(self, file_path: str) -> Dict[str, Any]:
        """Process an SEC filing and extract structured data."""
        # Step 1: Load and process the SEC document
        doc_info = self.sec_processor.load_from_file(file_path)
        
        if doc_info.get('status') == 'error':
            return doc_info
        
        # Step 2: Store the document in the database
        document_id = self.db.store_document(
            title=doc_info['title'],
            content=json.dumps(doc_info['sections']),  # Store sections as JSON
            file_type=doc_info.get('file_type', os.path.splitext(file_path)[1])
        )
        
        if not document_id:
            return {'status': 'error', 'message': 'Failed to store document in database'}
        
        # Step 3: Extract tables from the document
        tables = []
        
        if file_path.endswith('.pdf'):
            tables = self.table_extractor.extract_tables_from_pdf(file_path)
        elif file_path.endswith(('.html', '.htm')):
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            tables = self.table_extractor.extract_tables_from_html(html_content)
        
        # Step 4: Process and store tables
        financial_data = {}
        
        for idx, table in enumerate(tables):
            # Clean the table
            clean_table = self.table_extractor.clean_financial_table(table)
            
            # Identify table type
            table_type = self.table_extractor.identify_statement_type(clean_table)
            
            # Parse table based on type
            if table_type == "income_statement":
                parsed_data = self.financial_parser.parse_income_statement(clean_table)
                financial_data['income_statement'] = parsed_data
            # Add similar parsing for balance_sheet and cash_flow
            
            # Store table in database or file system
            # ...
        
        # Step 5: Generate TLDR summary
        tldr_summary = self.report_summarizer.create_tldr(doc_info['sections'])
        
        # Step 6: Store sections as chunks for vector search
        chunks = []
        for section_name, section_text in doc_info['sections'].items():
            section_chunks = self.document_processor.split_document(section_text)
            
            for chunk in section_chunks:
                chunk['section'] = section_name
                chunks.append(chunk)
                
                # Store the chunk
                chunk_id = self.db.store_document_chunk(
                    document_id=document_id,
                    chunk_text=f"{section_name}: {chunk['chunk_text']}",
                    chunk_index=len(chunks) - 1
                )
                
                if not chunk_id:
                    continue
                
                # Generate embedding for the chunk
                embedding = self.embedding_generator.generate_embedding(chunk['chunk_text'])
                
                # Store the embedding
                self.db.store_embedding(chunk_id=chunk_id, embedding=embedding)
        
        # Step 7: Store analysis results
        self.db.store_analysis_result(
            document_id=document_id,
            analysis_type='sec_filing',
            analysis_result=json.dumps({
                'financial_data': financial_data,
                'tldr_summary': tldr_summary
            })
        )
        
        return {
            'status': 'success',
            'document_id': document_id,
            'title': doc_info['title'],
            'sections': list(doc_info['sections'].keys()),
            'tables_extracted': len(tables),
            'chunks_processed': len(chunks),
            'has_financial_data': bool(financial_data),
            'tldr_summary': {
                'length': len(tldr_summary.get('executive_summary', '')),
                'sections': list(tldr_summary.get('sections', {}).keys())
            }
        }
    
    def search_similar_documents(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for documents similar to the query text."""
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_embedding(query_text)
        
        # Search for similar chunks
        similar_chunks = self.db.search_similar_chunks(
            query_embedding=query_embedding,
            limit=limit
        )
        
        return similar_chunks
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a text without storing it in the database."""
        return self.document_analyzer.analyze_document({'content': text})
    
    def get_financial_summary(self, document_id: int) -> Dict[str, Any]:
        """Get financial summary for a specific document."""
        # Retrieve the document analysis
        analysis_results = self.db.get_analysis_results(document_id, 'sec_filing')
        
        if not analysis_results:
            return {'status': 'error', 'message': 'No financial data found for this document'}
        
        # Parse the stored analysis
        try:
            financial_data = json.loads(analysis_results[0]['analysis_result'])
            return {
                'status': 'success',
                'financial_data': financial_data.get('financial_data', {}),
                'summary': financial_data.get('tldr_summary', {})
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Error parsing financial data: {str(e)}'}
    
    def answer_question(self, document_id: int, question: str) -> Dict[str, Any]:
        """Answer a question about a specific document."""
        # TODO: Implement retrieval of document by ID
        # For now, we'll return a placeholder
        return {
            'status': 'error',
            'message': 'Not implemented yet'
        }
    
    def get_document_sections(self, document_id: int) -> Dict[str, str]:
        """Get document sections for a specific document."""
        try:
            # Get document content
            document = self.db.get_document(document_id)
            
            if not document:
                return {}
            
            # Try to parse content as JSON (sections)
            try:
                sections = json.loads(document['content'])
                if isinstance(sections, dict):
                    return sections
            except (json.JSONDecodeError, TypeError):
                # Content is not JSON, treat as a single section
                return {"full_document": document['content']}
                
            return {}
        except Exception as e:
            print(f"Error getting document sections: {str(e)}")
            return {}

    def create_enhanced_tldr(self, document_id: int) -> Dict[str, Any]:
        """Create an enhanced TLDR summary for a document."""
        try:
            # Get document sections
            sections = self.get_document_sections(document_id)
            
            if not sections:
                return {
                    "status": "error", 
                    "message": "No document content available for TLDR generation"
                }
            
            # Generate the enhanced TLDR
            tldr = self.enhanced_summarizer.create_extended_tldr(sections)
            
            # Store the TLDR in the database
            self.db.store_analysis_result(
                document_id=document_id,
                analysis_type='enhanced_tldr',
                analysis_result=json.dumps(tldr)
            )
            
            return {
                "status": "success",
                "document_id": document_id,
                "extended_tldr": tldr
            }
        except Exception as e:
            print(f"Error creating enhanced TLDR: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate enhanced TLDR: {str(e)}"
            }

    def generate_financial_flow(self, document_id: int) -> Dict[str, Any]:
        """Generate financial flow data for Sankey diagram."""
        try:
            # Get financial data
            financial_summary = self.get_financial_summary(document_id)
            
            if financial_summary.get('status') == 'error':
                return financial_summary
            
            # Generate Sankey diagram data
            flow_data = self.flow_analyzer.generate_sankey_data(
                financial_summary.get('financial_data', {})
            )
            
            # Generate insights about the financial flows
            insights = self.flow_analyzer.generate_flow_insights(
                financial_summary.get('financial_data', {})
            )
            
            # Store the flow data in the database
            self.db.store_analysis_result(
                document_id=document_id,
                analysis_type='financial_flow',
                analysis_result=json.dumps({
                    "flow_data": flow_data,
                    "insights": insights
                })
            )
            
            return {
                "status": "success",
                "document_id": document_id,
                "flow_data": flow_data,
                "insights": insights
            }
        except Exception as e:
            print(f"Error generating financial flow: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate financial flow: {str(e)}"
            }

    def process_document_background(self, document_id: int) -> None:
        """Process a document in the background with progress tracking."""
        try:
            # Update status to processing
            self.db.update_processing_status(
                document_id=document_id, 
                status="parsing",
                message="Extracting document content"
            )
            
            # Get document info
            document = self.db.get_document(document_id)
            if not document:
                self.db.update_processing_status(
                    document_id=document_id,
                    status="error",
                    message="Document not found"
                )
                return
            
            # Step 1: Process document content
            time.sleep(2)  # Simulate processing time
            
            # Update status
            self.db.update_processing_status(
                document_id=document_id,
                status="analyzing",
                message="Analyzing document content"
            )
            
            # Step 2: Generate embeddings and analyze document
            time.sleep(3)  # Simulate processing time
            
            # Update status
            self.db.update_processing_status(
                document_id=document_id,
                status="generating_visualizations",
                message="Generating visualizations"
            )
            
            # Step 3: Generate TLDR and financial flow
            try:
                self.create_enhanced_tldr(document_id)
                self.generate_financial_flow(document_id)
            except Exception as e:
                print(f"Error in visualization generation: {str(e)}")
                # Continue processing even if visualizations fail
                
            # Update status to complete
            self.db.update_processing_status(
                document_id=document_id,
                status="complete",
                message="Document processing complete"
            )
            
        except Exception as e:
            print(f"Error in background processing: {str(e)}")
            
            # Update status to error
            self.db.update_processing_status(
                document_id=document_id,
                status="error",
                message=f"Error processing document: {str(e)}"
            )