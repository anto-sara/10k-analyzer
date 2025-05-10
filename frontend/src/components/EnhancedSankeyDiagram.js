import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';

const EnhancedSankeyDiagram = ({ data }) => {
  const sankeyRef = useRef(null);
  
  useEffect(() => {
    if (!data || !sankeyRef.current) return;
    
    // Clear any previous diagram
    d3.select(sankeyRef.current).selectAll("*").remove();
    
    // Set dimensions
    const margin = { top: 20, right: 30, bottom: 20, left: 30 };
    const width = 800 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(sankeyRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Sample financial flow data - you'll replace this with real API data
    const nodes = [
      { name: "Revenue" },
      { name: "Cost of Revenue" },
      { name: "Gross Profit" },
      { name: "Operating Expenses" },
      { name: "Operating Income" },
      { name: "Income Tax" },
      { name: "Net Income" },
      { name: "Dividends" },
      { name: "Retained Earnings" }
    ];
    
    const links = [
      { source: 0, target: 1, value: 800000, color: "#d62728" },  // Revenue to Cost of Revenue
      { source: 0, target: 2, value: 1200000, color: "#2ca02c" }, // Revenue to Gross Profit
      { source: 2, target: 3, value: 700000, color: "#d62728" },  // Gross Profit to Operating Expenses
      { source: 2, target: 4, value: 500000, color: "#2ca02c" },  // Gross Profit to Operating Income
      { source: 4, target: 5, value: 125000, color: "#d62728" },  // Operating Income to Income Tax
      { source: 4, target: 6, value: 375000, color: "#2ca02c" },  // Operating Income to Net Income
      { source: 6, target: 7, value: 125000, color: "#d62728" },  // Net Income to Dividends
      { source: 6, target: 8, value: 250000, color: "#2ca02c" }   // Net Income to Retained Earnings
    ];
    
    // Use provided data if available
    const graphData = data || { nodes, links };
    
    // Create Sankey generator
    const sankeyGenerator = sankey()
      .nodeWidth(20)
      .nodePadding(10)
      .extent([[0, 0], [width, height]]);
    
    // Process the data to ensure proper format
    const processedData = {
      nodes: graphData.nodes.map(d => ({...d})),
      links: graphData.links.map(d => ({...d}))
    };
    
    // Generate the Sankey diagram
    const { nodes: sankeyNodes, links: sankeyLinks } = sankeyGenerator(processedData);
    
    // Add links with gradients
    const links_g = svg.append("g")
      .selectAll(".link")
      .data(sankeyLinks)
      .enter()
      .append("g")
      .attr("class", "link");
    
    links_g.append("path")
      .attr("d", sankeyLinkHorizontal())
      .attr("stroke", d => d.color || "#aaa")
      .attr("stroke-width", d => Math.max(1, d.width))
      .attr("fill", "none")
      .attr("opacity", 0.5)
      .on("mouseover", function() {
        d3.select(this).attr("opacity", 0.8).attr("stroke-width", d => Math.max(1, d.width + 2));
      })
      .on("mouseout", function() {
        d3.select(this).attr("opacity", 0.5).attr("stroke-width", d => Math.max(1, d.width));
      })
      .append("title")
      .text(d => `${d.source.name} → ${d.target.name}: $${d.value.toLocaleString()}`);
    
    // Add nodes
    const nodes_g = svg.append("g")
      .selectAll(".node")
      .data(sankeyNodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", d => `translate(${d.x0},${d.y0})`);
    
    nodes_g.append("rect")
      .attr("height", d => d.y1 - d.y0)
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => d.color || "#69b3a2")
      .attr("stroke", "#000")
      .attr("stroke-width", 1)
      .on("mouseover", function() {
        d3.select(this).attr("stroke-width", 2).attr("opacity", 0.8);
      })
      .on("mouseout", function() {
        d3.select(this).attr("stroke-width", 1).attr("opacity", 1);
      })
      .append("title")
      .text(d => `${d.name}: $${d.value.toLocaleString()}`);
    
    // Add labels
    nodes_g.append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .text(d => d.name)
      .attr("font-size", 14)
      .attr("font-weight", "bold")
      .attr("fill", "#333");
    
    // Add value labels
    nodes_g.append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2 + 18)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .text(d => `$${d.value.toLocaleString()}`)
      .attr("font-size", 12)
      .attr("fill", "#666");
      
  }, [data]);
  
  return (
    <div className="cash-flow-sankey">
      <h3>Financial Flow Analysis</h3>
      <div ref={sankeyRef} className="sankey-diagram"></div>
      <div className="sankey-legend">
        <p><span className="legend-item revenue">■</span> Revenue Flows</p>
        <p><span className="legend-item expense">■</span> Expense Flows</p>
        <p><span className="legend-item profit">■</span> Profit Allocation</p>
      </div>
    </div>
  );
};

export default EnhancedSankeyDiagram;