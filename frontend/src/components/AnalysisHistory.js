import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

function AnalysisHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        
        // Add this endpoint to your api.js
        const response = await api.getAnalysisHistory();
        setHistory(response || []);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching analysis history:', err);
        setError('Failed to load analysis history');
        setLoading(false);
      }
    };
    
    fetchHistory();
  }, []);
  
  if (loading) return <div className="loading-indicator">Loading analysis history...</div>;
  if (error) return <div className="error-message">{error}</div>;
  
  // If no real API exists yet, we'll show sample data
  const displayHistory = history.length > 0 ? history : [
    {
      id: 17,
      title: "CHIPOTLE ANNUAL REPORT.pdf",
      file_type: "pdf",
      created_at: "2024-05-01T14:32:10",
      sections: ["business", "risk_factors", "management_discussion"],
      processing_status: "complete"
    },
    {
      id: 16,
      title: "TESLA 10-K 2023.pdf",
      file_type: "pdf",
      created_at: "2024-04-28T09:15:22",
      sections: ["business", "risk_factors", "financial_statements"],
      processing_status: "complete"
    },
    {
      id: 15,
      title: "MICROSOFT ANNUAL REPORT.pdf",
      file_type: "pdf",
      created_at: "2024-04-25T16:45:33",
      sections: ["business", "financial_statements", "outlook"],
      processing_status: "complete"
    }
  ];
  
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        <div className="navigation-tabs">
          <Link to="/" className="nav-button">Back to Dashboard</Link>
        </div>
      </header>
      
      <div className="dashboard-content">
        <div className="dashboard-section" style={{ gridColumn: "1 / span 3" }}>
          <h2>Previous Analyses</h2>
          
          {displayHistory.length === 0 ? (
            <p>No previous analyses found.</p>
          ) : (
            <div className="history-list">
              {displayHistory.map(item => (
                <div key={item.id} className="result-card">
                  <div className="result-header">
                    <h3 className="result-title">{item.title}</h3>
                    <span className="result-date">
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="result-info">
                    <p><strong>Document ID:</strong> {item.id}</p>
                    <p><strong>File Type:</strong> {item.file_type}</p>
                    
                    {item.sections && (
                      <div>
                        <p><strong>Sections:</strong></p>
                        <ul className="section-list">
                          {item.sections.map((section, index) => (
                            <li key={index}>{section.replace(/_/g, ' ')}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <div className="action-buttons">
                    <Link 
                      to={`/financial-report/${item.id}`}
                      className="view-button"
                    >
                      View Financial Analysis
                    </Link>
                    <Link 
                      to={`/tldr/${item.id}`}
                      className="view-button"
                    >
                      View TLDR Summary
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalysisHistory;