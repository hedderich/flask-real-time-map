# flask-real-time-map

Display a live visualization of vehicle position data.

## Setup

It is recommended to use an environment that lets you install
python versions and dependencies specific to your project, such as
[virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/),
pyenv or others.

This project has been tested using Python 3.5 and 3.6.

### Run server locally

Install directly from Github:

```
pip install git+git://github.com/hedderich/flask-real-time-map.git
```

Or clone the repository and execute:

```
pip install .
```

Before starting the server, be sure to set the environment variables for
Flask and the map application itself. You need to provide a configuration file
that contains a Mapbox API key, just like in the
[example settings](example_settings.cfg).

```
export FLASK_APP=real_time_map
export LIVEMAP_SETTINGS=~/local_settings.cfg
```

To make the app locally accessible on port 5000, just type:

```
flask run
```

### Inside a Docker container

Relying on the
[uwsgi-nginx-flask-docker](https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/)
Docker image, it is possible to serve the API so far. However it does not
work with the websocket connection yet, therefore the map will not be able to
update itself.

```
docker build -t live-map .
docker run -p 80:80 live-map
```

## Run tests

```
python setup.py test
```

## API reference

### Register vehicle

`POST /vehicles`

Request body: `{ "id": "vehicle-uuid" }`

Response: 204 No Content

### Update location

`POST /vehicles/:uuid/locations`

Request body: `{ "lat": 10.0, "lng": 20.0, "at": "2017-09-01T12:00:00Z" }`

Response: 204 No Content

### Deregister vehicle

`DELETE /vehicles/:uuid`

Response: 204 No Content
