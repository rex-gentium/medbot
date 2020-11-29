

class MedicationService:
    def __init__(self, dbworker):
        self.dbworker = dbworker

    def get_medication(self, name):
        return self.dbworker.get_medication(name)

    def add_medication(self, user_id, name):
        return self.dbworker.add_medication(user_id, name)

    def get_for_user(self, user_id):
        meds = self.dbworker.get_medications_by_user(user_id)
        res = [(m.id, m.name) for m in meds]
        return res
