from transformers import pipeline
import json
from typing import Dict, Any, List

class DocumentAnalyzer:
    def __init__(self):
        # Initialize the text classification pipeline
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        # Initialize the summarization pipeline
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            max_length=150,
            min_length=30
        )
        
        # Initialize the question answering pipeline
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad"
        )
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment of a text."""
        try:
            # For longer texts, truncate to avoid token limits
            truncated_text = text[:1000] if len(text) > 1000 else text
            
            result = self.sentiment_analyzer(truncated_text)[0]
            return {
                'label': result['label'],
                'score': float(result['score']),
                'analysis_type': 'sentiment'
            }
        except Exception as e:
            return {
                'error': str(e),
                'analysis_type': 'sentiment'
            }
    
    def generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate a summary of the text."""
        try:
            # Ensure text is not too short for summarization
            if len(text) < 100:
                return {
                    'summary': text,
                    'analysis_type': 'summary',
                    'note': 'Text too short for summarization'
                }
            
            # For longer texts, process in chunks if needed
            if len(text) > 1000:
                text = text[:1000]
                
            result = self.summarizer(text)[0]
            return {
                'summary': result['summary_text'],
                'analysis_type': 'summary'
            }
        except Exception as e:
            return {
                'error': str(e),
                'analysis_type': 'summary'
            }
    
    def extract_topics(self, text: str) -> Dict[str, Any]:
        """Extract main topics from the text using keyword extraction."""
        try:
            # This is a simple keyword frequency-based approach
            # In a real system, you might use a topic modeling approach like LDA
            words = text.lower().split()
            
            # Remove common stopwords
            stopwords = ['the', 'a', 'an', 'and', 'in', 'on', 'at', 'of', 'to', 'for', 'with', 'is', 'are']
            filtered_words = [word for word in words if word not in stopwords and len(word) > 3]
            
            # Count frequencies
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'topics': [{'word': word, 'frequency': freq} for word, freq in top_words],
                'analysis_type': 'topics'
            }
        except Exception as e:
            return {
                'error': str(e),
                'analysis_type': 'topics'
            }
    
    def answer_question(self, context: str, question: str) -> Dict[str, Any]:
        """Answer a question based on the document context."""
        try:
            result = self.qa_pipeline(question=question, context=context)
            return {
                'answer': result['answer'],
                'confidence': float(result['score']),
                'analysis_type': 'question_answering'
            }
        except Exception as e:
            return {
                'error': str(e),
                'analysis_type': 'question_answering'
            }
    
    def analyze_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive analysis on a document."""
        content = document.get('content', '')
        
        # Run different analyses
        sentiment = self.analyze_sentiment(content)
        summary = self.generate_summary(content)
        topics = self.extract_topics(content)
        
        # Combine results
        analysis_result = {
            'document_id': document.get('id'),
            'title': document.get('title'),
            'sentiment': sentiment,
            'summary': summary,
            'topics': topics
        }
        
        return analysis_result
