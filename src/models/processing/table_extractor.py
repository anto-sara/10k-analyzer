import camelot
import pandas as pd
from typing import List, Dict, Any

class FinancialTableExtractor:
    """Extract and process tables from financial documents"""
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[pd.DataFrame]:
        """Extract tables from PDF using camelot"""
        # Extract tables
        tables = camelot.read_pdf(
            pdf_path,
            pages='all',
            flavor='lattice'  # Try 'stream' if lattice doesn't work well
        )
        
        # Convert to list of pandas DataFrames
        return [table.df for table in tables if table.df.size > 0]
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[pd.DataFrame]:
        """Extract tables from PDF using camelot"""
        tables = []
        
        try:
            import camelot
            # Try lattice mode first
            lattice_tables = camelot.read_pdf(
                pdf_path,
                pages='all',
                flavor='lattice'
            )
            
            if len(lattice_tables) > 0:
                for table in lattice_tables:
                    if table.df.size > 0:
                        tables.append(table.df)
            
            # Try stream mode as a fallback
            stream_tables = camelot.read_pdf(
                pdf_path,
                pages='all',
                flavor='stream'
            )
            
            if len(stream_tables) > 0:
                for table in stream_tables:
                    if table.df.size > 0:
                        tables.append(table.df)
            
            # If still no tables, let's try a more aggressive approach with pdfplumber
            if len(tables) == 0:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        extracted_tables = page.extract_tables()
                        for table in extracted_tables:
                            if table and len(table) > 0:
                                tables.append(pd.DataFrame(table[1:], columns=table[0]))
            
            return tables
        except Exception as e:
            print(f"Table extraction error: {e}")
            return []
    
    def identify_statement_type(self, df: pd.DataFrame) -> str:
        """Determine if a table is an income statement, balance sheet, or cash flow statement"""
        try:
            # Convert all column headers and first column to a single string for pattern matching
            headers = ' '.join([str(x).lower() for x in df.columns.tolist()])
            if df.shape[0] > 0:
                first_col = ' '.join([str(x).lower() for x in df.iloc[:, 0].tolist()])
            else:
                first_col = ""
            
            full_text = headers + " " + first_col
            
            # Income statement indicators
            income_terms = ['revenue', 'sales', 'income', 'earnings', 'ebit', 'profit', 'loss']
            # Balance sheet indicators
            balance_terms = ['assets', 'liabilities', 'equity', 'cash and cash equivalents']
            # Cash flow indicators
            cashflow_terms = ['cash flow', 'operating activities', 'investing activities']
            
            # Count occurrences of terms
            income_count = sum(1 for term in income_terms if term in full_text)
            balance_count = sum(1 for term in balance_terms if term in full_text)
            cashflow_count = sum(1 for term in cashflow_terms if term in full_text)
            
            # Return the statement type with the most matching terms
            counts = [
                ("income_statement", income_count),
                ("balance_sheet", balance_count),
                ("cash_flow", cashflow_count)
            ]
            
            max_type = max(counts, key=lambda x: x[1])
            return max_type[0] if max_type[1] > 0 else "unknown"
        except Exception as e:
            print(f"Error identifying statement type: {e}")
            return "unknown"
    
    def clean_financial_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize a financial table"""
        try:
            # Make a copy to avoid modifying the original
            df = df.copy()
            
            # Remove empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Replace common financial formatting
            for col in df.columns:
                if df[col].dtype == object:  # Only process string columns
                    df[col] = df[col].astype(str)
                    # Remove parentheses for negative numbers and convert to actual negatives
                    df[col] = df[col].str.replace(r'\\((.*?)\\)', r'-\\1', regex=True)
                    # Remove $ and , characters
                    df[col] = df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            
            # Try to convert appropriate columns to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='ignore')
                
            return df
        except Exception as e:
            print(f"Error cleaning table: {e}")
            return df  # Return original on error