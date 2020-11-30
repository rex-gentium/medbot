from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from db.models import *

engine = create_engine('postgresql://medbot:3285@localhost/medbot', echo=True)
Session = sessionmaker(bind=engine)


def session_wrapper(f):
    def wrapper(*args, **kwargs):
        session = Session()
        args = [args[0], session, *args[1:]]
        res = f(*args, **kwargs)
        session.commit()
        session.close()
        return res
    return wrapper


class DbWorker:

    def __init__(self):
        self.engine = create_engine('postgresql://medbot:3285@localhost/medbot', echo=True)
        self.Session = sessionmaker(bind=self.engine)

    @session_wrapper
    def get_user(self, session, telegram_id):
        maybe_user = session.query(User) \
            .filter_by(id=telegram_id) \
            .first()
        return maybe_user

    @session_wrapper
    def does_user_exist(self, session, telegram_id):
        maybe_user = session.query(User) \
            .filter_by(id=telegram_id) \
            .first()
        return bool(maybe_user)

    @session_wrapper
    def add_user(self, session, telegram_id):
        user = User(id=telegram_id)
        session.add(user)

    @session_wrapper
    def add_medication(self, session, user_id, name):
        medication = Medication(user_id=user_id, name=name)
        session.add(medication)

    @session_wrapper
    def does_medication_exist(self, session, name):
        med = session.query(Medication)\
            .filter_by(name=name)\
            .first()
        return bool(med)

    @session_wrapper
    def add_prescription(self, session, user_id, medication_id, start_date, end_date, dose,
                         event_id, time_delta):
        prescription = Prescription(user_id=user_id, medication_id=medication_id, start_date=start_date,
                                    end_date=end_date, dose=dose, event_id=event_id, time_delta=time_delta)
        session.add(prescription)
        return prescription

    @session_wrapper
    def set_user_state(self, session, user_id, state_id):
        user = session.query(User)\
            .filter_by(id=user_id)\
            .first()
        if user:
            user.state_id = state_id

    @session_wrapper
    def get_user_state(self, session, user_id):
        user = session.query(User).filter_by(id=user_id).first()
        if user and user.state_id:
            state = session.query(State)\
                .filter_by(id=user.state_id)\
                .first()
            return state.id
        else:
            return None

    @session_wrapper
    def get_medications_by_user(self, session, user_id):
        meds = session.query(Medication)\
            .filter_by(user_id=user_id)\
            .order_by(Medication.name)\
            .all()
        return [(m.id, m.name) for m in meds]

    @session_wrapper
    def get_events(self, session):
        events = session.query(Event)\
            .order_by(Event.id)\
            .all()
        return [(e.id, e.name) for e in events]

    @session_wrapper
    def add_to_session_data(self, session, user_id, new_dict):
        user = session.query(User)\
            .filter_by(id=user_id)\
            .first()
        if user:
            user.session_data.update(new_dict)
            flag_modified(user, "session_data")

    @session_wrapper
    def get_conditions(self, session):
        conditions = session.query(SpecialCondition) \
            .order_by(SpecialCondition.id) \
            .all()
        return [(c.id, c.name) for c in conditions]

    @session_wrapper
    def get_session_data(self, session, user_id):
        user = session.query(User)\
            .filter_by(id=user_id)\
            .first()
        return user.session_data

    @session_wrapper
    def clear_session_data(self, session, user_id):
        user = session.query(User) \
            .filter_by(id=user_id) \
            .first()
        user.session_data = {}
        flag_modified(user, "session_data")
