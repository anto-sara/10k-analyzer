import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

function ProgressTracker({ documentId }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (!documentId) return;
    
    const fetchProgress = async () => {
      try {
        const response = await api.getProcessingStatus(documentId);
        
        // Update status display
        setStatus(response.status);
        
        // Convert status to percentage
        let percentage = 0;
        switch(response.status) {
          case 'uploaded': percentage = 10; break;
          case 'parsing': percentage = 25; break;
          case 'analyzing': percentage = 50; break;
          case 'generating_visualizations': percentage = 75; break;
          case 'complete': 
            percentage = 100; 
            setIsProcessing(false);
            break;
          case 'error': 
            setError(response.error); 
            setIsProcessing(false);
            break;
          default: percentage = 0;
        }
        
        setProgress(percentage);
      } catch (err) {
        console.error('Error fetching progress:', err);
        setError('Failed to get processing status');
      }
    };
    
    // Only poll if still processing
    if (isProcessing) {
      fetchProgress();
      const intervalId = setInterval(fetchProgress, 3000);
      return () => clearInterval(intervalId);
    }
  }, [documentId, isProcessing]);
  
  return (
    <div className="processing-status">
      <h3>Analysis Progress</h3>
      
      {error ? (
        <div className="processing-error">
          <p>Error: {error}</p>
        </div>
      ) : (
        <>
          <p>
            {status === 'complete' 
              ? 'Analysis complete!' 
              : `Status: ${status.replace('_', ' ')}`}
          </p>
          
          <div className="progress-indicator">
            <div 
              className="progress-bar" 
              style={{ width: `${progress}%`, animation: isProcessing ? 'progress-animation 1.5s infinite ease-in-out' : 'none' }}
            />
          </div>
          
          <p className="processing-tip">
            {isProcessing 
              ? 'Your document is being processed. This may take a few minutes.' 
              : 'Document processing is complete.'}
          </p>
        </>
      )}
    </div>
  );
}

export default ProgressTracker;