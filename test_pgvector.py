from src.utils.pgvector_db import PgVectorDB
import numpy as np

def test_pgvector_connection():
    # Initialize the database connection
    db = PgVectorDB(
        host='localhost',
        port='5433',  # Use 5433 if using Docker, 5432 if using local PostgreSQL
        dbname='my_project_db',
        user='postgres',
        password='Ishinehere1'
    )
    
    # Test connection
    conn = db.get_connection()
    if conn:
        print("✅ Successfully connected to PostgreSQL with pgvector")
        conn.close()
    else:
        print("❌ Failed to connect to PostgreSQL")
        return False
    
    # Test document storage
    document_id = db.store_document(
        title="Test Document",
        content="This is a test document for pgvector.",
        file_type="text"
    )
    
    if document_id:
        print(f"✅ Successfully stored document with ID: {document_id}")
    else:
        print("❌ Failed to store document")
        return False
    
    # Test chunk storage
    chunk_id = db.store_document_chunk(
        document_id=document_id,
        chunk_text="This is a test chunk for pgvector.",
        chunk_index=0
    )
    
    if chunk_id:
        print(f"✅ Successfully stored document chunk with ID: {chunk_id}")
    else:
        print("❌ Failed to store document chunk")
        return False
    
    # Test embedding storage
    # Generate a random 768-dimensional vector (typical for embedding models)
    test_embedding = np.random.rand(768).astype(np.float32)
    
    embedding_id = db.store_embedding(
        chunk_id=chunk_id,
        embedding=test_embedding
    )
    
    if embedding_id:
        print(f"✅ Successfully stored embedding with ID: {embedding_id}")
    else:
        print("❌ Failed to store embedding")
        return False
    
    # Test similarity search
    # Create a slightly modified version of the same embedding
    query_embedding = test_embedding + np.random.normal(0, 0.01, 768).astype(np.float32)
    
    similar_chunks = db.search_similar_chunks(
        query_embedding=query_embedding,
        limit=5
    )
    
    if similar_chunks and len(similar_chunks) > 0:
        print(f"✅ Successfully retrieved {len(similar_chunks)} similar chunks")
        print(f"   First result: {similar_chunks[0]['chunk_text']}")
    else:
        print("❌ Failed to retrieve similar chunks")
        return False
    
    print("✅ All pgvector tests passed successfully!")
    return True

if __name__ == "__main__":
    test_pgvector_connection()
