from pricing.spiders.base_litellm import BaseLiteLLMSpider


class GoogleSpider(BaseLiteLLMSpider):
    name = "google"
    provider_slug = "google"
    match_prefixes = ("gemini/", "gemini-", "vertex_ai/gemini", "text-bison", "chat-bison")
    # Google models are marked with several distinct litellm_provider values;
    # accept any of them without duplicating the prefix logic in the base.
    match_litellm_providers = ("gemini", "vertex_ai-language-models", "google")
