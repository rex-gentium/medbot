from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Medication, User, Prescription

engine = create_engine('postgresql://medbot:3285@localhost/medbot', echo=True)
Session = sessionmaker(bind=engine)


def add_user(telegram_id):
    session = Session()
    user = User(id=telegram_id)
    session.add(user)
    session.commit()
    session.close()


def add_medication(user_id, name):
    session = Session()
    medication = Medication(user_id, name)
    session.add(medication)
    session.commit()
    session.close()


def add_prescription(user_id, medication_id, start_date, end_date, dose, prescription_type, event_id, time_delta):
    session = Session()
    prescription = Prescription(user_id=user_id, medication_id=medication_id, start_date=start_date,
                                end_date=end_date, dose=dose, prescription_type=prescription_type,
                                event_id=event_id, time_delta=time_delta)
    session.add(prescription)
    session.commit()
    session.close()
