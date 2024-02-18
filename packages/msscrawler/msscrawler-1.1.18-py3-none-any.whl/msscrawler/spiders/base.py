import traceback
from datetime import datetime
import os
from urllib.parse import urlparse
import random
import requests
import scrapy
from scrapy import spiders
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from ..items.base import BaseItem
from ..log.default import get_default_log
from ..connectors.message_brokers.rabbitmq_connector import RabbitMQConnector


class BaseSpider(spiders.Spider):
    start_urls = []
    name = "base_name"  # override
    instance = ""  # override
    driver = None  # driver use for case selenium
    special_field = ["root_obj_id", "category_id"]

    def __init__(self, url, **kwargs):
        super().__init__()
        if f"//www.{self.name}" in url:
            url = url.replace(f"//www.{self.name}", f"//{self.name}")
        if f"//m.{self.name}" in url:
            url = url.replace(f"//m.{self.name}", f"//{self.name}")
        self.start_urls = [url]
        self.instance_url = url
        self.graylog = get_default_log(self.instance)
        self.site_name = "-"

        querys = urlparse(url).query
        if querys != "":
            query_dict = {}

            for query in querys.split("&"):
                query_key = query.split("=")[0]
                query_value = query.split("=")[1]
                query_dict[f"{query_key}"] = query_value

            self.query_dict = query_dict

        for field in self.special_field:
            setattr(self, field, kwargs.get(field, None))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    @staticmethod
    def get_new_item_instance():
        return BaseItem()

    def set_default_value(self):
        items = self.get_new_item_instance()
        items["url"] = ""
        items["brand"] = ""  # update when error
        items["status"] = "error"  # update when error
        items["status_code"] = ""
        items["last_crawl"] = datetime.now()  # update when error
        return items

    def process_crawl(self, response, items):
        """Crawl information of specific page
        Returns: item must have status = success, status_code from response
        """
        return items

    def set_value_after_process_crawl(self, response, items, is_selenium=False):
        items["url"] = self.instance_url
        items["last_crawl"] = datetime.now()

        # selenium can not get status code
        if not is_selenium:
            items["status_code"] = str(response.status)

        return items

    def parse(self, response):
        items = self.set_default_value()

        try:
            items = self.process_crawl(response, items)

        except Exception as error:
            # traceback.print_exc()
            # +log to log server
            self.graylog.error(
                f"[x] Error when crawl page {self.instance} (spider {self.name}: {self.instance_url}). \n"
                + traceback.format_exc()
            )
            items = self.set_default_value()
            if self.instance == "website":
                items["errors"].append(f"Status code: {str(response.status)}")
                items["errors"].append(
                    f"Error: {type(error).__name__}, Message: {str(error)}"
                )
        finally:
            if self.driver:
                self.driver.quit()

        items = self.set_value_after_process_crawl(response, items, is_selenium=False)

        yield items

    def get_host(self, protocol="https://", url=""):
        return (
            (protocol + urlparse(url).hostname)
            .replace("//www.", "//")
            .replace("//m.", "//")
        )

    def reduce_url(self, url):
        return url.replace("www.", "").replace("://m.", "://")

    def convertPrice(self, item):
        intPrice = item.split(",")
        return "".join(intPrice)

    def get_last_price(
        self,
        option_price,
        shipping_type,
        shipping_price,
        shipping_condition,
        price_above_quantity=0,
        minquantity=1,
    ):
        if shipping_type == "3":
            last_price = (
                (option_price + shipping_price)
                if (option_price < shipping_condition)
                else option_price
            )
        elif shipping_type == "4":
            last_price = (
                (option_price + shipping_price)
                if (minquantity < shipping_condition)
                else (option_price + price_above_quantity)
            )
        else:
            last_price = option_price + shipping_price

        return last_price

    def send_next_category_to_queue(self, body_message, category_url):
        try:
            rabbit_mq_conn = RabbitMQConnector(
                queue_declare=os.getenv("SPIDER_TRANSMIT_QUEUE")
            )

            body_message["is_root"] = "False"
            body_message["root_obj_id"] = self.root_obj_id
            body_message["source_type"] = self.source_type

            rabbit_mq_conn.send(
                message=body_message, target=os.getenv("SPIDER_TRANSMIT_QUEUE")
            )
            rabbit_mq_conn.close()
        except Exception as error:
            rabbit_mq_conn.close()
            raise Exception(
                f"Error when send next pagination category to queue (spider {self.name}: {category_url})."
            )

    def run_selenium(self, url, user_agent):
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-dev-shm-use")
            chrome_options.add_argument(f"--user-agent={user_agent}")

            # *use exact driver
            # driver = webdriver.Chrome(service=(driver_path), options=chrome_options)

            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(2)
            driver.get(url)

            return driver
        except Exception as error:
            if driver:
                driver.quit()
            self.graylog.error(
                f"[x] Error when crawl page {self.instance} (Error when run selenium). \n"
                + traceback.format_exc()
            )

    def send_request_to_API(
        self,
        url="",
        data={},
        is_multipart=False,
        protocol="GET",
        input_headers={},
        verify=True,
        type="json",
    ):
        # get random user agent
        user_agent = random.choice(self.user_agent_list)

        headers = {"User-Agent": user_agent, **input_headers}

        if is_multipart:
            headers["Content-Type"] = data.content_type

        try:
            if protocol == "POST":
                result = requests.post(url, data=data, headers=headers, verify=verify)
            else:
                result = requests.get(url, headers=headers, verify=verify)

            if result.status_code == 200:
                if type == "json":
                    return result.json()
                return result.text
            else:
                raise Exception(
                    f"Error when use requests: Can not get data in this web. Status code: {result.status_code}, message: {result.text}"
                )
        except requests.ConnectionError:
            raise Exception(f"Error when use requests: Connection error")
