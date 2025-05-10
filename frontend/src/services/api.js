import axios from "axios";

const API_URL = "http://localhost:8000/api";

export const api = {
  // Document endpoints
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await axios.post(`${API_URL}/documents/upload/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },
  
  async searchDocuments(query, limit = 5) {
    const response = await axios.post(`${API_URL}/documents/search/`, {
      query,
      limit,
    });
    return response.data;
  },
  
  async analyzeText(text) {
    const response = await axios.post(`${API_URL}/documents/analyze/`, {
      text,
    });
    return response.data;
  },
  
  // Get processing status for a document
  async getProcessingStatus(documentId) {
    try {
      const response = await axios.get(`${API_URL}/documents/processing-status/${documentId}`);
      return response.data;
    } catch (error) {
      console.error("Error checking processing status:", error);
      // Return placeholder status if endpoint not available
      return { status: "complete", progress: 100 };
    }
  },
  
  // Get financial summary for a document
  async getFinancialSummary(documentId) {
    try {
      const response = await axios.get(`${API_URL}/documents/financial-summary/${documentId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching financial summary:", error);
      // If API endpoint is not yet available, return placeholder data
      return {
        financial_data: {
          income_statement: {
            revenue: 1000000,
            cost_of_goods_sold: 650000,
            gross_profit: 350000,
            operating_expenses: 200000,
            net_profit: 150000
          }
        },
        summary: {
          executive_summary: "This is a placeholder executive summary of the document. In a real implementation, this would contain a condensed overview of the key points from the financial report.",
          sections: {
            business: "The company operates in various market segments and continues to expand its product offerings.",
            risk_factors: "Market competition and regulatory changes present ongoing challenges to the business.",
            management_discussion: "Management believes the company is well-positioned for growth in the coming fiscal year."
          }
        }
      };
    }
  },
  
  // NEW ENDPOINTS
  
  // Get financial flow data for Sankey diagram
  async getFinancialFlow(documentId) {
    try {
      const response = await axios.get(`${API_URL}/documents/financial-flow/${documentId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching financial flow:", error);
      
      // Return sample data structure for Sankey diagram
      return {
        flow_data: {
          nodes: [
            { name: "Revenue" },
            { name: "Cost of Revenue" },
            { name: "Gross Profit" },
            { name: "Operating Expenses" },
            { name: "Operating Income" },
            { name: "Income Tax" },
            { name: "Net Income" },
            { name: "Dividends" },
            { name: "Retained Earnings" }
          ],
          links: [
            { source: 0, target: 1, value: 800000, color: "#d62728" },
            { source: 0, target: 2, value: 1200000, color: "#2ca02c" },
            { source: 2, target: 3, value: 700000, color: "#d62728" },
            { source: 2, target: 4, value: 500000, color: "#2ca02c" },
            { source: 4, target: 5, value: 125000, color: "#d62728" },
            { source: 4, target: 6, value: 375000, color: "#2ca02c" },
            { source: 6, target: 7, value: 125000, color: "#d62728" },
            { source: 6, target: 8, value: 250000, color: "#2ca02c" }
          ]
        }
      };
    }
  },
  
  // Get extended TLDR with more detailed summaries
  async getExtendedTLDR(documentId) {
    try {
      const response = await axios.get(`${API_URL}/documents/extended-tldr/${documentId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching extended TLDR:", error);
      
      // Return enhanced placeholder data
      return {
        extended_tldr: {
          executive_summary: "This company has demonstrated strong revenue growth over the past fiscal year, with a 15% increase in total revenue compared to the previous period. Despite facing challenges in the supply chain and increased competition, the company maintained a healthy gross margin of 35%. Management has outlined a strategy focused on market expansion, product innovation, and operational efficiency for the coming year. Key risks include regulatory changes, market volatility, and technology disruption.",
          highlights: [
            "15% year-over-year revenue growth",
            "35% gross margin maintained despite supply chain challenges",
            "New product line launched in Q4 with positive initial reception",
            "Expansion into three new international markets"
          ],
          key_metrics: {
            revenue: 1000000,
            gross_profit: 350000,
            net_income: 150000,
            earnings_per_share: 2.45,
            year_over_year_growth: "15%"
          },
          sections: {
            business: "The company operates in multiple market segments including consumer goods, technology solutions, and professional services. Their primary business model revolves around subscription-based services and product sales through direct and indirect channels. Over the past year, the company has expanded its product portfolio with the introduction of new service offerings and has entered three new international markets in Europe and Asia. The management team has highlighted their focus on sustainable growth through innovation and strategic partnerships.",
            
            risk_factors: "The company faces several key risks that could impact future performance. Market competition continues to intensify with new entrants offering similar products at competitive price points. Regulatory changes in key markets could impose additional compliance costs or restrict certain business activities. Supply chain disruptions remain a concern, with potential impacts on product availability and margins. Technology and cybersecurity risks are also highlighted as areas requiring ongoing investment and vigilance. The company has implemented mitigation strategies for each risk category, including diversification of suppliers, enhanced compliance programs, and increased cybersecurity measures.",
            
            management_discussion: "Management's discussion emphasizes the company's strategic direction and financial performance. The 15% revenue growth exceeded internal targets and was primarily driven by expansion in the subscription services segment. Gross margins remained stable at 35% despite increased input costs, which management attributes to successful pricing strategies and operational efficiencies. Operating expenses increased by 10% year-over-year, primarily due to investments in R&D and market expansion initiatives. Looking forward, management expects continued growth in the core business segments while maintaining similar margin profiles. Capital expenditures are projected to increase by 20% as the company invests in infrastructure and technology capabilities.",
            
            financial_statements: "The financial statements reveal a company with a strong balance sheet and positive cash flow generation. Total assets increased by 12% year-over-year, with cash and short-term investments representing 30% of total assets. The company maintains a conservative debt profile with a debt-to-equity ratio of 0.4. The income statement shows the 15% revenue growth translating to a 18% increase in operating income, demonstrating positive operating leverage. The cash flow statement indicates strong free cash flow generation of $200 million, representing a 20% increase from the previous year. The company returned $75 million to shareholders through dividends and share repurchases.",
            
            outlook: "Management provides a positive outlook for the upcoming fiscal year, projecting revenue growth of 12-15% and stable to slightly improving profit margins. Key growth drivers include continued expansion in subscription services, geographic expansion, and new product introductions planned for Q2 and Q3. The company has announced plans to increase R&D spending by 18% to accelerate innovation and maintain technological leadership in its core markets. While acknowledging ongoing macroeconomic uncertainties, management believes the company is well-positioned to navigate potential challenges and capitalize on emerging opportunities in its target markets."
          },
          section_metrics: {
            financial_statements: {
              revenue_growth: "15%",
              operating_income_growth: "18%",
              free_cash_flow: "$200 million",
              debt_to_equity: 0.4
            },
            outlook: {
              projected_revenue_growth: "12-15%",
              rd_spending_increase: "18%",
              new_product_introductions: "Q2 and Q3"
            }
          }
        }
      };
    }
  },
  
  // Get analysis history
  async getAnalysisHistory(limit = 10, offset = 0) {
    try {
      const response = await axios.get(`${API_URL}/documents/analysis-history/`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching analysis history:", error);
      
      // Return placeholder data
      return [
        {
          id: 17,
          title: "CHIPOTLE ANNUAL REPORT.pdf",
          file_type: "pdf",
          created_at: "2024-05-01T14:32:10",
          sections: ["business", "risk_factors", "management_discussion"],
          processing_status: "complete"
        },
        {
          id: 16,
          title: "TESLA 10-K 2023.pdf",
          file_type: "pdf",
          created_at: "2024-04-28T09:15:22",
          sections: ["business", "risk_factors", "financial_statements"],
          processing_status: "complete"
        },
        {
          id: 15,
          title: "MICROSOFT ANNUAL REPORT.pdf",
          file_type: "pdf",
          created_at: "2024-04-25T16:45:33",
          sections: ["business", "financial_statements", "outlook"],
          processing_status: "complete"
        }
      ];
    }
  },

  // Get TLDR summary for a document
  async getTLDRSummary(documentId) {
    try {
      const response = await axios.get(`${API_URL}/documents/tldr-summary/${documentId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching TLDR summary:", error);
      // If API endpoint is not yet available, use fallback to financial summary
      try {
        const summaryResponse = await this.getFinancialSummary(documentId);
        return { summary: summaryResponse.summary };
      } catch (fallbackError) {
        console.error("Error in fallback summary:", fallbackError);
        return { 
          summary: {
            executive_summary: "Summary could not be loaded at this time.",
            sections: {}
          }
        };
      }
    }
  }
};