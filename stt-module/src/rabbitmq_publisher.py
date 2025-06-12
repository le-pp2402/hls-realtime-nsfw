import pika
import logging
from typing import Any

class RabbitMQPublisher:
    def __init__(self, host: str, queue_name: str, port: int, username: str, password: str):
        self.host = host
        self.queue_name = queue_name
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.logger.info(f"Connecting to RabbitMQ following info - Host: {self.host}, Queue: {self.queue_name}")
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host, 
                    port=self.port, 
                    credentials=pika.PlainCredentials(self.username, self.password)
                )
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.logger.info(f"Connected to RabbitMQ on {self.host}")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def publish(self, message: Any):
        if not self.connection or self.connection.is_closed:
            self.connect()
            
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            self.logger.info(f"Published message to queue: {self.queue_name}")
        except Exception as e:
            self.logger.error(f"Failed to publish message: {str(e)}")
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.logger.info("Closed RabbitMQ connection")
