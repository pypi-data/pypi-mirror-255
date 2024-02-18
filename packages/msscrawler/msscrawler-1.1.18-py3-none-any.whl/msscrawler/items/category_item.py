import scrapy

from .base import BaseItem


class CategoryItem(BaseItem):
    name = scrapy.Field()
    css_selector = scrapy.Field()
    products_num = scrapy.Field()
    product_urls = scrapy.Field()
    from_page = scrapy.Field()
    to_page = scrapy.Field()
    next_page = scrapy.Field()
    id_category = scrapy.Field()
    breadcrumb = scrapy.Field()
    total_products = scrapy.Field()
