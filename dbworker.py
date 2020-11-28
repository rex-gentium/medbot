from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Medication, User, Prescription


class DbWorker:

    def __init__(self):
        self.engine = create_engine('postgresql://medbot:3285@localhost/medbot', echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def add_user(self, telegram_id):
        session = self.Session()
        user = User(id=telegram_id)
        session.add(user)
        session.commit()
        session.close()

    def add_medication(self, user_id, name):
        session = self.Session()
        medication = Medication(user_id, name)
        session.add(medication)
        session.commit()
        session.close()

    def add_prescription(self, user_id, medication_id, start_date, end_date, dose,
                         prescription_type, event_id, time_delta):
        session = self.Session()
        prescription = Prescription(user_id=user_id, medication_id=medication_id, start_date=start_date,
                                    end_date=end_date, dose=dose, prescription_type=prescription_type,
                                    event_id=event_id, time_delta=time_delta)
        session.add(prescription)
        session.commit()
        session.close()
