import os

from dotenv import load_dotenv

from ....spiders.base import BaseSpider
from ..website_item import WebsiteItem


class WebsiteTheamallSpider(BaseSpider):

    name = "theamall.com"

    def __init__(self, url):
        super().__init__(url=url)
        load_dotenv(os.path.abspath('.env-base'))

    def is_element_valid(self, element):
        if "/goods/category?cate=" in element:
            return True
        else:
            return False

    def process_response(self, response, items, response_elements):
        items = super().process_response(response, items, response_elements)
        items["name"] = "TheAMall"
        items["brand"] = "TheAMall"

        return items

    @staticmethod
    def get_new_item_instance():
        return WebsiteItem()

    def set_default_value(self):
        items = super().set_default_value()
        # all field use to update record after crawling
        items["brand"] = ""  # update when error
        items["categories_num"] = []
        items["total_categories"] = 0  # update when error

        # use in pipeline to create categories and send message
        items["category_urls"] = []
        return items

    def get_css_selector(self):
        return "#header > div.gnb > ul > li > div.over-area > div.contents > dl.cate-list a::attr(href)"