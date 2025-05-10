from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add project root to sys.path
sys.path.insert(0, project_root)

from src.api.router import api_router

app = FastAPI(
    title="Document Analysis API",
    description="API for analyzing documents using ML",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the API router
app.include_router(api_router, prefix="/api")

# Create a temp directory for file uploads if it doesn't exist
os.makedirs("temp", exist_ok=True)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Document Analysis API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)