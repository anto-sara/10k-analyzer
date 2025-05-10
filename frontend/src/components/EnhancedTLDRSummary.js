import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function EnhancedTLDRSummary() {
  const { documentId } = useParams();
  const [summary, setSummary] = useState(null);
  const [activeSection, setActiveSection] = useState('executive');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // First try to get the enhanced TLDR if available
        try {
          const enhancedResponse = await api.getExtendedTLDR(documentId);
          if (enhancedResponse?.extended_tldr) {
            setSummary(enhancedResponse.extended_tldr);
            setLoading(false);
            return;
          }
        } catch (enhancedErr) {
          console.log("Enhanced TLDR not available, falling back to standard summary");
        }
        
        // Fall back to regular summary
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

  // Get available section names
  const sectionNames = Object.keys(summary.sections || {});

  return (
    <div className="tldr-container">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        <div className="navigation-tabs">
          <Link to="/" className="nav-button">Back to Dashboard</Link>
          <Link to={`/financial-report/${documentId}`} className="nav-button">Financial Analysis</Link>
        </div>
      </header>

      <div className="tldr-summary">
        <h2>Enhanced TLDR Summary</h2>
        <p>Document ID: {documentId}</p>
        
        <div className="tab-selector">
          <button 
            className={activeSection === 'executive' ? 'active' : ''}
            onClick={() => setActiveSection('executive')}
          >
            Executive Summary
          </button>
          
          {sectionNames.map(section => (
            <button 
              key={section}
              className={activeSection === section ? 'active' : ''}
              onClick={() => setActiveSection(section)}
            >
              {section.replace(/_/g, ' ').toUpperCase()}
            </button>
          ))}
        </div>
        
        <div className="summary-content">
          {activeSection === 'executive' ? (
            <div className="executive-summary">
              <h3>Executive Summary</h3>
              <p>{summary.executive_summary || "No executive summary available."}</p>
              
              {/* Add key metrics if available */}
              {summary.key_metrics && (
                <div className="key-metrics">
                  <h4>Key Metrics</h4>
                  <ul>
                    {Object.entries(summary.key_metrics).map(([key, value]) => (
                      <li key={key}>
                        <strong>{key.replace(/_/g, ' ')}: </strong>
                        {typeof value === 'number' 
                          ? `$${value.toLocaleString()}`
                          : value
                        }
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Add key highlights if available */}
              {summary.highlights && (
                <div className="highlights">
                  <h4>Key Highlights</h4>
                  <ul>
                    {summary.highlights.map((highlight, index) => (
                      <li key={index}>{highlight}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="section-details">
              <h3>{activeSection.replace(/_/g, ' ').toUpperCase()}</h3>
              <div className="section-content">
                <p>{summary.sections[activeSection]}</p>
              </div>
              
              {/* Add section-specific visualizations or metrics if available */}
              {summary.section_metrics && summary.section_metrics[activeSection] && (
                <div className="section-metrics">
                  <h4>Metrics</h4>
                  <ul>
                    {Object.entries(summary.section_metrics[activeSection]).map(([key, value]) => (
                      <li key={key}>
                        <strong>{key.replace(/_/g, ' ')}: </strong>
                        {typeof value === 'number' 
                          ? `$${value.toLocaleString()}`
                          : value
                        }
                      </li>
                    ))}
                  </ul>
                </div>
              )}
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

export default EnhancedTLDRSummary;