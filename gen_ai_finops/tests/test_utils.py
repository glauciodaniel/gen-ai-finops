"""
Tests for utility modules
"""
import pytest
from utils.pricing_knowledge_base import PricingKnowledgeBase
from utils.data_normalizer import (
    validate_pricing_data,
    normalize_pricing_data,
    pricing_to_text
)


class TestPricingKnowledgeBase:
    """Test PricingKnowledgeBase utility."""
    
    @pytest.fixture
    def kb(self):
        """Create a knowledge base instance."""
        return PricingKnowledgeBase()
    
    def test_kb_initialization(self, kb):
        """Test knowledge base initialization."""
        assert kb.collection is not None
        assert kb.collection_name == "pricing_models"
    
    def test_add_prices(self, kb):
        """Test adding pricing data."""
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        
        count = kb.add_prices(test_data)
        assert count == 1
    
    def test_add_prices_multiple(self, kb):
        """Test adding multiple pricing entries."""
        test_data = [
            {
                "provider": "OpenAI",
                "model_name": "gpt-4",
                "input_cost_per_1m_tokens": 30.0,
                "output_cost_per_1m_tokens": 60.0
            },
            {
                "provider": "OpenAI",
                "model_name": "gpt-3.5-turbo",
                "input_cost_per_1m_tokens": 0.5,
                "output_cost_per_1m_tokens": 1.5
            }
        ]
        
        count = kb.add_prices(test_data)
        assert count == 2
    
    def test_query_prices(self, kb):
        """Test semantic search."""
        # Add test data
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        kb.add_prices(test_data)
        
        # Query
        results = kb.query_prices("cheapest model", n_results=5)
        
        assert isinstance(results, list)
    
    def test_get_stats(self, kb):
        """Test getting statistics."""
        # Add some data
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        kb.add_prices(test_data)
        
        stats = kb.get_stats()
        
        assert isinstance(stats, dict)
        assert "total_models" in stats
        assert "providers" in stats
        assert stats["total_models"] >= 1
    
    def test_get_all_providers(self, kb):
        """Test getting all providers."""
        # Add test data
        test_data = [
            {
                "provider": "OpenAI",
                "model_name": "gpt-4",
                "input_cost_per_1m_tokens": 30.0,
                "output_cost_per_1m_tokens": 60.0
            },
            {
                "provider": "Anthropic",
                "model_name": "claude-3",
                "input_cost_per_1m_tokens": 15.0,
                "output_cost_per_1m_tokens": 75.0
            }
        ]
        kb.add_prices(test_data)
        
        providers = kb.get_all_providers()
        
        assert isinstance(providers, list)
        assert "OpenAI" in providers
        assert "Anthropic" in providers
    
    def test_get_all_models(self, kb):
        """Test getting all models."""
        # Add test data
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        kb.add_prices(test_data)
        
        models = kb.get_all_models()
        
        assert isinstance(models, list)
        assert len(models) >= 1
        assert any(m["model_name"] == "gpt-4" for m in models)
    
    def test_clear_all(self, kb):
        """Test clearing all data."""
        # Add data
        test_data = [{
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }]
        kb.add_prices(test_data)
        
        # Clear
        kb.clear_all()
        
        # Verify cleared
        stats = kb.get_stats()
        assert stats["total_models"] == 0


class TestDataNormalizer:
    """Test DataNormalizer utility."""
    
    def test_validate_pricing_data_valid(self):
        """Test validation of valid pricing data."""
        valid_data = {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }
        
        result = validate_pricing_data(valid_data)
        assert result is True
    
    def test_validate_pricing_data_invalid(self):
        """Test validation of invalid pricing data."""
        invalid_data = {
            "provider": "OpenAI",
            # Missing required fields
        }
        
        with pytest.raises(Exception):  # Should raise ValidationError
            validate_pricing_data(invalid_data)
    
    def test_normalize_pricing_data(self):
        """Test data normalization."""
        raw_data = {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }
        
        normalized = normalize_pricing_data(raw_data)
        
        assert isinstance(normalized, dict)
        assert "provider" in normalized
        assert "model_name" in normalized
        assert "input_cost_per_1m_tokens" in normalized
        assert "output_cost_per_1m_tokens" in normalized
    
    def test_normalize_pricing_data_with_defaults(self):
        """Test normalization with default values."""
        minimal_data = {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0
        }
        
        normalized = normalize_pricing_data(minimal_data)
        
        # Should have defaults
        assert normalized.get("supports_function_calling") is not None
        assert normalized.get("supports_vision") is not None
    
    def test_pricing_to_text(self):
        """Test converting pricing data to text."""
        data = {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0,
            "context_window": 8192,
            "supports_function_calling": True
        }
        
        text = pricing_to_text(data)
        
        assert isinstance(text, str)
        assert "OpenAI" in text
        assert "gpt-4" in text
        assert "30" in text or "30.0" in text
    
    def test_normalize_with_none_values(self):
        """Test normalization handles None values."""
        data_with_none = {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0,
            "context_window": None,
            "email": None
        }
        
        normalized = normalize_pricing_data(data_with_none)
        
        # Should not raise error
        assert isinstance(normalized, dict)

