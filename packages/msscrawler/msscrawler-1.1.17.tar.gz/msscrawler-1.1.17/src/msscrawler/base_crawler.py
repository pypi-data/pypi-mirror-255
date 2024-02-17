import logging
import os

from dotenv import load_dotenv

from .mixins.database_mixin import DatabaseMixin
from .mixins.message_connector_mixin import MessageConnectorMixin


class BaseCrawler(DatabaseMixin, MessageConnectorMixin):

    def __init__(self):
        DatabaseMixin.__init__(self)
        MessageConnectorMixin.__init__(self)

        self.logger = self.get_logger()

    def get_logger(self):
        return logging.getLogger(self.__str__())

    def run(self):
        pass