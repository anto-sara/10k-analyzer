from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    content: str
    file_type: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    upload_time: datetime
    
    class Config:
        from_attributes = True

class DocumentChunk(BaseModel):
    id: int
    document_id: int
    chunk_text: str
    chunk_index: int
    
    class Config:
        from_attributes = True

class EmbeddingResponse(BaseModel):
    id: int
    chunk_id: int
    
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    chunk_text: str
    document_id: int
    document_title: str
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

class AnalysisRequest(BaseModel):
    document_id: Optional[int] = None
    text: Optional[str] = None

class SentimentResponse(BaseModel):
    label: str
    score: float
    analysis_type: str = "sentiment"

class SummaryResponse(BaseModel):
    summary: str
    analysis_type: str = "summary"

class TopicItem(BaseModel):
    word: str
    frequency: int

class TopicsResponse(BaseModel):
    topics: List[TopicItem]
    analysis_type: str = "topics"

class AnalysisResponse(BaseModel):
    document_id: Optional[int] = None
    title: Optional[str] = None
    sentiment: SentimentResponse
    summary: SummaryResponse
    topics: TopicsResponse
