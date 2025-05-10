from transformers import pipeline
from typing import Dict, Any, List, Optional
import re
import numpy as np
import json

class FinancialFlowAnalyzer:
    """Analyze financial flows and generate Sankey diagram data"""
    
    def __init__(self):
        # Define standard financial flow categories
        self.flow_categories = {
            "Revenue": ["revenue", "net revenue", "total revenue", "sales", "net sales"],
            "Expenses": ["cost of revenue", "cost of sales", "operating expenses", "sg&a", "r&d"],
            "Income": ["operating income", "net income", "profit", "earnings"],
            "Cash": ["cash flow", "operating activities", "investing activities", "financing activities"],
            "Assets": ["assets", "total assets", "current assets"],
            "Liabilities": ["liabilities", "total liabilities", "current liabilities"],
            "Equity": ["equity", "stockholders equity", "shareholders equity"]
        }
        
        # Define standard colors for different flow types
        self.flow_colors = {
            "Revenue": "#2ca02c",       # Green for revenue
            "Expenses": "#d62728",      # Red for expenses
            "Income": "#1f77b4",        # Blue for income/profits
            "Assets": "#9467bd",        # Purple for assets
            "Liabilities": "#ff7f0e",   # Orange for liabilities
            "Equity": "#8c564b",        # Brown for equity
            "Cash": "#e377c2"           # Pink for cash flows
        }
    
    def generate_sankey_data(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for Sankey diagram from financial statements"""
        # Initialize nodes and links
        nodes = []
        links = []
        
        # Extract income statement data if available
        if 'income_statement' in financial_data:
            income_data = financial_data['income_statement']
            self._add_income_flow(income_data, nodes, links)
        
        # If no specific data is available, generate sample data for visualization
        if not links:
            self._add_sample_data(nodes, links)
        
        # Return formatted data for D3 Sankey diagram
        return {
            "nodes": [{"name": node} for node in nodes],
            "links": self._format_links(links, nodes)
        }
    
    def _add_income_flow(self, income_data: Dict[str, Any], nodes: List[str], links: List[Dict[str, Any]]):
        """Add income statement data to Sankey diagram"""
        # Extract key metrics from income statement
        revenue = income_data.get('revenue', 0)
        cogs = income_data.get('cost_of_goods_sold', 0)
        gross_profit = income_data.get('gross_profit', 0)
        opex = income_data.get('operating_expenses', 0)
        net_profit = income_data.get('net_profit', 0)
        
        # Add basic income statement nodes
        required_nodes = [
            "Revenue", 
            "Cost of Goods Sold", 
            "Gross Profit", 
            "Operating Expenses", 
            "Net Income"
        ]
        
        for node in required_nodes:
            if node not in nodes:
                nodes.append(node)
        
        # Add links for the income flows
        if revenue > 0:
            # If we have COGS data, create that flow
            if cogs > 0:
                links.append({
                    "source": "Revenue",
                    "target": "Cost of Goods Sold",
                    "value": abs(cogs),
                    "type": "Expenses"
                })
            
            # Calculate or use provided gross profit
            if gross_profit == 0 and revenue > 0 and cogs > 0:
                gross_profit = revenue - cogs
            
            if gross_profit > 0:
                links.append({
                    "source": "Revenue",
                    "target": "Gross Profit",
                    "value": abs(gross_profit),
                    "type": "Income"
                })
                
                # Add operating expenses flow if available
                if opex > 0:
                    links.append({
                        "source": "Gross Profit",
                        "target": "Operating Expenses",
                        "value": abs(opex),
                        "type": "Expenses"
                    })
                
                # Calculate or use provided net profit
                if net_profit == 0 and gross_profit > 0 and opex > 0:
                    net_profit = gross_profit - opex
                
                if net_profit > 0:
                    links.append({
                        "source": "Gross Profit",
                        "target": "Net Income",
                        "value": abs(net_profit),
                        "type": "Income"
                    })
        
        # Look for additional income statement items
        for item, value in income_data.items():
            if item not in ['revenue', 'cost_of_goods_sold', 'gross_profit', 'operating_expenses', 'net_profit'] and value:
                # Categorize the item and add to diagram if significant
                if item in ['interest_expense', 'depreciation_amortization', 'taxes']:
                    node_name = self._format_node_name(item)
                    
                    if node_name not in nodes:
                        nodes.append(node_name)
                    
                    # Add appropriate links
                    if item == 'interest_expense' and 'Net Income' in nodes:
                        links.append({
                            "source": "Gross Profit",
                            "target": node_name,
                            "value": abs(value),
                            "type": "Expenses"
                        })
                    elif item == 'taxes' and 'Net Income' in nodes:
                        links.append({
                            "source": "Gross Profit",
                            "target": node_name,
                            "value": abs(value),
                            "type": "Expenses"
                        })
                    elif item == 'depreciation_amortization' and 'Operating Expenses' in nodes:
                        links.append({
                            "source": node_name,
                            "target": "Operating Expenses",
                            "value": abs(value),
                            "type": "Expenses"
                        })
    
    def _add_balance_sheet_flow(self, balance_data: Dict[str, Any], nodes: List[str], links: List[Dict[str, Any]]):
        """Add balance sheet data to Sankey diagram"""
        # Implement balance sheet specific flows
        # This would depend on your balance sheet data structure
        pass
    
    def _add_cash_flow(self, cash_flow_data: Dict[str, Any], nodes: List[str], links: List[Dict[str, Any]]):
        """Add cash flow statement data to Sankey diagram"""
        # Implement cash flow specific flows
        # This would depend on your cash flow data structure
        pass
    
    def _format_node_name(self, snake_case_name: str) -> str:
        """Convert snake_case to Title Case for node names"""
        return ' '.join(word.capitalize() for word in snake_case_name.split('_'))
    
    def _format_links(self, raw_links: List[Dict[str, Any]], nodes: List[str]) -> List[Dict[str, Any]]:
        """Format links for D3 Sankey diagram with node indices"""
        formatted_links = []
        
        for link in raw_links:
            # Find source and target indices
            source_idx = nodes.index(link["source"]) if link["source"] in nodes else -1
            target_idx = nodes.index(link["target"]) if link["target"] in nodes else -1
            
            if source_idx >= 0 and target_idx >= 0:
                formatted_links.append({
                    "source": source_idx,
                    "target": target_idx,
                    "value": link["value"],
                    "color": self.flow_colors.get(link.get("type", ""), "#aaa")
                })
        
        return formatted_links
    
    def _add_sample_data(self, nodes: List[str], links: List[Dict[str, Any]]):
        """Add sample financial flow data when real data is not available"""
        # Define sample nodes
        sample_nodes = [
            "Revenue", 
            "Cost of Goods Sold", 
            "Gross Profit", 
            "Operating Expenses", 
            "Operating Income", 
            "Taxes",
            "Net Income", 
            "Dividends", 
            "Retained Earnings"
        ]
        
        # Add sample nodes
        for node in sample_nodes:
            if node not in nodes:
                nodes.append(node)
        
        # Add sample links with realistic values
        sample_links = [
            {"source": "Revenue", "target": "Cost of Goods Sold", "value": 800000, "type": "Expenses"},
            {"source": "Revenue", "target": "Gross Profit", "value": 1200000, "type": "Income"},
            {"source": "Gross Profit", "target": "Operating Expenses", "value": 700000, "type": "Expenses"},
            {"source": "Gross Profit", "target": "Operating Income", "value": 500000, "type": "Income"},
            {"source": "Operating Income", "target": "Taxes", "value": 125000, "type": "Expenses"},
            {"source": "Operating Income", "target": "Net Income", "value": 375000, "type": "Income"},
            {"source": "Net Income", "target": "Dividends", "value": 125000, "type": "Expenses"},
            {"source": "Net Income", "target": "Retained Earnings", "value": 250000, "type": "Income"}
        ]
        
        # Add sample links to the provided links list
        links.extend(sample_links)
    
    def generate_flow_insights(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about the financial flows"""
        insights = {
            "ratios": {},
            "observations": []
        }
        
        if 'income_statement' in financial_data:
            income_data = financial_data['income_statement']
            revenue = income_data.get('revenue', 0)
            
            if revenue > 0:
                # Calculate key ratios
                if 'gross_profit' in income_data and income_data['gross_profit']:
                    gross_margin = (income_data['gross_profit'] / revenue) * 100
                    insights["ratios"]["gross_margin"] = round(gross_margin, 2)
                    
                    if gross_margin > 50:
                        insights["observations"].append("High gross margin indicates strong pricing power or efficient production.")
                    elif gross_margin < 20:
                        insights["observations"].append("Low gross margin suggests cost pressures or competitive pricing environment.")
                
                if 'operating_expenses' in income_data and income_data['operating_expenses']:
                    opex_ratio = (income_data['operating_expenses'] / revenue) * 100
                    insights["ratios"]["opex_ratio"] = round(opex_ratio, 2)
                    
                    if opex_ratio > 40:
                        insights["observations"].append("High operating expense ratio may impact profitability.")
                    elif opex_ratio < 20:
                        insights["observations"].append("Low operating expense ratio indicates efficient operations.")
                
                if 'net_profit' in income_data and income_data['net_profit']:
                    net_margin = (income_data['net_profit'] / revenue) * 100
                    insights["ratios"]["net_margin"] = round(net_margin, 2)
                    
                    if net_margin > 20:
                        insights["observations"].append("Strong net margin demonstrates excellent profitability.")
                    elif net_margin < 5:
                        insights["observations"].append("Low net margin indicates pressure on bottom-line profitability.")
        
        return insights