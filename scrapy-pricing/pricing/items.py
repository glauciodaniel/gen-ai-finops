import scrapy


class ModelPricingItem(scrapy.Item):
    provider = scrapy.Field()
    slug = scrapy.Field()
    displayName = scrapy.Field()
    modality = scrapy.Field()
    contextWindow = scrapy.Field()
    maxOutput = scrapy.Field()
    supportsTools = scrapy.Field()
    supportsVision = scrapy.Field()
    supportsJson = scrapy.Field()
    deprecated = scrapy.Field()
    inputPer1M = scrapy.Field()
    outputPer1M = scrapy.Field()
    cachedInputPer1M = scrapy.Field()
    currency = scrapy.Field()
    source = scrapy.Field()
