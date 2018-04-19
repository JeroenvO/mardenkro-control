from old_flask.webserver import socketio, app

if __name__ == "__main__":
    socketio.run(app, debug=True)