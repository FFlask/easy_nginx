import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from bbs import db,create_app
from  geventwebsocket.websocket import WebSocket,WebSocketError
from  geventwebsocket.handler import WebSocketHandler
from  gevent.pywsgi import WSGIServer


app = create_app()

migrate = Migrate(app,db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    #manager.run()
    http_serve=WSGIServer(("0.0.0.0",5000),app,handler_class=WebSocketHandler)
    http_serve.serve_forever()

