import json
import uuid
from unittest import mock

import pytest

from real_time_map import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def vehicle():
    return str(uuid.uuid1())


def test_register_vehicle(client, vehicle):
    response = client.post('/vehicles',
                           data=json.dumps({'id': vehicle}),
                           content_type='application/json')

    assert response.status_code == 204
    assert response.data == b''


@mock.patch('flask_socketio.SocketIO.emit')
def test_update_location(socketio, client, vehicle):
    response = client.post('/vehicles/%s/locations' % vehicle,
                           data=json.dumps({'lat': 52.53,
                                            'lng': 13.403,
                                            'at': '2017-12-02T12:00:00+01:00'}),
                           content_type='application/json')

    expected = mock.call('update_location',
                         {'vehicle_id': vehicle, 'lat': 52.53, 'lng': 13.403},
                         namespace='/vehicles')

    assert socketio.called
    assert socketio.call_args == expected

    assert response.status_code == 204
    assert response.data == b''


@mock.patch('flask_socketio.SocketIO.emit')
def test_update_location_out_of_boundaries(socketio, client, vehicle):
    response = client.post('/vehicles/%s/locations' % vehicle,
                           data=json.dumps({'lat': 51.2,
                                            'lng': 45.3,
                                            'at': '2017-12-02T12:00:00+01:00'}),
                           content_type='application/json')

    expected = mock.call('delete_vehicle',
                         {'vehicle_id': vehicle},
                         namespace='/vehicles')

    assert socketio.called
    assert socketio.call_args == expected

    assert response.status_code == 204
    assert response.data == b''


@mock.patch('flask_socketio.SocketIO.emit')
def test_delete_vehicle(socketio, client, vehicle):
    response = client.delete('/vehicles/%s' % vehicle)

    expected = mock.call('delete_vehicle',
                         {'vehicle_id': vehicle},
                         namespace='/vehicles')

    assert socketio.called
    assert socketio.call_args == expected

    assert response.status_code == 204
    assert response.data == b''
