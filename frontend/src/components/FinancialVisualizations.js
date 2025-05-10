import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { sankeyLinkHorizontal, sankey, sankeyJustify } from 'd3-sankey';

export const IncomeStatementChart = ({ data }) => {
  const chartRef = useRef(null);
  
  useEffect(() => {
    if (!data || !chartRef.current) return;
    
    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();
    
    // Setup dimensions
    const margin = { top: 30, right: 30, bottom: 70, left: 100 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(chartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Prepare data
    const items = [
      { name: "Revenue", value: data.revenue || 0 },
      { name: "Cost of Goods Sold", value: -Math.abs(data.cost_of_goods_sold || 0) },
      { name: "Gross Profit", value: data.gross_profit || 0 },
      { name: "Operating Expenses", value: -Math.abs(data.operating_expenses || 0) },
      { name: "Net Profit", value: data.net_profit || 0 }
    ];
    
    // X and Y scales
    const x = d3.scaleBand()
      .domain(items.map(d => d.name))
      .range([0, width])
      .padding(0.2);
      
    const y = d3.scaleLinear()
      .domain([
        d3.min(items, d => d.value), 
        d3.max(items, d => d.value)
      ])
      .nice()
      .range([height, 0]);
    
    // Add X axis
    svg.append("g")
      .attr("transform", `translate(0,${height/2})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");
    
    // Add Y axis
    svg.append("g")
      .call(d3.axisLeft(y));
    
    // Add bars
    svg.selectAll(".bar")
      .data(items)
      .enter()
      .append("rect")
      .attr("x", d => x(d.name))
      .attr("y", d => d.value > 0 ? y(d.value) : y(0))
      .attr("width", x.bandwidth())
      .attr("height", d => Math.abs(y(d.value) - y(0)))
      .attr("fill", d => d.value >= 0 ? "green" : "red");
    
    // Add labels
    svg.selectAll(".label")
      .data(items)
      .enter()
      .append("text")
      .attr("class", "label")
      .attr("x", d => x(d.name) + x.bandwidth()/2)
      .attr("y", d => d.value > 0 ? y(d.value) - 5 : y(0) + Math.abs(y(d.value) - y(0)) + 15)
      .attr("text-anchor", "middle")
      .text(d => `$${Math.abs(d.value).toLocaleString()}`);
  }, [data]);
  
  return <div ref={chartRef}></div>;
};

export const SankeyChart = ({ data }) => {
  const sankeyRef = useRef(null);
  
  useEffect(() => {
    if (!data || !sankeyRef.current) return;
    
    // Clear previous chart
    d3.select(sankeyRef.current).selectAll("*").remove();
    
    // Setup dimensions
    const margin = { top: 20, right: 30, bottom: 20, left: 30 };
    const width = 700 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(sankeyRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Create Sankey generator
    const sankeyGenerator = sankey()
      .nodeWidth(20)
      .nodePadding(10)
      .extent([[0, 0], [width, height]]);
    
    // Transform cash flow data into nodes and links
    const graph = transformToSankeyData(data);
    
    // Generate the Sankey diagram
    const { nodes, links } = sankeyGenerator(graph);
    
    // Add links
    svg.append("g")
      .selectAll("path")
      .data(links)
      .enter()
      .append("path")
      .attr("d", sankeyLinkHorizontal())
      .attr("stroke-width", d => Math.max(1, d.width))
      .attr("stroke", d => d.color || "#aaa")
      .style("fill", "none")
      .style("stroke-opacity", 0.5);
    
    // Add nodes
    svg.append("g")
      .selectAll("rect")
      .data(nodes)
      .enter()
      .append("rect")
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("height", d => d.y1 - d.y0)
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => d.color || "#888")
      .attr("stroke", "#333");
    
    // Add labels
    svg.append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .text(d => `${d.name} ($${d.value.toLocaleString()})`);
      
  }, [data]);
  
  // Helper function to transform data into Sankey format
  const transformToSankeyData = (cashFlowData) => {
    // Transform the cash flow data into nodes and links
    // This would depend on your specific data structure
    // ...
    
    return {
      nodes: [
        // Example nodes for cash flow
        { name: "Revenue" },
        { name: "Expenses" },
        { name: "Operations" },
        { name: "Investments" },
        { name: "Financing" },
        { name: "Net Cash" }
      ],
      links: [
        // Example links
        { source: 0, target: 2, value: 1000000, color: "#1f77b4" },
        { source: 1, target: 2, value: 800000, color: "#d62728" },
        { source: 2, target: 5, value: 200000, color: "#2ca02c" },
        { source: 2, target: 3, value: 300000, color: "#ff7f0e" },
        { source: 3, target: 5, value: 100000, color: "#9467bd" },
        { source: 4, target: 5, value: 150000, color: "#8c564b" }
      ]
    };
  };
  
  return <div ref={sankeyRef}></div>;
};