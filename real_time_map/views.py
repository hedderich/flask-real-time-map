import uuid
from datetime import datetime, timedelta

from dateutil.parser import parse as parse_iso
from flask import render_template, request
from haversine import haversine

from real_time_map import app, db, models, socketio


@app.route('/')
def index():
    return render_template('index.html', mapbox_key=app.config['MAPBOX_KEY'])


@socketio.on('connected', namespace='/vehicles')
def send_initial_data():
    """
    When a new client connects, send the latest valid waypoint of every vehicle
    that showed up in the last 10 minutes back to this client.

    """
    since = datetime.utcnow() - timedelta(minutes=10)
    entries = models.VehicleLocationLog.get_latest_entries(since)

    for entry in entries:
        socketio.emit('update_location',
                      {'vehicle_id': entry.vehicle.vehicle_uuid,
                       'lat': entry.lat,
                       'lng': entry.lng},
                      namespace='/vehicles',
                      room=request.sid)


@app.route('/vehicles', methods=['POST'])
def register_vehicle():
    try:
        vehicle_id = str(uuid.UUID(request.get_json()['id']))
    except KeyError:
        return 'No vehicle ID provided', 400
    except ValueError:
        return 'Provided vehicle ID is not a valid UUID', 400

    vehicle = models.Vehicle.query.filter_by(vehicle_uuid=vehicle_id).first()
    if not vehicle:
        vehicle = models.Vehicle(vehicle_uuid=vehicle_id)
        db.session.add(vehicle)

    models.VehicleRegistrationLog(vehicle=vehicle,
                                  time=datetime.utcnow(),
                                  action='register')
    db.session.commit()

    return '', 204


@app.route('/vehicles/<uuid:vehicle_id>/locations', methods=['POST'])
def update_location(vehicle_id):
    vehicle_id = str(vehicle_id)

    vehicle = models.Vehicle.query.filter_by(vehicle_uuid=vehicle_id).first()
    if not vehicle:
        return 'Vehicle not found', 404

    if vehicle.registrations[-1].action != 'register':
        return 'Vehicle not registered', 409

    data = request.get_json()

    # Only store waypoints that are inside the "city boundaries"
    if haversine((data['lat'], data['lng']), (52.53, 13.403)) <= 3.5:
        models.VehicleLocationLog(vehicle=vehicle,
                                  time=parse_iso(data['at']),
                                  lat=data['lat'],
                                  lng=data['lng'])
        db.session.commit()

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
    vehicle_id = str(vehicle_id)

    vehicle = models.Vehicle.query.filter_by(vehicle_uuid=vehicle_id).first()
    if not vehicle:
        return 'Vehicle not found', 404

    models.VehicleRegistrationLog(vehicle=vehicle,
                                  time=datetime.utcnow(),
                                  action='deregister')
    db.session.commit()

    socketio.emit('delete_vehicle',
                  {'vehicle_id': str(vehicle_id)},
                  namespace='/vehicles')

    return '', 204
