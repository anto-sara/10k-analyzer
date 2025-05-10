from src.models.ml_manager import MLManager
from src.models.embedding.embedding_generator import EmbeddingGenerator
from src.models.analysis.document_analyzer import DocumentAnalyzer
import os
import time

def test_embedding_generator():
    print('\n===== Testing Embedding Generator =====')
    
    try:
        # Initialize the embedding generator
        print('Initializing embedding generator...')
        embedding_gen = EmbeddingGenerator()
        print(f'✅ Embedding generator initialized with model: {embedding_gen.model_name}')
        
        # Generate an embedding
        text = "This is a test sentence for generating embeddings."
        print(f'Generating embedding for: "{text}"')
        
        start_time = time.time()
        embedding = embedding_gen.generate_embedding(text)
        end_time = time.time()
        
        print(f'✅ Generated embedding with shape: {embedding.shape}')
        print(f'✅ Embedding generation time: {end_time - start_time:.2f} seconds')
        
        return True
    except Exception as e:
        print(f'❌ Error in embedding generator test: {str(e)}')
        return False

def test_document_analyzer():
    print('\n===== Testing Document Analyzer =====')
    
    try:
        # Initialize the document analyzer
        print('Initializing document analyzer...')
        analyzer = DocumentAnalyzer()
        print('✅ Document analyzer initialized')
        
        # Test with a sample text
        text = "This project is amazing! I'm very happy with the progress we've made so far. The technology stack is robust and the implementation is clean."
        
        # Test sentiment analysis
        print('Testing sentiment analysis...')
        sentiment = analyzer.analyze_sentiment(text)
        print(f'✅ Sentiment analysis result: {sentiment["label"]} with confidence {sentiment["score"]:.4f}')
        
        # Test summarization
        print('Testing summarization...')
        summary = analyzer.generate_summary(text)
        print(f'✅ Summary: {summary.get("summary", "No summary generated")}')
        
        # Test topic extraction
        print('Testing topic extraction...')
        topics = analyzer.extract_topics(text)
        print(f'✅ Extracted topics: {[topic["word"] for topic in topics.get("topics", [])]}')
        
        return True
    except Exception as e:
        print(f'❌ Error in document analyzer test: {str(e)}')
        return False

def main():
    print('===== Testing ML Layer =====')
    
    # Create a sample text file for testing
    sample_file_path = "test_document.txt"
    with open(sample_file_path, 'w') as f:
        f.write("""
        # Document Analysis System
        
        This is a test document for our AI-powered document analysis system. 
        The system uses machine learning to analyze documents, extract insights, and visualize the results.
        
        ## Features
        
        - Document processing and chunking
        - Embedding generation using transformer models
        - Vector similarity search with pgvector
        - Sentiment analysis and summarization
        - Topic extraction and visualization
        
        We're excited about the possibilities this system offers for document understanding and knowledge extraction.
        """)
    
    # Test individual components
    embedding_test = test_embedding_generator()
    analyzer_test = test_document_analyzer()
    
    if embedding_test and analyzer_test:
        print('\n===== Testing Full ML Pipeline =====')
        
        try:
            # Initialize the ML manager
            print('Initializing ML manager...')
            ml_manager = MLManager()
            print('✅ ML manager initialized')
            
            # Process the document
            print(f'Processing document: {sample_file_path}')
            result = ml_manager.process_document(sample_file_path)
            
            if result.get('status') == 'success':
                print(f'✅ Document processed successfully')
                print(f'✅ Document ID: {result.get("document_id")}')
                print(f'✅ Chunks processed: {result.get("chunks_processed")}')
                
                # Test search
                query = "machine learning for document analysis"
                print(f'Searching for: "{query}"')
                similar_chunks = ml_manager.search_similar_documents(query)
                
                if similar_chunks:
                    print(f'✅ Found {len(similar_chunks)} similar chunks')
                    print(f'   Top result: "{similar_chunks[0]["chunk_text"][:100]}..."')
                else:
                    print('❌ No similar chunks found')
                
                print('\n✅ All ML tests completed successfully!')
            else:
                print(f'❌ Document processing failed: {result.get("message")}')
        except Exception as e:
            print(f'❌ Error in ML pipeline test: {str(e)}')
    
    # Clean up
    if os.path.exists(sample_file_path):
        os.remove(sample_file_path)

if __name__ == "__main__":
    main()

