"""
This script runs the Launcher application using a development server.
"""

from web.views import *

if __name__ == '__main__':
    socketio.run(app, debug=True)