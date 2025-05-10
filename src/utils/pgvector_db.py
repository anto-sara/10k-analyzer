import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from typing import Dict, Any, List, Optional

class PgVectorDB:
    def __init__(self, host='localhost', port='5433', # Use 5433 for Docker, 5432 for local
                dbname='my_project_db', user='postgres', password='Ishinehere1'):
        self.connection_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password
        }
    
    def get_connection(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            conn = psycopg2.connect(**self.connection_params, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def store_document(self, title, content, file_type):
        """Store a document in the database."""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents (title, content, file_type) VALUES (%s, %s, %s) RETURNING id;",
                (title, content, file_type)
            )
            document_id = cursor.fetchone()['id']
            conn.commit()
            return document_id
        except Exception as e:
            conn.rollback()
            print(f"Error storing document: {e}")
            return None
        finally:
            conn.close()
    
    def store_document_chunk(self, document_id, chunk_text, chunk_index):
        """Store a document chunk in the database."""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO document_chunks (document_id, chunk_text, chunk_index) VALUES (%s, %s, %s) RETURNING id;",
                (document_id, chunk_text, chunk_index)
            )
            chunk_id = cursor.fetchone()['id']
            conn.commit()
            return chunk_id
        except Exception as e:
            conn.rollback()
            print(f"Error storing document chunk: {e}")
            return None
        finally:
            conn.close()
    
    def store_embedding(self, chunk_id, embedding):
        """Store an embedding vector for a document chunk."""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            # Convert numpy array to PostgreSQL vector format
            vector_str = f"[{','.join(str(x) for x in embedding)}]"
            
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO document_embeddings (chunk_id, embedding) VALUES (%s, %s) RETURNING id;",
                (chunk_id, vector_str)
            )
            embedding_id = cursor.fetchone()['id']
            conn.commit()
            return embedding_id
        except Exception as e:
            conn.rollback()
            print(f"Error storing embedding: {e}")
            return None
        finally:
            conn.close()
    
    def search_similar_chunks(self, query_embedding, limit=5):
        """Find similar document chunks based on embedding similarity."""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            # Convert numpy array to PostgreSQL vector format
            vector_str = f"[{','.join(str(x) for x in query_embedding)}]"
            
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT dc.chunk_text, dc.document_id, d.title, 
                       de.embedding <-> %s::vector AS distance
                FROM document_embeddings de
                JOIN document_chunks dc ON de.chunk_id = dc.id
                JOIN documents d ON dc.document_id = d.id
                ORDER BY distance ASC
                LIMIT %s;
                """,
                (vector_str, limit)
            )
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            return []
        finally:
            conn.close()
    
    def store_analysis_result(self, document_id, analysis_type, analysis_result):
        """Store analysis results for a document."""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO document_analyses (document_id, analysis_type, analysis_result) VALUES (%s, %s, %s) RETURNING id;",
                (document_id, analysis_type, analysis_result)
            )
            analysis_id = cursor.fetchone()['id']
            conn.commit()
            return analysis_id
        except Exception as e:
            conn.rollback()
            print(f"Error storing analysis result: {e}")
            return None
        finally:
            conn.close()
    
    def update_document(self, document_id: int, content: str = None, title: str = None) -> bool:
        """Update a document in the database."""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            update_parts = []
            params = []
            
            if content is not None:
                update_parts.append("content = %s")
                params.append(content)
            
            if title is not None:
                update_parts.append("title = %s")
                params.append(title)
            
            if not update_parts:
                return False  # Nothing to update
            
            params.append(document_id)
            
            query = f"UPDATE documents SET {', '.join(update_parts)} WHERE id = %s"
            cursor.execute(query, params)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating document: {e}")
            return False
        
    def get_analysis_results(self, document_id: int, analysis_type: str = None) -> List[Dict[str, Any]]:
        """Get analysis results for a document."""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if analysis_type:
                cursor.execute(
                    "SELECT * FROM document_analyses WHERE document_id = %s AND analysis_type = %s",
                    (document_id, analysis_type)
                )
            else:
                cursor.execute(
                    "SELECT * FROM document_analyses WHERE document_id = %s",
                    (document_id,)
                )
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return list(results)
        except Exception as e:
            print(f"Error getting analysis results: {e}")
            return []

def update_processing_status(self, document_id: int, status: str, message: str = None, error: str = None) -> bool:
    """Update document processing status and add to history."""
    try:
        # Update document status
        query = """
            UPDATE documents 
            SET 
                processing_status = %s, 
                processing_message = %s,
                processing_error = %s,
                processing_completed_at = CASE WHEN %s = 'complete' OR %s = 'error' THEN NOW() ELSE NULL END
            WHERE id = %s
        """
        self.cursor.execute(query, (status, message, error, status, status, document_id))
        
        # Add to processing history
        history_query = """
            INSERT INTO processing_history (document_id, status, message, error)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(history_query, (document_id, status, message, error))
        
        self.conn.commit()
        return True
    except Exception as e:
        print(f"Error updating processing status: {str(e)}")
        self.conn.rollback()
        return False

def get_processing_status(self, document_id: int) -> Dict[str, Any]:
    """Get current processing status for a document."""
    try:
        query = """
            SELECT 
                processing_status,
                processing_message,
                processing_error,
                processing_started_at,
                processing_completed_at
            FROM 
                documents
            WHERE 
                id = %s
        """
        self.cursor.execute(query, (document_id,))
        result = self.cursor.fetchone()
        
        if not result:
            return None
            
        return {
            "status": result[0],
            "message": result[1],
            "error": result[2],
            "started_at": result[3],
            "completed_at": result[4]
        }
    except Exception as e:
        print(f"Error getting processing status: {str(e)}")
        return None

def get_document_history(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Get history of document processing."""
    try:
        query = """
            SELECT 
                d.id, 
                d.title, 
                d.file_type, 
                d.created_at,
                d.processing_status,
                d.content
            FROM 
                documents d
            ORDER BY 
                d.created_at DESC
            LIMIT %s OFFSET %s
        """
        self.cursor.execute(query, (limit, offset))
        results = self.cursor.fetchall()
        
        history = []
        for row in results:
            history.append({
                "id": row[0],
                "title": row[1],
                "file_type": row[2],
                "created_at": row[3],
                "processing_status": row[4],
                "content": row[5]
            })
            
        return history
    except Exception as e:
        print(f"Error getting document history: {str(e)}")
        return []

def get_document(self, document_id: int) -> Dict[str, Any]:
    """Get document by ID."""
    try:
        query = """
            SELECT 
                id, 
                title, 
                content, 
                file_type, 
                created_at,
                processing_status
            FROM 
                documents
            WHERE 
                id = %s
        """
        self.cursor.execute(query, (document_id,))
        result = self.cursor.fetchone()
        
        if not result:
            return None
            
        return {
            "id": result[0],
            "title": result[1],
            "content": result[2],
            "file_type": result[3],
            "created_at": result[4],
            "processing_status": result[5]
        }
    except Exception as e:
        print(f"Error getting document: {str(e)}")
        return None