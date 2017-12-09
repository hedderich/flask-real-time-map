from flask import Flask
from flask_socketio import SocketIO

async_mode = None

app = Flask(__name__)
app.config.from_envvar('LIVEMAP_SETTINGS')
socketio = SocketIO(app)

import real_time_map.views
