import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

function FinancialReportUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
  };

  // Handle file upload
  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const result = await api.uploadDocument(file);
      setUploadResult(result);
      
      // Initialize processing status
      if (result.processing_status === "background") {
        setProcessingStatus("processing");
      } else {
        setProcessingStatus("complete");
      }
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading document');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Set up polling for background processing
  useEffect(() => {
    if (uploadResult && uploadResult.processing_status === "background") {
      // Start polling for processing status
      const interval = setInterval(async () => {
        try {
          const status = await api.getProcessingStatus(uploadResult.id);
          setProcessingStatus(status.status);
          
          if (status.status === "complete" || status.status === "error") {
            // Stop polling when processing is complete or failed
            clearInterval(interval);
            setPollingInterval(null);
            
            // Refresh document details if processing is complete
            if (status.status === "complete") {
              try {
                const docDetails = await api.getFinancialSummary(uploadResult.id);
                if (docDetails) {
                  setUploadResult({
                    ...uploadResult,
                    document_id: uploadResult.id,
                    sections: Object.keys(docDetails.financial_data || {}),
                    tables_extracted: Object.keys(docDetails.financial_data || {}).length
                  });
                }
              } catch (err) {
                console.error("Error fetching updated document details:", err);
              }
            }
          }
        } catch (err) {
          console.error("Error checking processing status:", err);
        }
      }, 5000); // Check every 5 seconds
      
      setPollingInterval(interval);
      
      return () => {
        if (interval) clearInterval(interval);
      };
    }
  }, [uploadResult]);

  return (
    <div className="upload-container">
      <h2>Upload Financial Report (10-K)</h2>
      <div className="upload-description">
        <p>Upload SEC filings or financial reports for specialized analysis.</p>
        <p>Supported formats: PDF, HTML</p>
      </div>
      
      <form onSubmit={handleUpload}>
        <div className="form-group">
          <label htmlFor="financial-report-file">Select Financial Report:</label>
          <input 
            type="file" 
            id="financial-report-file" 
            onChange={handleFileChange}
            accept=".pdf,.html,.htm"
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !file}
          className="upload-button"
        >
          {loading ? 'Processing...' : 'Upload & Analyze Report'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {uploadResult && (
        <div className="success-message">
          <h3>Financial Report {processingStatus === "complete" ? "Processed" : "Uploaded"} Successfully!</h3>
          <p><strong>Document ID:</strong> {uploadResult.id || uploadResult.document_id}</p>
          <p><strong>Title:</strong> {uploadResult.title}</p>
          
          {processingStatus === "processing" && (
            <div className="processing-status">
              <p>Processing document in background... This may take a few minutes.</p>
              <div className="progress-indicator">
                <div className="progress-bar"></div>
              </div>
              <p className="processing-tip">You can leave this page and come back later. Your document will continue processing.</p>
            </div>
          )}
          
          {processingStatus === "complete" && (
            <>
              {uploadResult.sections && uploadResult.sections.length > 0 && (
                <div>
                  <p><strong>Sections Extracted:</strong> {uploadResult.sections.length}</p>
                  <ul className="section-list">
                    {uploadResult.sections.map((section, index) => (
                      <li key={index}>{section}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {uploadResult.tables_extracted > 0 && (
                <p><strong>Financial Tables Extracted:</strong> {uploadResult.tables_extracted}</p>
              )}
              
              <div className="action-buttons">
                <Link 
                  to={`/financial-report/${uploadResult.id || uploadResult.document_id}`}
                  className="view-button"
                >
                  View Financial Analysis
                </Link>
                <Link 
                  to={`/tldr/${uploadResult.id || uploadResult.document_id}`}
                  className="view-button"
                >
                  View TLDR Summary
                </Link>
              </div>
            </>
          )}
          
          {processingStatus === "error" && (
            <div className="processing-error">
              <p>There was an error processing your document. The file may be in an unsupported format or contain unrecognized content.</p>
              <p>You can try uploading a different document or contact support if the problem persists.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FinancialReportUpload;