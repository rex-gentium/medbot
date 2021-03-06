from enum import IntEnum


class State(IntEnum):
    ADD_MED_ENTER_NAME = 1
    ADD_PRESCR_SELECT_MED = 2
    ADD_PRESCR_ENTER_DOSE = 3
    ADD_PRESCR_ENTER_START_DATE = 4
    ADD_PRESCR_ENTER_END_DATE = 5
    ADD_PRESCR_SELECT_EVENT = 6
    ADD_PRESCR_ENTER_TIME = 7
    ADD_PRESCR_ENTER_CONDITIONS = 8
