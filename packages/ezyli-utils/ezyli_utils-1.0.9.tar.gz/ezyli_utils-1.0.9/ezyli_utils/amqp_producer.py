import pika
import time


class AMQPProducer:
    def __init__(self, amqp_url):
        self.params = pika.URLParameters(amqp_url)
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect, retrying...")
            self.reconnect()

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def reconnect(self):
        self.close_connection()
        time.sleep(5)  # Wait before trying to reconnect
        self.connect()

    def publish(
        self,
        queue,
        message,
        content_type="application/json",
    ):
        try:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type=content_type,
                ),  # delivery_mode=2 make message persistent
            )
        except (
            pika.exceptions.AMQPConnectionError,
            pika.exceptions.ChannelClosed,
        ) as e:
            print("Connection was closed, retrying...")
            self.reconnect()
            self.publish(queue, message)

    def publish_with_fixed_retries(
        self,
        queue,
        message,
        content_type="application/json",
        max_retries=5,
    ):
        for i in range(max_retries):
            try:
                self.channel.queue_declare(queue=queue, durable=True)
                self.channel.basic_publish(
                    exchange="",
                    routing_key=queue,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type=content_type,
                    ),  # make message persistent
                )
                break  # If the operation is successful, break the loop
            except (
                pika.exceptions.AMQPConnectionError,
                pika.exceptions.ChannelClosed,
            ) as e:
                print("Connection was closed, retrying...")
                self.reconnect()
                time.sleep(5)  # Wait before retrying
            except Exception as e:
                print(f"An error occurred when trying to publish a message: {e}")
                if i == max_retries - 1:  # If this was the last retry
                    raise  # Re-raise the last exception
                time.sleep(5)  # Wait before retrying


# from celery import shared_task
# producer = RabbitMQProducer()
# @shared_task
# def publish_message(queue, message):
#     producer.publish(queue, message)

# view
# producer = RabbitMQProducer(amqp_url=settings.AMQP_URL)
# producer.publish(
#     queue="my_queue",
#     message="my_message",
#     content_type="save_response_content_type",
# )
