import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import re

class FinancialStatementParser:
    """Parse and structure financial statements from extracted tables"""
    
    def __init__(self):
        # Define schemas for each statement type
        self.income_statement_schema = {
            "revenue": ["revenue", "total revenue", "net revenue", "sales", "net sales"],
            "cost_of_goods_sold": ["cost of goods sold", "cost of revenue", "cost of sales", "cogs"],
            "gross_profit": ["gross profit", "gross margin", "gross income"],
            "operating_expenses": ["operating expenses", "operating costs", "total operating expenses"],
            "wages": ["salaries", "wages", "compensation", "salary expense", "labor"],
            "operational_overhead": ["overhead", "operational costs", "facilities"],
            "net_profit": ["net income", "net profit", "net earnings", "profit", "net loss"],
            "ebitda": ["ebitda", "earnings before interest taxes depreciation amortization"],
            "depreciation_amortization": ["depreciation", "amortization", "depreciation and amortization"],
            "interest_expense": ["interest expense", "interest income", "interest"]
            # Add more categories as needed
        }
        
        # Similar schemas for balance sheet and cash flow statement
        # ...
    
    def parse_income_statement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse income statement into standardized format"""
        result = {category: None for category in self.income_statement_schema.keys()}
        
        try:
            # First column usually contains item names
            if df.shape[1] > 0 and df.shape[0] > 0:
                items_col = df.iloc[:, 0]
                
                # Find numeric columns
                numeric_cols = []
                for i in range(1, df.shape[1]):
                    if df.iloc[:, i].dtype in [np.float64, np.int64] or pd.to_numeric(df.iloc[:, i], errors='coerce').notna().any():
                        numeric_cols.append(i)
                
                if not numeric_cols:
                    return result
                    
                values_col_idx = numeric_cols[-1]  # Use most recent period
                
                # Match items to schema categories
                for row_idx, item_name in enumerate(items_col):
                    if not isinstance(item_name, str):
                        continue
                        
                    item_name_lower = str(item_name).lower()
                    
                    for category, keywords in self.income_statement_schema.items():
                        if any(keyword in item_name_lower for keyword in keywords):
                            # Get the value for this item
                            value = df.iloc[row_idx, values_col_idx]
                            
                            # Convert to numeric if needed
                            if isinstance(value, str):
                                value = self._string_to_number(value)
                                
                            result[category] = value
                            break
            
            # Calculate missing items if possible
            if result["revenue"] is not None and result["cost_of_goods_sold"] is not None and result["gross_profit"] is None:
                result["gross_profit"] = result["revenue"] - result["cost_of_goods_sold"]
                
            return result
        except Exception as e:
            print(f"Error parsing income statement: {e}")
            return result
    
    def _string_to_number(self, value_str: str) -> Optional[float]:
        """Convert a string to a number, handling different formats"""
        if not value_str or not isinstance(value_str, str):
            return None
            
        # Remove any non-numeric characters except for decimal points and negative signs
        clean_str = re.sub(r'[^\d.-]', '', value_str)
        
        try:
            return float(clean_str)
        except ValueError:
            return None