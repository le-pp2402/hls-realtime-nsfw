import os
import logging
import json
from transformers import pipeline
from .rabbitmq_consummer import RabbitMQConsumer
from .rabbitmq_publisher import RabbitMQPublisher
from .config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def nsfw_classification(text: str, classifier):
    """
    Performs NSFW classification on the given text using a HuggingFace classifier.

    Args:
        text (str): The input text to classify.
        classifier: HuggingFace pipeline for classification.

    Returns:
        dict: The classification result.
    """
    try:
        result = classifier(text)
        logging.debug(f"Classification result: {result}")
        label = result[0]['label']
        
        fixed_width = 100  
        formatted_text = text.ljust(fixed_width)
        
        if label == 'nsfw':
            logging.info(f"\033[91m{formatted_text}{label:>10}\033[0m")  
        else:
            logging.info(f"\033[92m{formatted_text}{label:>10}\033[0m")  
    except Exception as e:
        logging.error(f"Error during classification: {e}")


def message_handler(body, classifier):
    """
    Processes the message from RabbitMQ.

    Args:
        body (bytes): The message body.
        classifier: The NSFW classification pipeline.
    """
    try:
        message_text = body.decode('utf-8')
        nsfw_classification(message_text, classifier)
    except Exception as e:
        logging.error(f"Failed to handle message: {e}")


def main():
    logging.info("Starting NSFW classifier service...")

    try:
        classifier_pipeline = pipeline("text-classification", model="eliasalbouzidi/distilbert-nsfw-text-classifier")
    except Exception as e:
        logging.critical(f"Failed to initialize classifier pipeline. Exiting. Error: {e}")
        return

    consumer = RabbitMQConsumer(
        host=RABBITMQ_HOST,
        queue_name=RABBITMQ_QUEUE,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD
    )
    consumer.connect()
    logging.info("Connected to RabbitMQ. Waiting for messages...")

    consumer.start_consuming(
        callback_func=lambda body: message_handler(body, classifier_pipeline)
    )


if __name__ == "__main__":
    main()
