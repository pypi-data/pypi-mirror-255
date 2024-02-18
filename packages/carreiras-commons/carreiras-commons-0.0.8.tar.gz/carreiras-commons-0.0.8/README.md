# Introdução 
Carreiras API

# Instalando ambiente venv
1. Install Python 3
2. Create virtual env (python3 -m venv .venv)
3. Activate virtual env (. ./.venv/bin/activate)
4. Install dependencies (pip install -U pip --no-cache && pip install -r requirements.txt)

# Env
1. RABBITMQ_HOST =  'localhost 
2. RABBITMQ_PORT = 5672
3. RABBITMQ_EXCHANGE = ''
4. RABBITMQ_ROUTING_KEY =  'email'
5. RABBITMQ_QUEUE = 'email'

# Package Library

1. Compile: python setup.py sdist
2. pip install twine
3. Upload: twine upload dist/* -r pypi