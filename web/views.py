"""
Routes and views for the flask application.
"""
from web.socketio import *
from flask import render_template, abort, url_for, redirect, Flask

from controlserver import ControlThread

# controller socket.
c = None


@app.route('/start/')
def agentstartall():
    global c
    if not c:
        c = ControlThread(socketio)
        c.start()
        socketio.emit('update', 'Started thread', namespace='/control')

    else:
        socketio.emit('update', 'Already started', namespace='/control')
    return redirect(url_for('home'))

@app.route('/stop/')
def agentstopall():
    global c
    if c:
        c.stop()
        socketio.emit('update', 'Stopped thread', namespace='/control')
    else:
        socketio.emit('update', 'No thread', namespace='/control')
    return redirect(url_for('home'))

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

