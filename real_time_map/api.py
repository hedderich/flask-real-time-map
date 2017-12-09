from flask import Flask, render_template, request
from flask_socketio import SocketIO
from haversine import haversine

async_mode = None

app = Flask(__name__)
app.config.from_envvar('LIVEMAP_SETTINGS')
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', mapbox_key=app.config['MAPBOX_KEY'])


@app.route('/vehicles', methods=['POST'])
def register_vehicle():
    return '', 204


@app.route('/vehicles/<uuid:vehicle_id>/locations', methods=['POST'])
def update_location(vehicle_id):
    data = request.get_json()

    if haversine((data['lat'], data['lng']), (52.53, 13.403)) <= 3.5:
        socketio.emit('update_location',
                      {'vehicle_id': str(vehicle_id),
                       'lat': data['lat'],
                       'lng': data['lng']},
                      namespace='/vehicles')
    else:
        socketio.emit('delete_vehicle',
                      {'vehicle_id': str(vehicle_id)},
                      namespace='/vehicles')

    return '', 204


@app.route('/vehicles/<uuid:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    socketio.emit('delete_vehicle',
                  {'vehicle_id': str(vehicle_id)},
                  namespace='/vehicles')

    return '', 204


if __name__ == '__main__':
    socketio.run(app)
