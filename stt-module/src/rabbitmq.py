import pika
from typing import Callable
import logging
from functools import partial

class RabbitMQConsumer:
    def __init__(self, host: str, queue_name: str, port: int, username: str, password: str, max_retries: int = 3):
        self.host = host
        self.queue_name = queue_name
        self.port = port
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.logger.info(f"Connecting to RabbitMQ following info - Host: {self.host}, Queue: {self.queue_name}")
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port, credentials=pika.PlainCredentials(self.username, self.password))
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.logger.info(f"Connected to RabbitMQ on {self.host}")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def process_message(self, callback_func: Callable, ch, method, properties, body):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                callback_func(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            except Exception as e:
                retry_count += 1
                self.logger.warning(
                    f"Processing failed (attempt {retry_count}/{self.max_retries}): {str(e)}"
                )
                if retry_count >= self.max_retries:
                    self.logger.error(f"Message processing failed after {self.max_retries} attempts, acknowledging and skipping message")
                    ch.basic_ack(delivery_tag=method.delivery_tag)  
                    return

    def start_consuming(self, callback_func: Callable):
        if not self.connection or self.connection.is_closed:
            self.connect()

        callback_with_retry = partial(self.process_message, callback_func)
        self.channel.basic_qos(prefetch_count=1)
        
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback_with_retry
        )

        try:
            self.logger.info(f"Started consuming from queue: {self.queue_name}")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()