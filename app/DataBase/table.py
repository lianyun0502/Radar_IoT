from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base, engine
from datetime import datetime

class Users(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True)
    email = Column(String(50))
    phone = Column(String(50))
    address = Column(String(50))
    password = Column(String(50))

    device_pool = relationship('DevicePool', uselist=False, backref='users') # one to one relationship

    def __init__(self, id, email, phone, address, password):
        self.id = id
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password


class Devices(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    topic = Column(String(50))
    description = Column(Text)
    status = Column(Boolean, default=True)

    register_devices = relationship('register_devices', backref='devices')

    def __init__(self, name, topic, description, status):
        self.name = name
        self.topic = topic
        self.description = description
        self.status = status

class DevicePool(Base):
    __tablename__ = 'device_pool'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.id'))

    register_devices = relationship('register_devices', backref='device_pool')

    def __init__(self, device_id, user_id):
        self.device_id = device_id
        self.user_id = user_id

class RegisterDevices(Base):
    __tablename__ = 'register_devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    register_date = Column(DateTime, default=datetime.utcnow())

    def __init__(self, device_id):
        self.device_id = device_id

class RawData(Base):
    __tablename__ = 'raw_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    raw_data = Column(String(50))
    date = Column(DateTime)

    def __init__(self, device_id):
        self.device_id = device_id




Base.metadata.create_all(bind=engine)




    