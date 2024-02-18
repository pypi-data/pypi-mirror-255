from urllib.parse import urlparse

from .base import BaseSpider
from ..items.category_item import CategoryItem


class CategorySpider(BaseSpider):
    instance = "category"
    current_page = 0

    # def __init__(self, url, website_id, root_obj_id, source_type):
    #     super().__init__(url)
    #     self.website_id = website_id
    #     self.root_obj_id = root_obj_id
    #     self.source_type = source_type

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)

    @staticmethod
    def get_new_item_instance():
        return CategoryItem()

    def set_default_value(self):
        items = super().set_default_value()
        items["name"] = ""  # update when error
        items["css_selector"] = ""
        items["products_num"] = []
        items["from_page"] = 0  # update when error
        items["to_page"] = 0  # update when error
        items["next_page"] = ""  # update when error
        items["id_category"] = ""
        items["breadcrumb"] = ""
        items["total_products"] = 0  # update when error
        # use in pipeline to create product and send message
        items["product_urls"] = []
        return items
