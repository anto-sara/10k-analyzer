from fastapi import APIRouter
from .endpoints import documents, enhanced_analysis

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(enhanced_analysis.router, prefix="/documents", tags=["enhanced-analysis"])