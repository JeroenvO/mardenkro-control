"""
This script runs the Launcher application using a development server.
"""

import eventlet.wsgi

# HOST = '127.0.0.1'
# try:
#     PORT = int(environ.get('SERVER_PORT', '5555'))
# except ValueError:
#     PORT = 5555
# app = Flask(__name__)
# app.config['SERVER_NAME'] = "{}:{}".format(HOST, PORT)
# socketio = SocketIO(app)

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
    # socketio.run(app, debug=False, host='0.0.0.0')
