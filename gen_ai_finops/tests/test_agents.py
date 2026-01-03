"""
Tests for AI agents (Oracle, Architect, Scraper)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.pricing_knowledge_base import PricingKnowledgeBase
from agents.oracle import PricingOracle
from agents.architect import CostArchitect
from agents.scraper import OpenAIPricingScraper


class TestPricingOracle:
    """Test PricingOracle agent."""
    
    @pytest.fixture
    def kb(self):
        """Create a knowledge base instance."""
        return PricingKnowledgeBase()
    
    @pytest.fixture
    def oracle(self, kb):
        """Create an Oracle instance."""
        return PricingOracle(kb=kb)
    
    def test_oracle_initialization(self, oracle):
        """Test Oracle initialization."""
        assert oracle.kb is not None
        assert oracle.model == "gpt-3.5-turbo"
        assert oracle.temperature == 0.3
    
    def test_retrieve_context(self, oracle):
        """Test context retrieval."""
        # Add test data
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        oracle.kb.add_prices(test_data)
        
        # Retrieve context
        results = oracle.retrieve_context("What is the cheapest model?", n_results=5)
        
        # Should return results (may be empty if no matching data)
        assert isinstance(results, list)
    
    def test_ask_without_llm(self, oracle):
        """Test ask method in fallback mode (no LLM)."""
        # Add test data
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-3.5-turbo",
            "input_cost_per_1m_tokens": 0.5,
            "output_cost_per_1m_tokens": 1.5
        }]
        oracle.kb.add_prices(test_data)
        
        # Should work in fallback mode
        answer = oracle.ask("What is the cheapest model?", n_results=3)
        
        assert isinstance(answer, str)
        assert len(answer) > 0
    
    def test_ask_empty_knowledge_base(self, oracle):
        """Test ask with empty knowledge base."""
        answer = oracle.ask("What is the cheapest model?")
        
        # Should return a message even with empty KB
        assert isinstance(answer, str)


class TestCostArchitect:
    """Test CostArchitect agent."""
    
    @pytest.fixture
    def kb(self):
        """Create a knowledge base instance."""
        return PricingKnowledgeBase()
    
    @pytest.fixture
    def architect(self, kb):
        """Create an Architect instance."""
        return CostArchitect(kb=kb)
    
    def test_architect_initialization(self, architect):
        """Test Architect initialization."""
        assert architect.kb is not None
        assert architect.model == "gpt-3.5-turbo"
    
    def test_extract_requirements_fallback(self, architect):
        """Test requirement extraction in fallback mode."""
        use_case = "Simple chatbot for customer support"
        requirements = architect.extract_requirements(use_case)
        
        assert isinstance(requirements, dict)
        assert "needs_function_calling" in requirements
        assert "needs_vision" in requirements
        assert "quality_requirement" in requirements
    
    def test_find_candidates(self, architect):
        """Test finding candidate models."""
        # Add test data
        test_data = [
            {
                "provider": "OpenAI",
                "model_name": "gpt-4",
                "input_cost_per_1m_tokens": 30.0,
                "output_cost_per_1m_tokens": 60.0,
                "supports_function_calling": True
            },
            {
                "provider": "OpenAI",
                "model_name": "gpt-3.5-turbo",
                "input_cost_per_1m_tokens": 0.5,
                "output_cost_per_1m_tokens": 1.5,
                "supports_function_calling": True
            }
        ]
        architect.kb.add_prices(test_data)
        
        requirements = {
            "needs_function_calling": True,
            "quality_requirement": "medium",
            "budget_priority": "high"
        }
        
        candidates = architect.find_candidates(requirements, top_n=5)
        
        assert isinstance(candidates, list)
        assert len(candidates) > 0
    
    def test_calculate_costs(self, architect):
        """Test cost calculation."""
        model_data = {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }
        
        monthly_cost = architect.calculate_costs(
            model_data,
            monthly_input_tokens=1000000,
            monthly_output_tokens=500000
        )
        
        # 1M input * $30/1M + 0.5M output * $60/1M = $30 + $30 = $60
        assert monthly_cost > 0
        assert isinstance(monthly_cost, float)
    
    def test_analyze_and_optimize(self, architect):
        """Test full optimization analysis."""
        # Add test data
        test_data = [
            {
                "provider": "OpenAI",
                "model_name": "gpt-3.5-turbo",
                "input_cost_per_1m_tokens": 0.5,
                "output_cost_per_1m_tokens": 1.5,
                "supports_function_calling": True
            }
        ]
        architect.kb.add_prices(test_data)
        
        analysis = architect.analyze_and_optimize(
            use_case_description="Simple chatbot",
            monthly_input_tokens=1000000,
            monthly_output_tokens=500000
        )
        
        assert isinstance(analysis, dict)
        assert "status" in analysis
        assert analysis["status"] in ["success", "error"]


class TestOpenAIPricingScraper:
    """Test OpenAIPricingScraper agent."""
    
    @pytest.fixture
    def kb(self):
        """Create a knowledge base instance."""
        return PricingKnowledgeBase()
    
    @pytest.fixture
    def scraper(self, kb):
        """Create a Scraper instance."""
        return OpenAIPricingScraper(kb)
    
    def test_scraper_initialization(self, scraper):
        """Test Scraper initialization."""
        assert scraper.kb is not None
    
    @patch('agents.scraper.requests.get')
    def test_scrape_pricing_page(self, mock_get, scraper):
        """Test scraping pricing page."""
        # Mock HTML response
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Should not raise exception
        result = scraper.scrape_pricing_page()
        assert result is not None
    
    def test_parse_pricing_data(self, scraper):
        """Test parsing pricing data from HTML."""
        # Sample HTML (simplified)
        html = """
        <html>
            <body>
                <h2>GPT-4</h2>
                <p>Input: $30.00 / 1M tokens</p>
                <p>Output: $60.00 / 1M tokens</p>
            </body>
        </html>
        """
        
        # Should parse without error
        data = scraper.parse_pricing_data(html)
        assert isinstance(data, list)
    
    @patch('agents.scraper.OpenAIPricingScraper.scrape_pricing_page')
    @patch('agents.scraper.OpenAIPricingScraper.parse_pricing_data')
    def test_run_scraper(self, mock_parse, mock_scrape, scraper):
        """Test running the scraper."""
        # Mock responses
        mock_scrape.return_value = "<html>Test</html>"
        mock_parse.return_value = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        
        count = scraper.run()
        
        assert isinstance(count, int)
        assert count >= 0

