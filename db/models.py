from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, Integer, String, Date, Interval, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True)
    state_id = Column(BigInteger, ForeignKey('state.id'), default=None)
    session_data = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, state_id={self.state_id}, session_data={self.session_data})>"


class State(Base):
    __tablename__ = 'state'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<State(id={self.id}, name={self.name})>"


class Medication(Base):
    __tablename__ = 'medication'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Medication(id={self.id}, user_id={self.user_id}, name={self.name})>"


class Prescription(Base):
    __tablename__ = 'prescription'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    medication_id = Column(BigInteger, ForeignKey('medication.id'), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    dose = Column(Integer, nullable=False)
    event_id = Column(BigInteger, ForeignKey('event.id'), nullable=False)
    time_delta = Column(Interval)

    def __repr__(self) -> str:
        return f"<Prescription(id={self.id}, user_id={self.user_id}, medication_id={self.medication_id}, " \
               f"start_date={self.start_date}, end_date={self.end_date}, dose={self.dose}, event_id={self.event_id}, " \
               f"time_delta={self.time_delta})>"


class SpecialCondition(Base):
    __tablename__ = 'special_condition'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<SpecialCondition(id={self.id}, name={self.name})>"


class PrescriptionConditions(Base):
    __tablename__ = 'prescription_conditions'
    prescription_id = Column(BigInteger, ForeignKey('prescription.id'), primary_key=True, nullable=False)
    condition_id = Column(BigInteger, ForeignKey('special_condition.id'), primary_key=True, nullable=False)

    def __repr__(self) -> str:
        return f"<PrescriptionConditions(prescription_id={self.prescription_id}, condition_id={self.condition_id})>"


class Event(Base):
    __tablename__ = 'event'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, name={self.name})>"
