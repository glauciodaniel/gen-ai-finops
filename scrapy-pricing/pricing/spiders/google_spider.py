from pricing.spiders.base_litellm import BaseLiteLLMSpider


class GoogleSpider(BaseLiteLLMSpider):
    name = "google"
    provider_slug = "google"
    match_prefixes = ("gemini/", "gemini-", "vertex_ai/gemini", "text-bison", "chat-bison")

    def _matches(self, key, entry):
        provider_field = str(entry.get("litellm_provider", "")).lower()
        if provider_field in ("gemini", "vertex_ai-language-models", "google"):
            return True
        return super()._matches(key, entry)
