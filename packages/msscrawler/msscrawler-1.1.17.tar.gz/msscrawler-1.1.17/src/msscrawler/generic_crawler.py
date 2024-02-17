import json
import os
import sys
import random
import traceback
from datetime import datetime, timedelta
from pymongo import read_concern, write_concern

import asyncio
import psutil
from bson import ObjectId

from .base_crawler import BaseCrawler
from .connectors.databases.mongodb_connector import MongoDBConnector
from .connectors.message_brokers.rabbitmq_connector import RabbitMQConnector
from .log.default import get_default_log
from .mixins.spider_cache_mixin import SpiderCacheMixin


class GenericCrawler(BaseCrawler, SpiderCacheMixin):
    def __init__(self, name, coll_env_name):
        self.name = name
        self.coll_env_name = coll_env_name
        self.data_coll = None

        self.receive_queue = None
        self.transmit_queue = None

        self.website_coll = None
        self.categories_coll = None
        self.products_coll = None
        self.logger = None

        super().__init__()
        SpiderCacheMixin.__init__(self)

        self.user = os.getenv("USER")
        self.retry_time_limit = os.getenv("RETRY_TIME_LIMIT")

        # use phys_cpu
        # total_sub = psutil.cpu_count(logical=False) - 2
        self.total_sub_process = int(os.getenv("TOTAL_SUB_PROCESS"))

    def setup_database(self, reinit=False):
        super().setup_database(reinit=reinit)
        self.data_coll = self.database[f"{os.getenv(self.coll_env_name)}"]

    def init_database_connector(self):
        self.database_client = MongoDBConnector(
            connection_string=self.database_params["conn_string"],
            default_database=self.database_params["database"],
        )
        self.database = self.database_client.connection[
            self.database_params["database"]
        ]

    def load_connector_env(self):
        super().load_connector_env()
        self.receive_queue = os.getenv("RECEIVE_QUEUE")
        self.connector_params["receive_queue"] = self.receive_queue
        self.transmit_queue = os.getenv("TRANSMIT_QUEUE")
        self.connector_params["transmit_queue"] = self.transmit_queue

    def init_message_connector(self):
        self.connector_client = RabbitMQConnector(
            queue_declare=os.getenv("RECEIVE_QUEUE")
        )

    def get_logger(self):
        if not self.logger:
            self.logger = get_default_log(self.name)

        return self.logger

    def run(self):
        self.get_logger().info(f" [*] {self.name} instance: waiting for messages")
        self.receive_message(self.receive_queue, self.receive_message_callback)

    def receive_message_callback(self, ch, method, properties, body):
        # self.get_logger().info(
        #     f"[*] Receive message in {self.name}_queue: (message: {body.decode()})"
        # )

        rc_snapshot = read_concern.ReadConcern("snapshot")
        wc_majority = write_concern.WriteConcern("majority")

        body_message = None
        try:
            body_message = json.loads(body.decode())

            if not self.choose_spider(body_message["spider_name"]):
                return self.connector_client.send_processed_message_status(
                    is_processed=False, delivery_tag=method.delivery_tag
                )

            if self.name == "product":
                query_obj = {
                    "url": body_message["url"],
                    "category_id": ObjectId(body_message["category_id"]),
                }
            else:
                query_obj = {"url": body_message["url"]}

            record = self.data_coll.find_one(query_obj)

            # ! check last crawl (not crawl document has last crawl > previous time range in env)
            # prevent continuos pagination categories
            if self.check_crawled_in_previous_time(record):
                return self.connector_client.send_processed_message_status(
                    is_processed=True, delivery_tag=method.delivery_tag
                )

            # ! check if status in-active and re process > retry time => omit (return ack)
            if self.check_process_retry_time(record):
                return self.connector_client.send_processed_message_status(
                    is_processed=True, delivery_tag=method.delivery_tag
                )

            #! check if status error and re crawl > retry time => omit (return ack)
            if self.check_error_retry_time(record):
                return self.connector_client.send_processed_message_status(
                    is_processed=True, delivery_tag=method.delivery_tag
                )

            if not record:
                return self.connector_client.send_processed_message_status(
                    is_processed=False, delivery_tag=method.delivery_tag
                )

            # limit subprocess
            child_process = psutil.Process()
            # print("total subprocess", len(child_process.children()))
            if len(child_process.children()) >= self.total_sub_process:
                return self.connector_client.send_processed_message_status(
                    is_processed=False, delivery_tag=method.delivery_tag
                )

            self.data_coll.update_one(
                {"_id": record["_id"]},
                {
                    "$set": {
                        "err_re_process": record["err_re_process"] + 1,
                    },
                },
            )

            # with self.database_client.connection.start_session(
            #     {"causalConsistency": False}
            # ) as session:
            #     session.with_transaction(
            #         lambda s: self.update_one_data_callback(
            #             s,
            #             query_obj,
            #             {
            #                 "err_re_process": record["err_re_process"] + 1,
            #             },
            #         ),
            #         read_concern=rc_snapshot,
            #         write_concern=wc_majority,
            #     )

            asyncio.run(self.run_subprocess(record))

            # add count for spider
            self.increase_spider_count(record["spider_name"])

            self.connector_client.send_processed_message_status(
                is_processed=True, delivery_tag=method.delivery_tag
            )
        except Exception as error:
            if self.database_client.connection:
                self.database_client.close()

            # traceback.print_exc()
            # + log to log server
            self.get_logger().error(
                f"[x] Error when process message from {self.name}_queue (message: {body_message}). \n"
                + traceback.format_exc()
            )
            sys.exit()

    def check_crawled_in_previous_time(self, record):
        return (
            record
            and record["status"] == "active"
            and (
                record["last_crawl"]
                > datetime.now() - timedelta(hours=int(os.getenv("PREV_TIME")))
            )
        )

    def check_process_retry_time(self, record):
        return (
            record
            and record["status"] == "in-active"
            and record["err_re_process"] > int(os.getenv("RETRY_TIME_LIMIT"))
        )

    def check_error_retry_time(self, record):
        return (
            record
            and record["status"] == "error"
            and record["err_re_crawl"] > int(os.getenv("RETRY_TIME_LIMIT"))
        )

    async def run_subprocess(self, crawl_record):
        delay_time = crawl_record["random_sleep"]
        # print(f"Delay time {delay_time}")
        # await asyncio.sleep(delay_time)

        command = self.get_spider_command(crawl_record)
        # print("subprocess", f"sleep {delay_time} && " + command.replace("&", "\&"))
        # process = Popen(
        #     command.replace("&", "\&"), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE
        # )

        process = await asyncio.create_subprocess_shell(
            cmd=f"sleep {delay_time} && " + command.replace("&", "\&")
        )

        self.get_logger().info(
            f"[*] Sub process created: "
            + f"sleep {delay_time} && "
            + command.replace("&", "\&")
        )

    def get_spider_command(self, crawl_record):
        raise NotImplemented()

    def build_update_object(self, body_message):
        return {}

    def build_insert_object(self, body_message):
        update_obj = self.build_update_object(body_message)
        update_obj["err_re_crawl"] = 0
        update_obj["err_re_process"] = 0

        return update_obj

    def update_one_data_callback(self, session, query, update_obj):
        self.data_coll.update_one(
            query,
            {
                "$set": update_obj,
            },
            session=session,
        )
