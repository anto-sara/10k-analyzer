import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function TLDRSummary() {
  const { documentId } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getFinancialSummary(documentId);
        setSummary(response.summary);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching TLDR summary:", err);
        setError("Failed to load TLDR summary. Please try again later.");
        setLoading(false);
      }
    };

    fetchData();
  }, [documentId]);

  if (loading) return <div className="loading-indicator">Loading TLDR summary...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!summary) return <div className="no-data">No summary available for this document.</div>;

  return (
    <div className="tldr-container">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        <div className="navigation-tabs">
          <Link to="/" className="nav-button">Back to Dashboard</Link>
        </div>
      </header>

      <div className="tldr-summary">
        <h2>TLDR Summary</h2>
        <p>Document ID: {documentId}</p>
        
        <div className="summary-content">
          <div className="executive-summary">
            <h3>Executive Summary</h3>
            <p>{summary.executive_summary || "No executive summary available."}</p>
          </div>
          
          {summary.sections && Object.keys(summary.sections).length > 0 && (
            <div className="section-summaries">
              <h3>Section Summaries</h3>
              
              {Object.entries(summary.sections).map(([section, content]) => (
                <div key={section} className="section-summary">
                  <h4>{section.replace(/_/g, ' ').toUpperCase()}</h4>
                  <p>{content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="navigation-links">
          <Link to={`/financial-report/${documentId}`} className="view-button">View Financial Analysis</Link>
          <Link to="/" className="secondary-button">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}

export default TLDRSummary;