
from os import getenv

RABBITMQ_HOST = getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = getenv('RABBITMQ_PORT', 5672)
RABBITMQ_EXCHANGE = getenv('RABBITMQ_EXCHANGE', '')
RABBITMQ_ROUTING_KEY =  getenv('RABBITMQ_ROUTING_KEY', 'email')
RABBITMQ_QUEUE = getenv('RABBITMQ_QUEUE', 'email')
DEBUG = getenv('DEBUG',True)
PORT = getenv('PORT',8080)