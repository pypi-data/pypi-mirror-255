import pika
import json
from carreiras_commons import config

class RabbitMQManagerEmail:
    def __init__(self):
        self.connection_params = pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT
        )
        self.queue_name = config.RABBITMQ_QUEUE_EMAIL
        self.exchange = config.RABBITMQ_EXCHANGE
        self.routing_key = config.RABBITMQ_QUEUE_EMAIL

    def send_json_message(self, data):
        message = json.dumps(data)
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_name)

        channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=message
        )

        print(f" [x] Enviado: {message}")
        connection.close()


rabbitmq_manager_email = RabbitMQManagerEmail()
