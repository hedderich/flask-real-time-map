from real_time_map import db


class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_uuid = db.Column(db.String(36))


class VehicleRegistrationLog(db.Model):
    __tablename__ = 'vehicle_registration'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    action = db.Column(db.String(10))

    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'),
                           nullable=False)
    vehicle = db.relationship('Vehicle',
                              backref=db.backref('registrations', lazy=True))


class VehicleLocationLog(db.Model):
    __tablename__ = 'vehicle_location'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)

    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'),
                           nullable=False)
    vehicle = db.relationship('Vehicle',
                              backref=db.backref('locations', lazy=True))

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)


db.create_all()
