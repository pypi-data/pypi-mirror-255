import pika
import time
from .validator import validate_data
from .schemas import COMMON_SCHEMA
from pika.exceptions import ChannelClosed, AMQPConnectionError


class AMQPManager:
    def __init__(self, amqp_url):
        self.params = pika.URLParameters(amqp_url)
        self.connection = None
        self.channel = None
        self.connect_counter = 0

    def connect(self):
        while True:
            self.connect_counter += 1
            try:
                self.close_connection()
                self.connection = pika.BlockingConnection(self.params)
                self.channel = self.connection.channel()
                # Reset the counter if the connection is successful
                self.connect_counter = 0
                break  # If the connection is successful, break the loop
            except pika.exceptions.AMQPConnectionError:
                print("Failed to connect, retrying...")
                time.sleep(5) if self.connect_counter > 1 else time.sleep(0)

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"An error occurred when trying to close the connection: {e}")

    def reconnect(self):
        self.connect()

    def publish(
        self,
        queue,
        message,
        durability,
        content_type="application/json",
    ):
        while True:
            try:
                self.channel.queue_declare(queue=queue, durable=durability)
                self.channel.basic_publish(
                    exchange="",
                    routing_key=queue,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type=content_type,
                    ),  # delivery_mode=2 make message persistent
                )
                break  # If the operation is successful, break the loop
            except (AMQPConnectionError, ChannelClosed) as e:
                print("Connection was closed, retrying...")
                self.reconnect()

    def publish_with_fixed_retries(
        self,
        queue,
        message,
        durability,
        content_type="application/json",
        max_retries=5,
    ):
        for i in range(max_retries):
            try:
                self.channel.queue_declare(queue=queue, durable=durability)
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

    def validate_data(self, data, schema):
        return validate_data(data, schema)

    def _is_valid_body(self, body):
        # Convert body from bytes to string and then to a dictionary
        try:
            content = json.loads(body.decode())
        except json.JSONDecodeError:
            print(f"Invalid JSON received :: {body.decode()}")
            return False
        schema = COMMON_SCHEMA
        return self.validate_data(content, schema)

    def consume(self, queue_name, durability, callback):
        def internal_callback(ch, method, properties, body):
            if self._is_valid_body(body):
                callback(ch, method, properties, body)

        while True:
            print("Setting up consumer 2:- ...")
            try:
                self.channel.queue_declare(queue=queue_name, durable=durability)
                self.channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=internal_callback,
                    auto_ack=True,
                )

                print("Started Consuming")

                self.channel.start_consuming()
            except (
                pika.exceptions.ChannelClosed,
                pika.exceptions.AMQPConnectionError,
            ) as e:
                print("Reconnecting ...")
                self.reconnect()
            except Exception as e:
                print("Reconnecting ...")
                print(e)
                self.reconnect()
