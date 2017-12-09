import uuid
from datetime import datetime

from dateutil.parser import parse as parse_iso
from flask import render_template, request
from haversine import haversine

from real_time_map import app, db, models, socketio


@app.route('/')
def index():
    return render_template('index.html', mapbox_key=app.config['MAPBOX_KEY'])


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
        entry = models.VehicleLocationLog(vehicle=vehicle,
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

    entry = models.VehicleRegistrationLog(vehicle=vehicle,
                                          time=datetime.utcnow(),
                                          action='deregister')
    db.session.commit()

    socketio.emit('delete_vehicle',
                  {'vehicle_id': str(vehicle_id)},
                  namespace='/vehicles')

    return '', 204
