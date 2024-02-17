import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from common_packages.message_queue_utils.interface import MessageQueue


class RabbitmqQueue(MessageQueue):
    def __init__(self, queue_name: str, host: str, port: str, **kwargs) -> None:
        if not {"username", "password"}.issubset(kwargs.keys()):
            raise ValueError("username and password must be provided")
        self.queue_name = queue_name
        credentials = pika.PlainCredentials(kwargs["username"], kwargs["password"])
        try:
            self.connect = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, port=port, credentials=credentials)
            )
        except Exception as e:
            raise ConnectionError(f"connect rabbitmq failed, {e}")
        try:
            self.channel = self.connect.channel()
        except Exception as e:
            raise ConnectionError(f"create channel failed, {e}")
        try:
            self.channel.queue_declare(queue=self.queue_name)
        except Exception as e:
            raise ConnectionError(f"create queue failed, {e}")

    def enqueue(self, item: bytes) -> None:
        self.channel.basic_publish(exchange="", routing_key=self.queue_name, body=item)

    def message_callback(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        logging.info(f"consumer handle ok: {body.decode()}")

    def consumer(self, welcome_message) -> None:
        self.channel.basic_consume(
            queue=self.queue_name,
            auto_ack=True,
            on_message_callback=self.message_callback,
        )
        logging.info(f"consumer start success \n {welcome_message}")
        self.channel.start_consuming()
