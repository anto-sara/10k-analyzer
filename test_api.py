import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def test_api_root():
    print("Testing API root...")
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        print("✅ API root accessible")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ API root failed: {response.status_code}")
    print()

def test_document_upload():
    print("Testing document upload...")
    
    # Create a test document if it doesn't exist
    test_file_path = "test_document.txt"
    if not os.path.exists(test_file_path):
        with open(test_file_path, "w") as f:
            f.write("""
            # Document Analysis Test
            
            This is a test document for the API endpoint. 
            It contains some sample text that will be processed by the document analysis system.
            
            The system should:
            1. Extract the content
            2. Split it into chunks
            3. Generate embeddings
            4. Store everything in the database
            
            Let's see if it works!
            """)
    
    # Upload the document
    with open(test_file_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/documents/upload/",
            files={"file": (os.path.basename(test_file_path), f)}
        )
    
    if response.status_code == 200:
        print("✅ Document upload successful")
        print(f"Response: {response.json()}")
        document_id = response.json().get("id")
        return document_id
    else:
        print(f"❌ Document upload failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def test_document_search(query="document analysis", limit=3):
    print(f"Testing document search with query: '{query}'...")
    
    payload = {
        "query": query,
        "limit": limit
    }
    
    response = requests.post(
        f"{BASE_URL}/documents/search/",
        json=payload
    )
    
    if response.status_code == 200:
        print("✅ Document search successful")
        results = response.json().get("results", [])
        print(f"Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Document ID: {result['document_id']}")
            print(f"  Document Title: {result['document_title']}")
            print(f"  Distance: {result['distance']}")
            print(f"  Text: {result['chunk_text'][:100]}...")
    else:
        print(f"❌ Document search failed: {response.status_code}")
        print(f"Error: {response.text}")

def test_text_analysis(text="This document analysis system is amazing! It provides great insights into text content."):
    print("Testing text analysis...")
    
    payload = {
        "text": text
    }
    
    response = requests.post(
        f"{BASE_URL}/documents/analyze/",
        json=payload
    )
    
    if response.status_code == 200:
        print("✅ Text analysis successful")
        result = response.json()
        print(f"Sentiment: {result['sentiment']['label']} ({result['sentiment']['score']:.4f})")
        print(f"Summary: {result['summary']['summary']}")
        print(f"Topics: {', '.join([topic['word'] for topic in result['topics']['topics']])}")
    else:
        print(f"❌ Text analysis failed: {response.status_code}")
        print(f"Error: {response.text}")

def main():
    print("===== Testing Document Analysis API =====\n")
    
    # Test API root
    test_api_root()
    
    # Test document upload
    document_id = test_document_upload()
    print()
    
    # Test document search
    if document_id:
        test_document_search()
        print()
    
    # Test text analysis
    test_text_analysis()
    print()
    
    print("===== API Testing Complete =====")

if __name__ == "__main__":
    main()
