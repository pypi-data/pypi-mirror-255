class BaseDatabaseConnector:

    def __init__(self, connection_string):
        self.database = None
        self.connection = self.get_connection(connection_string=connection_string)

    def close(self):
        pass

    @staticmethod
    def get_connection(**kwargs):
        pass

    def get(self, key, obj_type, **kwargs):
        pass

    def get_list(self, criteria, obj_type, **kwargs):
        pass

    def insert(self, obj, obj_type, **kwargs):
        pass

    def update(self, criteria, new_obj, obj_type, **kwargs):
        pass
