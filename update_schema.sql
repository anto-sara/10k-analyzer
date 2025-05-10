-- Drop existing table and its dependencies
DROP TABLE IF EXISTS document_embeddings CASCADE;

-- Create the table with the correct dimensions
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(384), -- 384 dimensions for all-MiniLM-L6-v2 model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index for fast similarity search
CREATE INDEX document_embeddings_idx ON document_embeddings USING ivfflat (embedding vector_l2_ops);
