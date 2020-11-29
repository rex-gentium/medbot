from state import State


class UserService:
    def __init__(self, dbworker):
        self.dbworker = dbworker

    def add_user_if_needed(self, user_id, user_name):
        user = self.dbworker.get_user(telegram_id=user_id)
        if not user:
            self.dbworker.add_user(user_id)
            greeting = "Приятно познакомиться"
        else:
            greeting = "С возвращением"
        return f"{greeting}, {user_name}! Вот список моих команд:\n" \
               f"/start\n" \
               f"/addmedication\n" \
               f"/addprescription"

    def set_user_state(self, user_id, state):
        self.dbworker.set_user_state(user_id, state)

    def get_user_state(self, user_id):
        return self.dbworker.get_user_state(user_id)

    def add_to_session_data(self, user_id, some_dicts):
        user = self.dbworker.get_user(user_id)
        if user:
            res = user.session_data
            for x in some_dicts:
                res.update(x)
            return res
        else:
            return None
