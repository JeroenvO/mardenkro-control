"""
Routes and views for the flask application.
"""
from flask import render_template, Flask
import socketio
from old_flask.controlserver import ControlThread

# controller socket.
c = None

sio = socketio.Server(async_mode='eventlet')
app = Flask(__name__)

@sio.on('update', namespace='/control')
def message(sid, data):
    print('recv: '+data)
    global c
    if data =='start':
        if not c:
            c = ControlThread(sio)
            c.start()
            sio.emit('update', 'Started thread', namespace='/control')
        else:
            sio.emit('update', 'Already started', namespace='/control')
    elif data == 'stop':
        if c:
            sio.emit('update', 'Stopping thread', namespace='/control')
            c.stop()
            # c.join()
            c=None
            sio.emit('update', 'Stopped thread', namespace='/control')
        else:
            sio.emit('update', 'No thread', namespace='/control')

@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html', title='Home')

@app.route('/control/')
def control():
    return render_template('control.html', title='Manual control')

@app.route('/line/')
def line():
    return render_template('line.html', title='Line viewer')

