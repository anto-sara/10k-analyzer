import psycopg2

def create_schema():
    conn = psycopg2.connect(
        host="localhost",
        port="5433",  # Use the port from your MLManager
        database="my_project_db",
        user="postgres",
        password="Ishinehere1"  # Replace with your actual password
    )
    
    try:
        with conn.cursor() as cursor:
            # Create tables and add columns
            cursor.execute("""
                -- Create the documents table if it doesn't exist
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    file_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Add processing columns
                ALTER TABLE documents 
                ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'complete',
                ADD COLUMN IF NOT EXISTS processing_message TEXT,
                ADD COLUMN IF NOT EXISTS processing_error TEXT,
                ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP;
                
                -- Create other tables
                CREATE TABLE IF NOT EXISTS processing_history (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    status VARCHAR(50) NOT NULL,
                    message TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    analysis_type VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indices
                CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);
                CREATE INDEX IF NOT EXISTS idx_processing_history_document_id ON processing_history(document_id);
                CREATE INDEX IF NOT EXISTS idx_analysis_history_document_id ON analysis_history(document_id);
            """)
            
            conn.commit()
            print("Schema created successfully")
    except Exception as e:
        print(f"Error creating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_schema()