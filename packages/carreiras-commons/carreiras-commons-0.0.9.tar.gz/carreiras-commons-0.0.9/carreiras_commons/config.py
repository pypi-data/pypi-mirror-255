from os import getenv
import urllib.parse

RABBITMQ_HOST = getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = getenv('RABBITMQ_PORT', '5672')
RABBITMQ_EXCHANGE = getenv('RABBITMQ_EXCHANGE', '')
RABBITMQ_QUEUE_EMAIL = getenv('RABBITMQ_QUEUE', 'email')
RABBITMQ_QUEUE_NOTIFICACAO = getenv('RABBITMQ_QUEUE', 'notificacoes')
RABBITMQ_QUEUE_NOTIFICACAO_ADMIN = getenv('RABBITMQ_QUEUE', 'notificacoes_admin')

SMTP_SERVER =  getenv('SMTP_SERVER', "smtp.gmail.com")
SMTP_PORT = getenv('SMTP_PORT', 587)
SMTP_USUERNAME = getenv('SMTP_USUERNAME', "teste@gmail.com") 
SMTP_PASSWORD = getenv('SMTP_PASSWORD', "123") 
SENDER_EMAIL = getenv('SENDER_EMAIL', "teste@gmail.com")  

DEBUG = getenv('DEBUG',True)
PORT = getenv('PORT',9090)

DATABASE_PASSAOWRD = urllib.parse.quote_plus( getenv('DATABASE_PASSAOWRD', "123"))
DATABASE_USER = getenv('DATABASE_USER', 'root')
DATABASE_HOST = getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = getenv('DATABASE_PORT', '5432')
DATABASE_NAME = getenv('DATABASE_NAME', 'bd')
SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USER}:{DATABASE_PASSAOWRD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False