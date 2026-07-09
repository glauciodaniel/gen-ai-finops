import pytest
from scrapy.exceptions import DropItem

from pricing.pipelines import ValidationPipeline, LiteLLMCrossCheckPipeline


def _valid_item():
    return {
        "provider": "openai",
        "slug": "gpt-4o",
        "displayName": "GPT-4o",
        "inputPer1M": 2.5,
        "outputPer1M": 10.0,
    }


def test_validation_accepts_valid_item():
    pipeline = ValidationPipeline()
    item = _valid_item()
    assert pipeline.process_item(item, None) is item


@pytest.mark.parametrize("missing_field", ["provider", "slug", "displayName", "inputPer1M", "outputPer1M"])
def test_validation_rejects_missing_required(missing_field):
    pipeline = ValidationPipeline()
    item = _valid_item()
    item[missing_field] = None
    with pytest.raises(DropItem):
        pipeline.process_item(item, None)


def test_validation_rejects_negative_price():
    pipeline = ValidationPipeline()
    item = _valid_item()
    item["inputPer1M"] = -1.0
    with pytest.raises(DropItem):
        pipeline.process_item(item, None)


def test_cross_check_flags_divergent_price():
    pipeline = LiteLLMCrossCheckPipeline(litellm_url="unused", threshold=0.2)
    pipeline.reference = {
        "gpt-4o": {
            "input_cost_per_token": 0.0000025,
            "output_cost_per_token": 0.00001,
        }
    }
    item = _valid_item()
    item["inputPer1M"] = 5.0  # doubled vs. 2.5 in reference
    pipeline.process_item(item, None)
    assert any("gpt-4o" in msg for msg in pipeline.divergences)


def test_cross_check_ignores_within_threshold():
    pipeline = LiteLLMCrossCheckPipeline(litellm_url="unused", threshold=0.2)
    pipeline.reference = {
        "gpt-4o": {
            "input_cost_per_token": 0.0000025,
            "output_cost_per_token": 0.00001,
        }
    }
    item = _valid_item()
    item["inputPer1M"] = 2.6
    pipeline.process_item(item, None)
    assert not pipeline.divergences
