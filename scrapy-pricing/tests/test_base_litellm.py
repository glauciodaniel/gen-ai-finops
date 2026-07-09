from pricing.spiders.base_litellm import BaseLiteLLMSpider


class DummySpider(BaseLiteLLMSpider):
    name = "dummy"
    provider_slug = "openai"
    match_prefixes = ("openai/", "gpt-")


LITELLM_ENTRY = {
    "max_tokens": 128000,
    "max_input_tokens": 128000,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0000025,
    "output_cost_per_token": 0.00001,
    "cache_read_input_token_cost": 0.00000125,
    "litellm_provider": "openai",
    "mode": "chat",
    "supports_function_calling": True,
    "supports_vision": True,
    "supports_response_schema": True,
}


def test_to_item_converts_per_token_to_per_million():
    spider = DummySpider()
    item = spider._to_item("gpt-4o", LITELLM_ENTRY)
    assert item is not None
    assert item["provider"] == "openai"
    assert item["slug"] == "gpt-4o"
    assert item["inputPer1M"] == 2.5
    assert item["outputPer1M"] == 10.0
    assert item["cachedInputPer1M"] == 1.25
    assert item["contextWindow"] == 128000
    assert item["maxOutput"] == 16384
    assert item["supportsTools"] is True
    assert item["supportsVision"] is True
    assert item["supportsJson"] is True
    assert item["modality"] == "text"
    assert item["source"] == "litellm"


def test_matches_by_prefix():
    spider = DummySpider()
    assert spider._matches("openai/gpt-4o", {"litellm_provider": "openai"})
    assert spider._matches("gpt-4o", {"litellm_provider": "other"})
    assert not spider._matches("claude-3", {"litellm_provider": "anthropic"})


def test_normalize_slug_strips_provider_prefix():
    spider = DummySpider()
    assert spider._normalize_slug("openai/gpt-4o") == "gpt-4o"
    assert spider._normalize_slug("gpt-4o") == "gpt-4o"


def test_to_item_skips_when_no_prices():
    spider = DummySpider()
    entry = dict(LITELLM_ENTRY)
    entry.pop("input_cost_per_token")
    assert spider._to_item("gpt-4o", entry) is None


def test_modality_mapping():
    assert BaseLiteLLMSpider._map_modality("chat") == "text"
    assert BaseLiteLLMSpider._map_modality("embedding") == "embedding"
    assert BaseLiteLLMSpider._map_modality("image_generation") == "image"
    assert BaseLiteLLMSpider._map_modality("audio_transcription") == "audio"
    assert BaseLiteLLMSpider._map_modality("unknown") == "text"
