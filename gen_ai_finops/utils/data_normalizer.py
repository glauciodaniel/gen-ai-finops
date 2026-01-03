"""
Data Normalizer for GenAIFinOps
Validates and normalizes pricing data according to the standard schema.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, field_validator


class PricingModel(BaseModel):
    """Pydantic model for LLM pricing data validation."""

    provider: str = Field(..., description="Provider name (e.g., OpenAI, Anthropic)")
    model_name: str = Field(..., description="Official model name")
    model_display_name: Optional[str] = Field(None, description="Human-friendly display name")
    input_cost_per_1m_tokens: float = Field(..., ge=0, description="Cost per 1M input tokens (USD)")
    output_cost_per_1m_tokens: float = Field(..., ge=0, description="Cost per 1M output tokens (USD)")
    context_window: Optional[int] = Field(None, ge=0, description="Max context window in tokens")
    supports_function_calling: bool = Field(default=False)
    supports_vision: bool = Field(default=False)
    supports_json_mode: bool = Field(default=False)
    max_output_tokens: Optional[int] = Field(None, ge=0)
    training_data_cutoff: Optional[str] = Field(None)
    additional_features: List[str] = Field(default_factory=list)
    pricing_url: Optional[str] = Field(None)
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    notes: Optional[str] = Field(None)

    @field_validator('model_display_name', mode='before')
    @classmethod
    def set_display_name(cls, v: Optional[str], info) -> str:
        """Auto-generate display name from model_name if not provided."""
        if v is None and 'model_name' in info.data:
            return info.data['model_name'].replace('-', ' ').title()
        return v or ""


def validate_pricing_data(data: Dict[str, Any]) -> bool:
    """
    Validates if a dictionary follows the pricing schema.

    Args:
        data: Dictionary containing pricing information

    Returns:
        bool: True if valid, raises ValidationError otherwise

    Raises:
        ValidationError: If data doesn't match schema
    """
    try:
        PricingModel(**data)
        return True
    except Exception as e:
        raise ValueError(f"Pricing data validation failed: {str(e)}")


def normalize_pricing_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes raw pricing data to match the standard schema.

    Args:
        raw_data: Raw pricing data from scraper

    Returns:
        Dict: Normalized pricing data
    """
    pricing_model = PricingModel(**raw_data)
    return pricing_model.model_dump()


def normalize_batch(raw_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizes a batch of pricing data entries.

    Args:
        raw_data_list: List of raw pricing data dictionaries

    Returns:
        List[Dict]: List of normalized pricing data
    """
    normalized = []
    errors = []

    for idx, raw_data in enumerate(raw_data_list):
        try:
            normalized.append(normalize_pricing_data(raw_data))
        except Exception as e:
            errors.append(f"Entry {idx}: {str(e)}")

    if errors:
        print(f"Warning: {len(errors)} entries failed validation:")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")

    return normalized


def load_schema() -> Dict[str, Any]:
    """
    Loads the pricing schema JSON file.

    Returns:
        Dict: The pricing schema
    """
    schema_path = Path(__file__).parent.parent / "data" / "pricing_schema.json"
    with open(schema_path, 'r') as f:
        return json.load(f)


def pricing_to_text(pricing_data: Dict[str, Any]) -> str:
    """
    Converts pricing data to a human-readable text format for embeddings.
    This text representation is what gets vectorized in ChromaDB.

    Args:
        pricing_data: Normalized pricing data

    Returns:
        str: Text representation optimized for semantic search
    """
    provider = pricing_data.get('provider', 'Unknown')
    model = pricing_data.get('model_name', 'Unknown')
    display_name = pricing_data.get('model_display_name', model)
    input_cost = pricing_data.get('input_cost_per_1m_tokens', 0)
    output_cost = pricing_data.get('output_cost_per_1m_tokens', 0)
    context = pricing_data.get('context_window', 'N/A')

    text_parts = [
        f"Provider: {provider}",
        f"Model: {model} ({display_name})",
        f"Pricing: ${input_cost} per 1M input tokens, ${output_cost} per 1M output tokens",
    ]

    if context != 'N/A':
        text_parts.append(f"Context Window: {context:,} tokens")

    features = []
    if pricing_data.get('supports_function_calling'):
        features.append('function calling')
    if pricing_data.get('supports_vision'):
        features.append('vision/image input')
    if pricing_data.get('supports_json_mode'):
        features.append('JSON mode')

    if features:
        text_parts.append(f"Features: {', '.join(features)}")

    if pricing_data.get('additional_features'):
        text_parts.append(f"Additional: {', '.join(pricing_data['additional_features'])}")

    if pricing_data.get('notes'):
        text_parts.append(f"Notes: {pricing_data['notes']}")

    return " | ".join(text_parts)


if __name__ == "__main__":
    sample_data = {
        "provider": "OpenAI",
        "model_name": "gpt-4",
        "input_cost_per_1m_tokens": 30.0,
        "output_cost_per_1m_tokens": 60.0,
        "context_window": 8192,
        "supports_function_calling": True,
        "supports_json_mode": True
    }

    print("Testing data normalization...")
    normalized = normalize_pricing_data(sample_data)
    print(json.dumps(normalized, indent=2))

    print("\nConverting to text for embedding:")
    text = pricing_to_text(normalized)
    print(text)
