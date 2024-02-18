import json
import os
import ssl

import pika

from .base import BaseMessageBrokerConnector


class RabbitMQConnector(BaseMessageBrokerConnector):
    def __init__(self, queue_declare, **kwargs):
        super().__init__(**kwargs)

        # * old version
        # credentials = pika.PlainCredentials(
        #     os.getenv("RABBIT_MQ_USER"), os.getenv("RABBIT_MQ_PASSWORD")
        # )
        # parameters = pika.ConnectionParameters(
        #     os.getenv("RABBIT_MQ_CONN"), 5672, os.getenv("RABBIT_MQ_VHOST"), credentials
        # )

        # *new version
        if os.getenv("RABBIT_MQ_CONN_TYPE") == "PARAMETER":
            credentials = pika.PlainCredentials(
                os.getenv("RABBIT_MQ_USER"), os.getenv("RABBIT_MQ_PASSWORD")
            )
            parameters = pika.ConnectionParameters(
                os.getenv("RABBIT_MQ_CONN"),
                os.getenv("RABBIT_MQ_PORT"),
                os.getenv("RABBIT_MQ_VHOST"),
                credentials,
            )
        elif os.getenv("RABBIT_MQ_CONN_TYPE") == "STRING":
            parameters = pika.URLParameters(os.getenv("RABBIT_MQ_CONN_STRING"))

        if os.getenv("RABBIT_MQ_CONN_SSL") == "ENABLE":
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")
            parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        self.rabbit_mq_conn = pika.BlockingConnection(parameters)

        self.channel = self.rabbit_mq_conn.channel()
        self.channel.queue_declare(queue=queue_declare, durable=True)

    def close(self):
        if self.rabbit_mq_conn:
            self.rabbit_mq_conn.close()

    def send(self, message, target, **kwargs):
        self.channel.basic_publish(
            exchange="",
            routing_key=target,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    def receive(self, receive_from, received_callback, **kwargs):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=receive_from, on_message_callback=received_callback, auto_ack=False
        )

        self.channel.start_consuming()

    def send_processed_message_status(self, is_processed=True, **kwargs):
        if is_processed:
            return self.channel.basic_ack(delivery_tag=kwargs["delivery_tag"])
        else:
            return self.channel.basic_nack(delivery_tag=kwargs["delivery_tag"])
