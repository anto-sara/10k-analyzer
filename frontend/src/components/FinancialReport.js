import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { IncomeStatementChart } from './FinancialVisualizations';
import EnhancedSankeyDiagram from './EnhancedSankeyDiagram';
import ProgressTracker from './ProgressTracker';

function FinancialReport() {
  const { documentId } = useParams();
  const [financialData, setFinancialData] = useState(null);
  const [flowData, setFlowData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get financial summary data
        const response = await api.getFinancialSummary(documentId);
        setFinancialData(response);
        
        // Get financial flow data for Sankey diagram
        try {
          const flowResponse = await api.getFinancialFlow(documentId);
          if (flowResponse && flowResponse.flow_data) {
            setFlowData(flowResponse.flow_data);
          }
        } catch (flowErr) {
          console.error("Error fetching flow data:", flowErr);
          // Continue without flow data if it fails
        }
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching financial data:", err);
        setError("Failed to load financial report. Please try again later.");
        setLoading(false);
      }
    };

    fetchData();
  }, [documentId]);

  if (loading) {
    return (
      <div className="financial-report-container">
        <header className="dashboard-header">
          <h1>Document Analysis System</h1>
          <p>Upload, search, and analyze documents using AI</p>
          <div className="navigation-tabs">
            <Link to="/" className="nav-button">Back to Dashboard</Link>
          </div>
        </header>
        
        <div className="loading-indicator">Loading financial report...</div>
        
        {/* Show progress tracker while loading */}
        <ProgressTracker documentId={documentId} />
      </div>
    );
  }

  if (error) return (
    <div className="financial-report-container">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        <div className="navigation-tabs">
          <Link to="/" className="nav-button">Back to Dashboard</Link>
        </div>
      </header>
      
      <div className="error-message">{error}</div>
    </div>
  );

  if (!financialData) return (
    <div className="financial-report-container">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        <div className="navigation-tabs">
          <Link to="/" className="nav-button">Back to Dashboard</Link>
        </div>
      </header>
      
      <div className="no-data">No financial data available for this document.</div>
    </div>
  );

  const incomeStatementData = financialData.financial_data?.income_statement || {};

  return (
    <div className="financial-report-container">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        <div className="navigation-tabs">
          <Link to="/" className="nav-button">Back to Dashboard</Link>
          <Link to="/history" className="nav-button">Analysis History</Link>
        </div>
      </header>

      <div className="financial-report">
        <h2>Financial Analysis</h2>
        <p>Document ID: {documentId}</p>
        
        {/* Tab Navigation */}
        <div className="tab-selector">
          <button 
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={activeTab === 'income' ? 'active' : ''}
            onClick={() => setActiveTab('income')}
          >
            Income Statement
          </button>
          <button 
            className={activeTab === 'flow' ? 'active' : ''}
            onClick={() => setActiveTab('flow')}
          >
            Financial Flow
          </button>
        </div>
        
        <div className="financial-content">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="financial-overview">
              <div className="financial-summary">
                <h3>Financial Summary</h3>
                <p>{financialData.summary?.executive_summary || "No financial summary available."}</p>
                
                {/* Add key metrics */}
                <div className="key-metrics">
                  <h4>Key Metrics</h4>
                  <div className="metrics-grid">
                    <div className="metric-item">
                      <span className="metric-label">Revenue</span>
                      <span className="metric-value">${incomeStatementData.revenue?.toLocaleString() || 'N/A'}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Gross Profit</span>
                      <span className="metric-value">${incomeStatementData.gross_profit?.toLocaleString() || 'N/A'}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Net Profit</span>
                      <span className="metric-value">${incomeStatementData.net_profit?.toLocaleString() || 'N/A'}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Operating Expenses</span>
                      <span className="metric-value">${incomeStatementData.operating_expenses?.toLocaleString() || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Preview chart */}
              <div className="overview-chart">
                <h3>Income Statement Overview</h3>
                <IncomeStatementChart data={incomeStatementData} />
              </div>
              
              {/* Preview of flow diagram */}
              {flowData && (
                <div className="overview-flow preview-flow">
                  <h3>Financial Flow Preview</h3>
                  <div className="preview-container">
                    <EnhancedSankeyDiagram data={flowData} />
                  </div>
                  <button 
                    className="view-more-button"
                    onClick={() => setActiveTab('flow')}
                  >
                    View Full Financial Flow Analysis
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Income Statement Tab */}
          {activeTab === 'income' && (
            <div className="income-statement">
              <h3>Income Statement Analysis</h3>
              
              <div className="financial-table">
                <table>
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Revenue</td>
                      <td>${incomeStatementData.revenue?.toLocaleString() || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Cost of Goods Sold</td>
                      <td>${incomeStatementData.cost_of_goods_sold?.toLocaleString() || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Gross Profit</td>
                      <td>${incomeStatementData.gross_profit?.toLocaleString() || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Operating Expenses</td>
                      <td>${incomeStatementData.operating_expenses?.toLocaleString() || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Net Profit</td>
                      <td>${incomeStatementData.net_profit?.toLocaleString() || 'N/A'}</td>
                    </tr>
                    {incomeStatementData.ebitda && (
                      <tr>
                        <td>EBITDA</td>
                        <td>${incomeStatementData.ebitda.toLocaleString()}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              
              <div className="income-visualization">
                <h4>Income Statement Visualization</h4>
                <IncomeStatementChart data={incomeStatementData} />
              </div>
              
              {/* Add trend analysis if available */}
              {financialData.trends && (
                <div className="trend-analysis">
                  <h4>Trend Analysis</h4>
                  <p>{financialData.trends.income_statement || "No trend data available."}</p>
                </div>
              )}
            </div>
          )}
          
          {/* Financial Flow Tab */}
          {activeTab === 'flow' && (
            <div className="financial-flow">
              <h3>Financial Flow Analysis</h3>
              
              <p className="flow-description">
                This Sankey diagram visualizes the flow of funds through the company's financial statements,
                showing how revenue is allocated to various expenses and ultimately to net income.
              </p>
              
              {flowData ? (
                <div className="sankey-container">
                  <EnhancedSankeyDiagram data={flowData} />
                </div>
              ) : (
                <div className="placeholder-visualization">
                  <p>Financial flow data is not available for this document.</p>
                </div>
              )}
              
              <div className="flow-insights">
                <h4>Financial Flow Insights</h4>
                <ul>
                  <li>Revenue conversion efficiency: {Math.round((incomeStatementData.net_profit / incomeStatementData.revenue) * 100)}%</li>
                  <li>Gross margin: {Math.round((incomeStatementData.gross_profit / incomeStatementData.revenue) * 100)}%</li>
                  <li>Operating expense ratio: {Math.round((incomeStatementData.operating_expenses / incomeStatementData.revenue) * 100)}%</li>
                </ul>
              </div>
            </div>
          )}
        </div>
        
        <div className="navigation-links">
          <Link to={`/enhanced-tldr/${documentId}`} className="view-button">View Enhanced TLDR</Link>
          <Link to="/" className="secondary-button">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}

export default FinancialReport;