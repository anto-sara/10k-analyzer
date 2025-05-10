import React, { useState } from 'react';
import { api } from '../services/api';

function DocumentSearch() {
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await api.searchDocuments(query, limit);
      setResults(response.results);
      
      if (response.results.length === 0) {
        setError('No results found for your query');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error searching documents');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <h2>Search Documents</h2>
      <form onSubmit={handleSearch}>
        <div className="form-group">
          <label htmlFor="search-query">Search Query:</label>
          <input 
            type="text" 
            id="search-query" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search query"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="result-limit">Results Limit:</label>
          <select 
            id="result-limit" 
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value="3">3 results</option>
            <option value="5">5 results</option>
            <option value="10">10 results</option>
          </select>
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !query.trim()}
          className="search-button"
        >
          {loading ? 'Searching...' : 'Search Documents'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="search-results">
          <h3>Search Results</h3>
          <ul>
            {results.map((result, index) => (
              <li key={index} className="result-item">
                <div className="result-header">
                  <span className="result-title">Document: {result.document_title}</span>
                  <span className="result-score">Relevance: {(1 - result.distance).toFixed(2)}</span>
                </div>
                <div className="result-content">
                  {result.chunk_text.slice(0, 200)}...
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default DocumentSearch;
