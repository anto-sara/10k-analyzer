import React, { useState } from 'react';
import { api } from '../services/api';

function DocumentUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
  };

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
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading document');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Document</h2>
      <form onSubmit={handleUpload}>
        <div className="form-group">
          <label htmlFor="document-file">Select Document:</label>
          <input 
            type="file" 
            id="document-file" 
            onChange={handleFileChange}
            accept=".txt,.md,.csv,.json,.py,.pdf,.docx"
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !file}
          className="upload-button"
        >
          {loading ? 'Uploading...' : 'Upload Document'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {uploadResult && (
        <div className="success-message">
          <h3>Document Uploaded Successfully!</h3>
          <p><strong>Document ID:</strong> {uploadResult.id}</p>
          <p><strong>Title:</strong> {uploadResult.title}</p>
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;
