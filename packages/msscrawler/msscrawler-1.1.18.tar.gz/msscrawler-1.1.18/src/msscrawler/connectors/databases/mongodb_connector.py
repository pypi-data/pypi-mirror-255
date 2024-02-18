import pymongo

from .base import BaseDatabaseConnector

class MongoDBConnector(BaseDatabaseConnector):

    def __init__(self, connection_string, default_database=None):
        super().__init__(connection_string)
        self.database = self.connection[default_database]

    @staticmethod
    def get_connection(**kwargs):
        return pymongo.MongoClient(kwargs['connection_string'])

    def close(self):
        if self.connection:
            self.connection.close()

    def get(self, key, obj_type, **kwargs):
        return self.database[obj_type].find_one(key)

    def get_list(self, criteria, obj_type, **kwargs):
        return self.database[obj_type].find()

    def insert(self, obj, obj_type, **kwargs):
        return self.database[obj_type].insert_one(obj)

    def update(self, criteria, new_obj, obj_type, **kwargs):
        return self.database[obj_type].update_one(
            criteria,
            {
                "$set": new_obj
            }
        )

