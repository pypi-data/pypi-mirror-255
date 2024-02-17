import scrapy


class BaseItem(scrapy.Item):
    url = scrapy.Field()
    brand = scrapy.Field()
    status = scrapy.Field()
    status_code = scrapy.Field()
    last_crawl = scrapy.Field()
