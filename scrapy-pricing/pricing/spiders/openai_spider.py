from pricing.spiders.base_litellm import BaseLiteLLMSpider


class OpenAISpider(BaseLiteLLMSpider):
    name = "openai"
    provider_slug = "openai"
    match_prefixes = ("openai/", "gpt-", "o1", "o3", "o4", "text-embedding-", "dall-e", "whisper")
