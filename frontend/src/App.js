import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import FinancialReport from './components/FinancialReport';
import TLDRSummary from './components/TLDRSummary';
import EnhancedTLDRSummary from './components/EnhancedTLDRSummary';
import AnalysisHistory from './components/AnalysisHistory';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/financial-report/:documentId" element={<FinancialReport />} />
          <Route path="/tldr/:documentId" element={<TLDRSummary />} />
          <Route path="/enhanced-tldr/:documentId" element={<EnhancedTLDRSummary />} />
          <Route path="/history" element={<AnalysisHistory />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;