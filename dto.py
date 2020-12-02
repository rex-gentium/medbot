from datetime import timedelta


class PrescriptionDto:
    abstract_events = {1, 5}
    event_localization = {
        1: 'утром',
        2: 'завтрака',
        3: 'обеда',
        4: 'ужина',
        5: 'на ночь'
    }

    def __init__(self, time_delta: timedelta, event_id, medication_name, dose):
        self.time_delta = time_delta
        self.event_id = event_id
        self.medication_name = medication_name
        self.dose = dose

    def __str__(self):
        return f"{self.__time_delta_str__()} {self.__event_str__()} {self.medication_name} {self.__dose_str__()}"\
            .strip()

    def __time_delta_str__(self):
        if self.time_delta is None:
            if self.event_id in self.abstract_events:
                return ""
            else:
                return "во время"
        else:
            delta_str = self.abs_time_delta_str(self.time_delta)
            if self.time_delta.days < 0:
                return f"за {delta_str} до"
            else:
                return f"через {delta_str} после"

    def __event_str__(self):
        if self.event_id is None:
            return "в течение дня"
        else:
            return self.event_localization[self.event_id]

    def __dose_str__(self):
        if self.dose == 1:
            return ""
        else:
            return f"{self.dose} шт"

    @staticmethod
    def abs_time_delta_str(time_delta):
        td = time_delta
        if td.days < 0:
            td = -td
        seconds = td.seconds
        hours = seconds // 3600
        minutes = (seconds - hours * 3600) // 60
        if hours > 0:
            return f"{hours} ч {minutes} мин"
        else:
            return f"{minutes} мин"

