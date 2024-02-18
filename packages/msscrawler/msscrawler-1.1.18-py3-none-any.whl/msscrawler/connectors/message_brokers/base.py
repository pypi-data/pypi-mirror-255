class BaseMessageBrokerConnector:
    def __init__(self, **kwargs):
        pass

    def send(self, message, target, **kwargs):
        pass

    def receive(self, receive_from, received_callback, **kwargs):
        pass

    def close(self):
        pass

    def send_processed_message_status(self, is_processed=True, **kwargs):
        pass