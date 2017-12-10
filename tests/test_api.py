import json
import uuid
from datetime import datetime, timedelta
from unittest import mock

import pytest

from real_time_map import app, models


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def vehicle_id():
    return str(uuid.uuid1())


def register_vehicle(client, vehicle_id):
    return client.post('/vehicles',
                       data=json.dumps({'id': vehicle_id}),
                       content_type='application/json')


def update_location(client, vehicle_id, lat, lng):
    now = datetime.isoformat(datetime.utcnow())
    return client.post('/vehicles/%s/locations' % vehicle_id,
                       data=json.dumps({'lat': lat,
                                        'lng': lng,
                                        'at': now}),
                       content_type='application/json')


def test_register_vehicle(client, vehicle_id):
    response = register_vehicle(client, vehicle_id)

    vehicle = models.Vehicle.query.filter_by(vehicle_uuid=vehicle_id).first()

    assert vehicle.vehicle_uuid == vehicle_id
    assert vehicle.registrations[-1].action == 'register'

    assert response.status_code == 204
    assert response.data == b''


@mock.patch('flask_socketio.SocketIO.emit')
def test_update_location(socketio, client, vehicle_id):
    register_vehicle(client, vehicle_id)
    response = update_location(client, vehicle_id, 52.53, 13.403)

    since = datetime.utcnow() - timedelta(seconds=2)
    entry = models.VehicleLocationLog.get_latest_entries(since)[-1]
    expected = mock.call('update_location',
                         {'vehicle_id': vehicle_id,
                          'lat': 52.53, 'lng': 13.403},
                         namespace='/vehicles')

    assert socketio.called
    assert socketio.call_args == expected
    assert entry.vehicle.vehicle_uuid == vehicle_id
    assert entry.lat, entry.lgn == (52.53, 13.403)

    assert response.status_code == 204
    assert response.data == b''


@mock.patch('flask_socketio.SocketIO.emit')
def test_update_location_out_of_boundaries(socketio, client, vehicle_id):
    register_vehicle(client, vehicle_id)
    response = update_location(client, vehicle_id, 51.2, 45.3)

    expected = mock.call('delete_vehicle',
                         {'vehicle_id': vehicle_id},
                         namespace='/vehicles')

    assert socketio.called
    assert socketio.call_args == expected

    assert response.status_code == 204
    assert response.data == b''


@mock.patch('flask_socketio.SocketIO.emit')
def test_delete_vehicle(socketio, client, vehicle_id):
    register_vehicle(client, vehicle_id)
    response = client.delete('/vehicles/%s' % vehicle_id)

    vehicle = models.Vehicle.query.filter_by(vehicle_uuid=vehicle_id).first()
    expected = mock.call('delete_vehicle',
                         {'vehicle_id': vehicle_id},
                         namespace='/vehicles')

    assert socketio.called
    assert socketio.call_args == expected
    assert vehicle.registrations[-1].action == 'deregister'

    assert response.status_code == 204
    assert response.data == b''
