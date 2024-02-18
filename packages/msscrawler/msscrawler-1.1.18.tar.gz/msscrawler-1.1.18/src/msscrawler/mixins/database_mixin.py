import os

from ..connectors.databases.base import BaseDatabaseConnector

class DatabaseMixin:

    def __init__(self):
        super().__init__()
        self.database_params = {}
        self.database_client = None
        self.database = None
        self.setup_database()

    def load_database_env(self):
        self.database_params['conn_string'] = os.getenv("CONNECTION_STRING")
        self.database_params['database'] = os.getenv("DATABASE")

    def setup_database(self, reinit=False):
        self.load_database_env()
        if not self.database_client or reinit:
            self.init_database_connector()

    def init_database_connector(self):
        self.database_client = BaseDatabaseConnector(connection_string=self.database_params['conn_string'])


    def insert(self, obj, obj_type, **kwargs):
        return self.database_client.insert(obj)

    def update(self, key, new_obj, obj_type, **kwargs):
        return self.database_client.update(key, new_obj)

    def get(self, key, obj_type, **kwargs):
        return self.database_client.get(key)
