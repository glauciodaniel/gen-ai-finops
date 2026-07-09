from pricing.spiders.base_litellm import BaseLiteLLMSpider


class AnthropicSpider(BaseLiteLLMSpider):
    name = "anthropic"
    provider_slug = "anthropic"
    match_prefixes = ("anthropic/", "claude-")
