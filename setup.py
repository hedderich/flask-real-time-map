from setuptools import find_packages, setup

setup(
    name='flask-real-time-map',
    version='0.1.0',

    license='MIT',
    url='https://github.com/hedderich/flask-real-time-map',
    author='Marvin Hedderich',
    author_email='dev@hedderich.info',
    description='Display a live visualization of vehicle position data',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-socketio',
        'flask-sqlalchemy',
        'gevent',
        'gevent-websocket',
        'haversine',
        'python-dateutil'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
