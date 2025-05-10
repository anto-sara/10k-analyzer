from transformers import pipeline
from typing import Dict, Any, List
import re

class EnhancedReportSummarizer:
    """Generate more comprehensive and detailed summaries of financial reports"""
    
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            max_length=1500,  # Increased for longer summaries
            min_length=200    # More substantial minimum length
        )
        
        # Define key sections with more detailed descriptions
        self.key_sections = [
            "business",
            "risk_factors",
            "management_discussion",
            "financial_statements",
            "outlook",
            "operating_results",
            "liquidity",
            "off_balance_sheet",
            "contractual_obligations",
            "market_risk"
        ]
    
    def generate_executive_summary(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Generate a detailed executive summary with highlights and key metrics"""
        # Combine important points from each section
        section_highlights = []
        
        for section_name, content in sections.items():
            if section_name in self.key_sections and content:
                # Get a brief highlight from each key section
                highlight = self._extract_highlight(content)
                if highlight:
                    section_highlights.append(f"{section_name.replace('_', ' ').title()}: {highlight}")
        
        # Combine highlights into a coherent summary
        combined = " ".join(section_highlights)
        
        # Create an executive summary from the combined highlights
        if len(combined) > 200:
            summary_text = self.summarizer(combined, max_length=500, min_length=200)[0]['summary_text']
        else:
            summary_text = combined
        
        # Extract key metrics and highlights
        key_metrics = self._extract_key_metrics(sections)
        highlights = self._extract_highlights(sections)
            
        return {
            "executive_summary": summary_text,
            "key_metrics": key_metrics,
            "highlights": highlights
        }
    
    def _extract_highlight(self, text: str, max_words: int = 50) -> str:
        """Extract a key highlight from text"""
        # Simple implementation - get the first few sentences
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return ""
            
        # Get the first few sentences up to max_words
        highlight = ""
        word_count = 0
        
        for sentence in sentences:
            words = sentence.split()
            if word_count + len(words) <= max_words:
                highlight += sentence + ". "
                word_count += len(words)
            else:
                break
                
        return highlight
    
    def _extract_key_metrics(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract key financial metrics from sections"""
        metrics = {}
        
        # Look for financial metrics in the management discussion section
        md_section = sections.get("management_discussion", "")
        if md_section:
            # Extract revenue mentions
            revenue_match = re.search(r'revenue of \$?(\d+(?:\.\d+)?)\s*(million|billion|trillion)?', md_section.lower())
            if revenue_match:
                value = float(revenue_match.group(1))
                if revenue_match.group(2) == "billion":
                    value *= 1000000000
                elif revenue_match.group(2) == "million":
                    value *= 1000000
                elif revenue_match.group(2) == "trillion":
                    value *= 1000000000000
                metrics["revenue"] = value
            
            # Extract growth percentages
            growth_match = re.search(r'(?:increased|decreased|grew|declined) by (\d+(?:\.\d+)?)%', md_section.lower())
            if growth_match:
                metrics["year_over_year_growth"] = f"{growth_match.group(1)}%"
            
            # Extract margins
            margin_match = re.search(r'(?:gross|operating|profit) margin of (\d+(?:\.\d+)?)%', md_section.lower())
            if margin_match:
                metrics["margin"] = f"{margin_match.group(1)}%"
        
        return metrics
    
    def _extract_highlights(self, sections: Dict[str, str]) -> List[str]:
        """Extract key highlights from all sections"""
        highlights = []
        
        # Look for bullet points or numbered lists
        for section_name, content in sections.items():
            if not content:
                continue
                
            # Look for lines that might be bullet points
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # Check if line starts with a bullet, number, or similar pattern
                if re.match(r'^[\•\-\*\d\(\[\.\○\★]\s+', line):
                    # Clean up the bullet point
                    clean_line = re.sub(r'^[\•\-\*\d\(\[\.\○\★]\s+', '', line)
                    if 10 < len(clean_line) < 150:  # Reasonable length for a highlight
                        highlights.append(clean_line)
        
        # If we couldn't find explicit bullet points, generate some from key sentences
        if len(highlights) < 3:
            for section_name in ["business", "outlook", "management_discussion"]:
                if section_name in sections and sections[section_name]:
                    sentences = re.split(r'[.!?]', sections[section_name])
                    sentences = [s.strip() for s in sentences if s.strip()]
                    for sentence in sentences[:5]:  # Check first few sentences
                        # Look for sentences with indicators of importance
                        if re.search(r'key|significant|important|major|primary|critical|growth|increase|improve', sentence.lower()):
                            if len(sentence) > 20 and sentence not in highlights:
                                highlights.append(sentence)
        
        # Return top 5 highlights
        return highlights[:5]
    
    def summarize_section(self, section_text: str, max_words: int = 500) -> str:
        """Summarize a single section of the report with more detail"""
        # Split into chunks if longer than model can handle
        chunks = self._split_into_chunks(section_text)
        
        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            if len(chunk) > 200:  # Only summarize substantial chunks
                summary = self.summarizer(chunk, max_length=500, min_length=100)[0]['summary_text']
                summaries.append(summary)
        
        # Combine summaries
        combined = " ".join(summaries)
        
        # Ensure text isn't too short
        if len(combined) < 100 and section_text:
            # Just use the beginning of the text
            words = section_text.split()[:max_words]
            combined = " ".join(words) + "..."
        
        return combined
    
    def create_extended_tldr(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Create a comprehensive TLDR summary of the financial report"""
        # Generate executive summary with metrics and highlights
        executive_summary = self.generate_executive_summary(sections)
        
        # Create the TLDR structure
        tldr = {
            "executive_summary": executive_summary["executive_summary"],
            "highlights": executive_summary["highlights"],
            "key_metrics": executive_summary["key_metrics"],
            "sections": {},
            "section_metrics": {}
        }
        
        # Summarize each section with more detail
        for section_name, content in sections.items():
            if section_name in self.key_sections and content:
                tldr["sections"][section_name] = self.summarize_section(content, max_words=500)
        
        # Add section-specific metrics if available
        financial_section = sections.get("financial_statements", "")
        if financial_section:
            metrics = {}
            
            # Extract revenue growth
            growth_match = re.search(r'revenue growth of (\d+(?:\.\d+)?)%', financial_section.lower())
            if growth_match:
                metrics["revenue_growth"] = f"{growth_match.group(1)}%"
            
            # Extract operating income
            income_match = re.search(r'operating income (?:increased|decreased) (?:by )?(\d+(?:\.\d+)?)%', financial_section.lower())
            if income_match:
                metrics["operating_income_growth"] = f"{income_match.group(1)}%"
            
            tldr["section_metrics"]["financial_statements"] = metrics
        
        # Add outlook metrics if available
        outlook_section = sections.get("outlook", "")
        if outlook_section:
            metrics = {}
            
            # Extract projected growth
            projection_match = re.search(r'project(?:ing|ed|s)? (?:a |an )?(?:increase|growth|rise) of (\d+(?:\.\d+)?(?:\-\d+(?:\.\d+)?)?)%', outlook_section.lower())
            if projection_match:
                metrics["projected_growth"] = f"{projection_match.group(1)}%"
            
            tldr["section_metrics"]["outlook"] = metrics
        
        return tldr
    
    def _split_into_chunks(self, text: str, max_length: int = 1500) -> List[str]:
        """Split text into chunks that the model can handle"""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) >= max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks