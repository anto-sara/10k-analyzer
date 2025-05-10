from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...models.analysis.enhanced_report_summarizer import EnhancedReportSummarizer
from ...models.analysis.financial_flow_analyzer import FinancialFlowAnalyzer
from ...models.ml_manager import MLManager

# Models for request/response
class AnalysisHistoryResponse(BaseModel):
    id: int
    title: str
    file_type: str
    created_at: str
    sections: Optional[List[str]] = None
    processing_status: str

class ProcessingStatusResponse(BaseModel):
    status: str
    progress: int
    message: Optional[str] = None
    error: Optional[str] = None

class FinancialFlowResponse(BaseModel):
    status: str
    document_id: int
    flow_data: Dict[str, Any]
    insights: Optional[Dict[str, Any]] = None

class ExtendedTLDRResponse(BaseModel):
    status: str
    document_id: int
    extended_tldr: Dict[str, Any]

# Create router
router = APIRouter()

# Create service instances
def get_ml_manager():
    return MLManager()

def get_enhanced_summarizer():
    return EnhancedReportSummarizer()

def get_flow_analyzer():
    return FinancialFlowAnalyzer()

# Endpoint to get processing status
@router.get("/processing-status/{document_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    document_id: int,
    ml_manager: MLManager = Depends(get_ml_manager)
):
    """Get the current processing status of a document"""
    try:
        # Check status in database
        status = ml_manager.db.get_processing_status(document_id)
        
        if not status:
            return ProcessingStatusResponse(
                status="not_found",
                progress=0,
                message="Document not found"
            )
        
        # Convert status to progress percentage
        progress = 0
        if status["status"] == "uploaded":
            progress = 10
        elif status["status"] == "parsing":
            progress = 30
        elif status["status"] == "analyzing":
            progress = 50
        elif status["status"] == "generating_visualizations":
            progress = 80
        elif status["status"] == "complete":
            progress = 100
        elif status["status"] == "error":
            progress = 0
        
        return ProcessingStatusResponse(
            status=status["status"],
            progress=progress,
            message=status.get("message", ""),
            error=status.get("error", None)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking processing status: {str(e)}")

# Endpoint to get analysis history
@router.get("/analysis-history/", response_model=List[AnalysisHistoryResponse])
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    ml_manager: MLManager = Depends(get_ml_manager)
):
    """Get history of previous document analyses"""
    try:
        # Get history from database
        history_entries = ml_manager.db.get_document_history(limit, offset)
        
        # Format response
        formatted_history = []
        for entry in history_entries:
            # Get section names if available
            sections = []
            try:
                if entry.get("content"):
                    content_data = json.loads(entry["content"])
                    if isinstance(content_data, dict):
                        sections = list(content_data.keys())
            except:
                pass
            
            formatted_history.append(AnalysisHistoryResponse(
                id=entry["id"],
                title=entry["title"],
                file_type=entry["file_type"],
                created_at=entry["created_at"].isoformat() if entry.get("created_at") else "",
                sections=sections,
                processing_status=entry.get("processing_status", "complete")
            ))
        
        return formatted_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis history: {str(e)}")

# Endpoint to get financial flow for Sankey diagram
@router.get("/financial-flow/{document_id}", response_model=FinancialFlowResponse)
async def get_financial_flow(
    document_id: int,
    flow_analyzer: FinancialFlowAnalyzer = Depends(get_flow_analyzer),
    ml_manager: MLManager = Depends(get_ml_manager)
):
    """Get financial flow data for Sankey diagram visualization"""
    try:
        # Get financial data from ML manager
        financial_summary = ml_manager.get_financial_summary(document_id)
        
        if financial_summary.get('status') == 'error':
            raise HTTPException(status_code=404, detail=financial_summary.get('message'))
        
        # Generate Sankey diagram data
        flow_data = flow_analyzer.generate_sankey_data(financial_summary.get('financial_data', {}))
        
        # Generate insights about the financial flows
        insights = flow_analyzer.generate_flow_insights(financial_summary.get('financial_data', {}))
        
        return FinancialFlowResponse(
            status="success",
            document_id=document_id,
            flow_data=flow_data,
            insights=insights
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate financial flow: {str(e)}")

# Endpoint to get extended TLDR summary
@router.get("/extended-tldr/{document_id}", response_model=ExtendedTLDRResponse)
async def get_extended_tldr(
    document_id: int,
    summarizer: EnhancedReportSummarizer = Depends(get_enhanced_summarizer),
    ml_manager: MLManager = Depends(get_ml_manager)
):
    """Get enhanced and extended TLDR summary"""
    try:
        # Get document sections from the database
        document = ml_manager.db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail=f"Document not found with ID {document_id}")
        
        # Extract sections from document content
        sections = {}
        try:
            content = document.get("content", "{}")
            sections = json.loads(content)
        except json.JSONDecodeError:
            # If not valid JSON, treat as a single section
            sections = {"full_content": content}
        
        if not sections:
            raise HTTPException(status_code=404, detail=f"Document sections not found for ID {document_id}")
        
        # Generate extended TLDR
        extended_tldr = summarizer.create_extended_tldr(sections)
        
        return ExtendedTLDRResponse(
            status="success",
            document_id=document_id,
            extended_tldr=extended_tldr
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate extended TLDR: {str(e)}")

# Add an endpoint to analyze document in background (for longer processes)
@router.post("/analyze-background/{document_id}")
async def analyze_document_background(
    document_id: int,
    background_tasks: BackgroundTasks,
    ml_manager: MLManager = Depends(get_ml_manager)
):
    """Start a background analysis task for a document"""
    try:
        # Check if document exists
        document = ml_manager.db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail=f"Document not found with ID {document_id}")
        
        # Update status to processing
        ml_manager.db.update_processing_status(
            document_id=document_id,
            status="parsing",
            message="Document analysis started in background"
        )
        
        # Add task to background
        background_tasks.add_task(ml_manager.process_document_background, document_id)
        
        return {
            "status": "success",
            "message": "Background analysis started",
            "document_id": document_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start background analysis: {str(e)}")