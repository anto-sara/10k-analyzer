import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import * as d3 from "d3";

function TextAnalysis() {
  const [text, setText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const topicChartRef = useRef(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError("Please enter text to analyze");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const result = await api.analyzeText(text);
      setAnalysis(result);
      
    } catch (err) {
      setError(err.response?.data?.detail || "Error analyzing text");
      console.error("Analysis error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Create D3 visualization for topics
  useEffect(() => {
    if (analysis && analysis.topics && analysis.topics.topics && topicChartRef.current) {
      createTopicsChart();
    }
  }, [analysis]);

  const createTopicsChart = () => {
    const topicData = analysis.topics.topics.slice(0, 10); // Get top 10 topics
    
    // Clear previous chart
    d3.select(topicChartRef.current).selectAll("*").remove();
    
    // Set dimensions
    const margin = { top: 20, right: 30, bottom: 70, left: 60 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(topicChartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // X scale
    const x = d3.scaleBand()
      .domain(topicData.map(d => d.word))
      .range([0, width])
      .padding(0.2);
    
    // Y scale
    const y = d3.scaleLinear()
      .domain([0, d3.max(topicData, d => d.frequency)])
      .nice()
      .range([height, 0]);
    
    // Add X axis
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");
    
    // Add Y axis
    svg.append("g")
      .call(d3.axisLeft(y));
    
    // Add title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", 0 - margin.top / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .text("Topic Frequency");
    
    // Add bars
    svg.selectAll(".bar")
      .data(topicData)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.word))
      .attr("y", d => y(d.frequency))
      .attr("width", x.bandwidth())
      .attr("height", d => height - y(d.frequency))
      .attr("fill", "steelblue");
  };

  return (
    <div className="analysis-container">
      <h2>Text Analysis</h2>
      <form onSubmit={handleAnalyze}>
        <div className="form-group">
          <label htmlFor="analysis-text">Enter Text to Analyze:</label>
          <textarea 
            id="analysis-text" 
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text for analysis (minimum 100 characters recommended)"
            rows="6"
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || text.length < 20}
          className="analyze-button"
        >
          {loading ? "Analyzing..." : "Analyze Text"}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {analysis && (
        <div className="analysis-results">
          <h3>Analysis Results</h3>
          
          <div className="result-card sentiment-card">
            <h4>Sentiment Analysis</h4>
            <div className="sentiment-result">
              <div className={`sentiment-indicator ${analysis.sentiment.label.toLowerCase()}`}>
                {analysis.sentiment.label}
              </div>
              <div className="sentiment-score">
                Confidence: {(analysis.sentiment.score * 100).toFixed(1)}%
              </div>
            </div>
          </div>
          
          <div className="result-card summary-card">
            <h4>Summary</h4>
            <p>{analysis.summary.summary}</p>
          </div>
          
          <div className="result-card topics-card">
            <h4>Topic Analysis</h4>
            <div className="topics-visualization" ref={topicChartRef}></div>
            <div className="topics-list">
              <h5>Top Topics:</h5>
              <ul>
                {analysis.topics.topics.slice(0, 10).map((topic, index) => (
                  <li key={index}>
                    <span className="topic-word">{topic.word}</span>
                    <span className="topic-frequency">({topic.frequency})</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TextAnalysis;