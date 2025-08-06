from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    all_time = db.Column(PickleType)
    booked_time = db.Column(MutableList.as_mutable(PickleType), default=list)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'), nullable=False)
    clinic = db.relationship('Clinic', back_populates='doctors')

class Clinic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    doctors = db.relationship('Doctor', back_populates='clinic', lazy=True)
