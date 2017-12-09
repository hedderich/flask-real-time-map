from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

async_mode = None

app = Flask(__name__)
app.config.from_envvar('LIVEMAP_SETTINGS')
socketio = SocketIO(app)
db = SQLAlchemy(app)

import real_time_map.views
import real_time_map.models
