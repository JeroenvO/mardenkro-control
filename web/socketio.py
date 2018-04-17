from flask_socketio import SocketIO
from os import environ

from flask import render_template, Flask

HOST = '127.0.0.1'
try:
    PORT = int(environ.get('SERVER_PORT', '5555'))
except ValueError:
    PORT = 5555
app = Flask(__name__)
app.config['SERVER_NAME'] = "{}:{}".format(HOST, PORT)
socketio = SocketIO(app)