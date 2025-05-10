from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from ...models.ml_manager import MLManager
import os
import uuid
import shutil
from datetime import datetime

router = APIRouter()

def get_ml_manager():
    return MLManager()

@router.post("/upload-file/")
async def upload_document_new(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    ml_manager: MLManager = Depends(get_ml_manager)
):
    """A simpler implementation of document upload to isolate the issue"""
    
    # Create a temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    temp_file_path = f"temp/{str(uuid.uuid4())}{file_extension}"
    
    try:
        # Save the uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Begin with just a basic document save
        is_sec_filing = ml_manager._is_sec_filing(temp_file_path)
        
        if is_sec_filing:
            # For SEC filings, do minimal processing now
            doc_info = ml_manager.sec_processor.load_from_file(temp_file_path)
            
            if doc_info.get('status') != 'success':
                raise HTTPException(status_code=400, detail=doc_info.get('message', 'Failed to process document'))
            
            # Store the document quickly
            document_id = ml_manager.db.store_document(
                title=doc_info['title'],
                content=doc_info.get('content', ''),
                file_type=file_extension
            )
            
            if not document_id:
                raise HTTPException(status_code=500, detail="Failed to store document")
            
            # Process in background if background_tasks is available
            if background_tasks:
                background_tasks.add_task(
                    ml_manager.process_sec_filing_background, 
                    temp_file_path, 
                    document_id
                )
            
            # Return immediately with the document ID
            return {
                "id": document_id,
                "title": doc_info['title'],
                "upload_time": str(datetime.now()),
                "processing_status": "processing"
            }
        else:
            # Regular document processing
            result = ml_manager.process_document(temp_file_path)
            return result
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")