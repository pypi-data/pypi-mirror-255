from .base import BaseSpider
from ..items.product_item import ProductItem


class ProductSpider(BaseSpider):
    instance = "product"
    allProduct = []
    tempProduct = []

    # def __init__(self, url, category_id):
    #     super().__init__(url)
    #     self.category_id = category_id

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)

    @staticmethod
    def get_new_item_instance():
        return ProductItem()

    def set_default_value(self):
        items = super().set_default_value()
        items["product_id"] = ""  # update when error
        items["competitor"] = ""  # update when error
        items["good_nm"] = ""  # update when error
        items["normal_price"] = None  # update when error
        items["sale_price"] = None  # update when error
        items["shipping_price"] = 0  # update when error
        items["shipping_type"] = 1  # update when error
        items["shipping_condition"] = 0  # update when error
        items["options"] = []  # update when error
        items["total_options"] = 0  # update when error
        items["currency"] = "KRW"  # update when error
        items["category_id"] = self.category_id
        items["image_urls"] = []
        return items
