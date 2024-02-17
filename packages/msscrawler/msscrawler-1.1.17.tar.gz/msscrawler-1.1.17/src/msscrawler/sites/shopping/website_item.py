import scrapy

from ...items.base import BaseItem

class WebsiteItem(BaseItem):
    brand = scrapy.Field()
    categories_num = scrapy.Field()
    category_urls = scrapy.Field()
    total_categories = scrapy.Field()