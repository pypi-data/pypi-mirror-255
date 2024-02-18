from ..connectors.message_brokers.base import BaseMessageBrokerConnector


class MessageConnectorMixin:

    def __init__(self):
        super().__init__()
        self.connector_params = {}
        self.connector_client = None
        self.setup_connector()

    def load_connector_env(self):
        pass

    def setup_connector(self, reinit=False):
        self.load_connector_env()
        if not self.connector_client or reinit:
            self.init_message_connector()

    def init_message_connector(self):
        self.connector_client = BaseMessageBrokerConnector()


    def send_message(self, message="", target=None):
        self.connector_client.send(message, target)

    def receive_message(self, receive_from, received_callback):
        self.connector_client.receive(receive_from, received_callback)