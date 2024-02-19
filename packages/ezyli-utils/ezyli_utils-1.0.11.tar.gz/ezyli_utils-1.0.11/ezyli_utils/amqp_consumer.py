import json
import time
import pika
from pika.exceptions import ChannelClosed, AMQPConnectionError
from .validator import validate_data
from .schemas import COMMON_SCHEMA


class AMQPConsumer:
    def __init__(self, amqp_url, callback):
        self.amqp_url = amqp_url
        self.callback = callback
        self.params = pika.URLParameters(self.amqp_url)

    def validate_data(self, data, schema):
        return validate_data(data, schema)

    def internal_callback(self, ch, method, properties, body):
        # Convert body from bytes to string and then to a dictionary
        try:
            content = json.loads(body.decode())
        except json.JSONDecodeError:
            print(f"Invalid JSON received :: {body.decode()}")
            return

        # Define your schema here
        schema = COMMON_SCHEMA
        if self.validate_data(content, schema):
            self.callback(ch, method, properties, body)

    def consume(self, queue_name, durability):
        while True:
            print("Setting up consumer 1:- ...")
            try:
                connection = pika.BlockingConnection(self.params)
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=durability)
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=self.internal_callback,
                    auto_ack=True,
                )

                print("Started Consuming")

                channel.start_consuming()
            except (ChannelClosed, AMQPConnectionError) as e:
                print("Reconnecting ...")
                try:
                    channel.close()
                    connection.close()
                except:
                    pass
                time.sleep(5)
            except Exception as e:
                print("Reconnecting ...")
                print(e)
                pass
