import React from 'react';
import { Link } from 'react-router-dom';
import FinancialReportUpload from './FinancialReportUpload';
import DocumentSearch from './DocumentSearch';
import TextAnalysis from './TextAnalysis';

function Dashboard() {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Document Analysis System</h1>
        <p>Upload, search, and analyze documents using AI</p>
        
        {/* Add History button */}
        <div className="navigation-tabs">
          <Link to="/history" className="nav-button">View Analysis History</Link>
        </div>
      </header>
      
      <div className="tab-selector">
        <button className="active">General Documents</button>
        <button>Financial Reports</button>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-section">
          <FinancialReportUpload />
        </div>
        
        <div className="dashboard-section">
          <DocumentSearch />
        </div>
        
        <div className="dashboard-section">
          <TextAnalysis />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;