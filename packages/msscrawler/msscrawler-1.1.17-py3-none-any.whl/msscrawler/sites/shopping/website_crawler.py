import logging
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from pymongo import read_concern, write_concern

import graypy
from crontab import CronTab

from ...base_crawler import BaseCrawler
from ...connectors.databases.mongodb_connector import MongoDBConnector
from ...log.default import get_default_log


class WebsiteCrawler(BaseCrawler):
    def __init__(self):
        self.receive_queue = None
        self.transmit_queue = None

        self.website_coll = None
        self.categories_coll = None
        self.logger = None

        super().__init__()

        self.cron_cmd_template = os.getenv("CRON_CMD_TEMPLATE")
        self.user = os.getenv("USER")
        self.loop_time = int(os.getenv("LOOP_TIME"))
        self.retry_time_limit = os.getenv("RETRY_TIME_LIMIT")

    def setup_database(self, reinit=False):
        super().setup_database()
        self.website_coll = self.database[f'{os.getenv("WEBSITE_COLL")}']
        self.categories_coll = self.database[f'{os.getenv("CATEGORIES_COLL")}']

    def load_database_env(self):
        super().load_database_env()

    # def load_connector_env(self):
    #     super().load_connector_env()
    #     self.receive_queue = os.getenv("RECEIVE_QUEUE")
    #     self.transmit_queue = os.getenv("TRANSMIT_QUEUE")

    def init_database_connector(self):
        self.database_client = MongoDBConnector(
            connection_string=self.database_params["conn_string"],
            default_database=self.database_params["database"],
        )
        self.database = self.database_client.connection[
            self.database_params["database"]
        ]

    def get_logger(self):
        if not self.logger:
            self.logger = get_default_log()

        return self.logger

    def run(self):
        super().run()
        first_time = True

        next_time = datetime.now() + timedelta(seconds=self.loop_time)

        while True:
            if first_time:
                self.logger.info("[*] Website instance: Init first time")

                self.remove_all_job()

                self.logger.info("[*] Website instance: Remove all prev job")

                self.init_schedule()

                first_time = False
            else:
                date_time_now = datetime.now()

                if date_time_now >= next_time:
                    self.init_schedule()
                    next_time = date_time_now + timedelta(seconds=self.loop_time)
                else:
                    # put process to sleep for remained time to prevent continuous loop
                    remained_time = next_time - date_time_now
                    if remained_time.seconds > 0:
                        time.sleep((remained_time + timedelta(seconds=5)).seconds)

    def remove_all_job(self):
        cron = CronTab(user=self.user)
        cron.remove_all()
        cron.write()

    def init_schedule(self):
        connection = None
        rc_snapshot = read_concern.ReadConcern("snapshot")
        wc_majority = write_concern.WriteConcern("majority")
        try:
            self.init_database_connector()
            connection = self.database_client.connection

            cron = CronTab(user=self.user)

            collection = self.website_coll

            for website in collection.find():
                found = False
                for job in cron:
                    if job.comment == website["spider_name"]:
                        found = True

                        # ! check status still in-active (error when spider not run) if err_re_process > 2 time => omit
                        if website["status"] == "in-active":
                            if website["err_re_process"] > int(self.retry_time_limit):
                                self.get_logger().info(
                                    f"[*] Remove cronjob of {website['spider_name']}: exceed retry time when process job"
                                )
                                cron.remove(job)
                                cron.write()
                                return
                            # update err_re_process
                            # with connection.start_session(
                            #     {"causalConsistency": False}
                            # ) as session:
                            #     session.with_transaction(
                            #         lambda s: self.update_website_callback(
                            #             s,
                            #             website["url"],
                            #             {
                            #                 "err_re_process": website["err_re_process"]
                            #                 + 1
                            #             },
                            #         ),
                            #         read_concern=rc_snapshot,
                            #         write_concern=wc_majority,
                            #     )

                            self.website_coll.update_one(
                                {"url": website["url"]},
                                {
                                    "$set": {
                                        "err_re_process": website["err_re_process"] + 1
                                    },
                                },
                            )

                        # ! check status if error and error > 2 time => kill process
                        if website["status"] == "error" and website[
                            "err_re_crawl"
                        ] > int(self.retry_time_limit):
                            self.get_logger().info(
                                f"[*] Remove cronjob of {website['spider_name']}: exceed retry time when crawl website"
                            )
                            cron.remove(job)
                            cron.write()
                            return

                        # check if modified schedule
                        if (
                            job.slices.render() != "* * * * *"
                            and job.slices.render() != website["schedule"]
                        ) or (
                            job.slices.render() == "* * * * *"
                            and website["schedule"].replace("/1", "")
                            != job.slices.render()
                        ):
                            current_schedule = job.slices.render()
                            self.get_logger().info(
                                f"[*] Change schedule time for {website['spider_name']}: from {current_schedule} to {website['schedule']}"
                            )
                            job.setall(website["schedule"])
                            cron.write()

                if not found:
                    # ! check status in-active if err_re_process > 2 time => omit
                    if website["status"] == "in-active":
                        if website["err_re_process"] > int(self.retry_time_limit):
                            return
                        # update err_re_process
                        # with connection.start_session(
                        #     {"causalConsistency": False}
                        # ) as session:
                        #     session.with_transaction(
                        #         lambda s: self.update_website_callback(
                        #             s,
                        #             website["url"],
                        #             {"err_re_process": website["err_re_process"] + 1},
                        #         ),
                        #         read_concern=rc_snapshot,
                        #         write_concern=wc_majority,
                        #     )

                        self.website_coll.update_one(
                            {"url": website["url"]},
                            {
                                "$set": {
                                    "err_re_process": website["err_re_process"] + 1
                                },
                            },
                        )

                    # ! check status error if error > 2 time => omit
                    if website["status"] == "error" and website["err_re_crawl"] > int(
                        self.retry_time_limit
                    ):
                        return

                    # start new cronjob

                    # create new cron job based on template
                    job = cron.new(
                        command=self.cron_cmd_template.format(
                            website["spider_name"], website["url"]
                        ),
                        comment=website["spider_name"],
                    )

                    job.setall(website["schedule"])
                    cron.write()

                    self.get_logger().info(
                        f"[*] Init new job for {website['spider_name']}"
                    )

            connection.close()
        except Exception as error:
            if connection:
                connection.close()

            # traceback.print_exc()
            # + log to log server
            self.get_logger().error(
                f"[x] Error when process cronjob of website. \n"
                + traceback.format_exc()
            )
            sys.exit()

    def update_website_callback(self, session, url, update_obj):
        self.website_coll.update_one(
            {"url": url},
            {
                "$set": update_obj,
            },
            session=session,
        )
