from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Interval, ForeignKey

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    state_id = Column(Integer, ForeignKey('state.id'), default=None)


class State(Base):
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Medication(Base):
    __tablename__ = 'medication'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String, unique=True, nullable=False)


class Prescription(Base):
    __tablename__ = 'prescription'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    medication_id = Column(Integer, ForeignKey('medication.id'), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    dose = Column(Integer, nullable=False)
    prescription_type = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    time_delta = Column(Interval)


class SpecialCondition(Base):
    __tablename__ = 'special_condition'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PrescriptionConditions(Base):
    __tablename__ = 'prescription_conditions'
    prescription_id = Column(Integer, ForeignKey('prescription.id'), primary_key=True, nullable=False)
    condition_id = Column(Integer, ForeignKey('special_condition.id'), primary_key=True, nullable=False)


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
