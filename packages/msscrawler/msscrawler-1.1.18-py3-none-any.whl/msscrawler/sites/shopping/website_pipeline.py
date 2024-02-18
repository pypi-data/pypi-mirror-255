import os
import traceback

from pymongo import ReturnDocument, read_concern, write_concern

from ...pipelines.base import BasePipeline
from ...connectors.databases.mongodb_connector import MongoDBConnector
from ...connectors.message_brokers.rabbitmq_connector import RabbitMQConnector


class WebsitePipeline(BasePipeline):
    def __init__(self):
        self.receive_queue = None
        self.transmit_queue = None

        self.website_coll = None
        self.categories_coll = None

        super().__init__()

    def load_database_env(self):
        super().load_database_env()

    def setup_database(self, reinit=False):
        super().setup_database()
        self.website_coll = self.database[f'{os.getenv("WEBSITE_COLL")}']
        self.categories_coll = self.database[f'{os.getenv("CATEGORIES_COLL")}']

    def load_connector_env(self):
        super().load_connector_env()
        self.receive_queue = os.getenv("RECEIVE_QUEUE")
        self.connector_params["receive_queue"] = self.receive_queue
        self.transmit_queue = os.getenv("TRANSMIT_QUEUE")
        self.connector_params["transmit_queue"] = self.transmit_queue

    def init_database_connector(self):
        self.database_client = MongoDBConnector(
            connection_string=self.database_params["conn_string"],
            default_database=self.database_params["database"],
        )
        self.database = self.database_client.connection[
            self.database_params["database"]
        ]

    def init_message_connector(self):
        self.connector_client = RabbitMQConnector()

    def process_item(self, item, spider):
        # update status of website_data
        try:
            website = None

            rc_snapshot = read_concern.ReadConcern("snapshot")
            wc_majority = write_concern.WriteConcern("majority")
            # prepare update obj
            update_obj = None

            if item["status"] != "error":
                update_obj = {
                    "name": item["name"],
                    "brand": item["brand"],
                    "status": item["status"],
                    "last_crawl": item["last_crawl"],
                    "css_selector": item["css_selector"],
                    "categories_num": item["categories_num"],
                    "total_categories": item["total_categories"],
                    "err_re_crawl": 0,
                    "err_re_process": 0,  # clear err when cron init
                }
            else:
                website = self.website_coll.find_one({"url": item["url"]})

                update_obj = {
                    "name": item["name"],
                    "brand": item["brand"],
                    "status": item["status"],
                    "last_crawl": item["last_crawl"],
                    "total_categories": item["total_categories"],
                    "err_re_crawl": website["err_re_crawl"] + 1,
                    "err_re_process": 0,  # clear err when cron init
                }

            # with self.database_client.connection.start_session(
            #     {"causalConsistency": False}
            # ) as session:
            #     session.with_transaction(
            #         lambda s: self.update_website_callback(s, item["url"], update_obj),
            #         read_concern=rc_snapshot,
            #         write_concern=wc_majority,
            #     )

            self.website_coll.update_one(
                {"url": website["url"]},
                {
                    "$set": update_obj,
                },
            )

            # send all categories_url to categories_queue
            website = self.website_coll.find_one({"url": item["url"]})

            if website:
                for category in item["category_urls"]:
                    # test rabbit
                    if category != item["category_urls"][0]:
                        continue

                    body_message = {
                        "website_id": str(website["_id"]),
                        "website_url": website["url"],
                        "website_name": website["name"],
                        "url": category,
                        "spider_name": website["spider_name"],
                        "is_root": "True",
                        "root_obj_id": "",
                    }

                    # send message to rabbitmq (categories_queue)
                    self.send_message(
                        body_message, self.connector_params["transmit_queue"]
                    )

            self.get_logger().info(
                f'[*] Crawling website {item["url"]} completed at {item["last_crawl"]}: status - "{item["status"]}"'
            )
        except Exception as error:
            # traceback.print_exc()
            # + log to log server
            self.get_logger().error(
                f'[x] Error when process data crawled in pipeline website (url: {item["url"]}). \n'
                + traceback.format_exc()
            )

        return item

    def close_spider(self, spider):
        # disconnect database
        self.database_client.close()

        # disconnect rabbitmq
        self.connector_client.close()

    def update_website_callback(self, session, url, update_obj):
        self.website_coll.update_one(
            {"url": url},
            {
                "$set": update_obj,
            },
            session=session,
        )
