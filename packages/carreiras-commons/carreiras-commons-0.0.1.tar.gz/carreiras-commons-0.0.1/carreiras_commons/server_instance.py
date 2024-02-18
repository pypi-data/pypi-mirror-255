from flask import Flask
from flask_restx import Api
from os import getenv
from gevent.pywsgi import WSGIServer
import config

class ServerInstance():
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app
                       ,version='1.0'
                       , title='Best Frame'
                       , description='Carreiras commons')
        
    def debug(self):
        self.app.run(
            debug=config.DEBUG
        )
    
    def production(self):
        http_server = WSGIServer(('0.0.0.0',config.PORT),self.app)
        http_server.serve_forever()

    def run(self):
        if not config.DEBUG:
            self.debug()
            return
        self.production()

server = ServerInstance()