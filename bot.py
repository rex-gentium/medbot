import telebot
import telebot_calendar
import logging
import json
import datetime

from telebot.types import ReplyKeyboardRemove

from dbworker import DbWorker
from settings import *
from state import State
from telebot_calendar import CallbackData

logging.basicConfig(filename='medbot.log', level=logging.DEBUG)
bot = telebot.TeleBot(bot_token)
dbworker = DbWorker()
calendar = CallbackData("calendar", "action", "year", "month", "day")
logger = logging.getLogger(__name__)
date_format = '%d.%m.%Y'
time_format = '%H:%M'


@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.chat.id
    logger.debug(f"Received start command from user {user_id}")
    user_name = message.from_user.first_name
    exists = dbworker.does_user_exist(user_id)
    if not exists:
        dbworker.add_user(user_id)
        greeting = "Приятно познакомиться"
    else:
        greeting = "С возвращением"
    dbworker.set_user_state(user_id, None)
    dbworker.clear_session_data(user_id)
    reply = f"{greeting}, {user_name}! Вот список моих команд:\n" \
            f"/start\n" \
            f"/addmedication\n" \
            f"/addprescription"
    bot.send_message(user_id, reply)


@bot.message_handler(commands=["addmedication"])
def cmd_add_medication(message):
    user_id = message.chat.id
    logger.debug(f"Received addmedication command from user {user_id}")
    dbworker.set_user_state(user_id, State.ADD_MED_ENTER_NAME)
    bot.send_message(user_id, "Введите название препарата")


@bot.message_handler(func=lambda message: dbworker.get_user_state(message.chat.id) == State.ADD_MED_ENTER_NAME)
def user_entering_name(message):
    user_id = message.chat.id
    medication_name = message.text.strip()
    med_exists = dbworker.does_medication_exist(medication_name)
    if not med_exists:
        dbworker.add_medication(user_id, medication_name)
        reply = f"Препарат {medication_name} успешно создан"
    else:
        reply = f"Препарат {medication_name} уже зарегистрирован"
    dbworker.set_user_state(user_id, None)
    bot.send_message(user_id, reply)


@bot.message_handler(commands=["addprescription"])
def cmd_add_prescription(message):
    user_id = message.chat.id
    logger.debug(f"Received addprescription command from user {user_id}")
    medications = dbworker.get_medications_by_user(user_id)
    if medications:
        dbworker.set_user_state(user_id, State.ADD_PRESCR_SELECT_MED)
        medications_buttons = [[{'text': m[1], "callback_data": m[0]}] for m in medications]
        keyboard = json.dumps({"inline_keyboard": medications_buttons})
        bot.send_message(user_id, "Выберите препарат", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "У вас ещё нет препаратов. Создайте новый командой /addmedication")


@bot.callback_query_handler(
    func=lambda call: dbworker.get_user_state(call.message.chat.id) == State.ADD_PRESCR_SELECT_MED)
def user_selected_med(call):
    user_id = call.message.chat.id
    med_id = int(call.data)
    dbworker.add_to_session_data(user_id, {"medication_id": med_id})
    dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_DOSE)
    bot.send_message(user_id, "Введите дозировку препарата (целое число)")


@bot.message_handler(func=lambda message: dbworker.get_user_state(message.chat.id) == State.ADD_PRESCR_ENTER_DOSE)
def user_entered_dose(message):
    user_id = message.chat.id
    if message.text.isdigit():
        dose = int(message.text)
        dbworker.add_to_session_data(user_id, {"dose": dose})
        dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_START_DATE)
        send_enter_start_date(user_id)
    else:
        bot.send_message(user_id, "Сообщение не удается распознать как целое число")


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar.prefix))
def user_selected_date(call):
    user_id = call.message.chat.id
    name, action, year, month, day = call.data.split(calendar.sep)
    date = telebot_calendar.calendar_query_handler(bot, call, name, action, year, month, day)
    user_state = dbworker.get_user_state(user_id)
    if action == "DAY":
        if user_state == State.ADD_PRESCR_ENTER_START_DATE:
            # выбрали стартовую дату
            dbworker.add_to_session_data(user_id, {"start_date": date.strftime(date_format)})
            dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_END_DATE)
            bot.send_message(user_id, f"Установлена дата начала {date.strftime(date_format)}",
                             reply_markup=ReplyKeyboardRemove())
            send_enter_end_date(user_id)
        elif user_state == State.ADD_PRESCR_ENTER_END_DATE:
            # задали конечную дату
            dbworker.add_to_session_data(user_id, {"end_date": date.strftime(date_format)})
            bot.send_message(user_id, f"Установлена дата окончания {date.strftime(date_format)}",
                             reply_markup=ReplyKeyboardRemove())
            dbworker.set_user_state(user_id, State.ADD_PRESCR_SELECT_EVENT)
            send_select_event(user_id)
    elif action == "CANCEL":
        if user_state == State.ADD_PRESCR_ENTER_START_DATE:
            # отменили стартовую дату
            bot.send_message(user_id, "Дата начала правила не задана (не ограниченное время в прошлом)",
                             reply_markup=ReplyKeyboardRemove())
            dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_END_DATE)
            send_enter_end_date(user_id)
        elif user_state == State.ADD_PRESCR_ENTER_END_DATE:
            # отменили конечную дату
            bot.send_message(user_id, "Дата окончания правила не задана", reply_markup=ReplyKeyboardRemove())
            dbworker.set_user_state(user_id, State.ADD_PRESCR_SELECT_EVENT)
            send_select_event(user_id)


def send_enter_start_date(user_id):
    send_enter_date(user_id, "Выберите дату начала правила")


def send_enter_end_date(user_id):
    send_enter_date(user_id, "Выберите дату окончания правила")


def send_enter_date(user_id, text):
    now = datetime.datetime.now()
    calendar_keyboard = telebot_calendar.create_calendar(calendar.prefix, now.year, now.month)
    bot.send_message(user_id, text, reply_markup=calendar_keyboard)


def send_select_event(user_id):
    events = dbworker.get_events()
    event_buttons = [[{'text': e[1], "callback_data": e[0]}] for e in events]
    event_buttons.append([{'text': 'не привязывать к событию', 'callback_data': 'cancel'}])
    keyboard = json.dumps({"inline_keyboard": event_buttons})
    bot.send_message(user_id, "Выберите событие приёма (если нужно)", reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call: dbworker.get_user_state(call.message.chat.id) == State.ADD_PRESCR_SELECT_EVENT)
def user_selected_event(call):
    user_id = call.message.chat.id
    event_id = call.data
    if not event_id == 'cancel':
        dbworker.add_to_session_data(user_id, {"event_id": int(event_id)})
        dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_TIME)
        bot.send_message(user_id, "За какое время до/после выбранного события нужно принять препарат?\n"
                                  "Введите время в формате ЧЧ:ММ\n"
                                  "где ЧЧ - часы, ММ - минуты."
                                  "Если препарат нужно принять до указанного события, поставьте "
                                  "перед временем знак минус.\n\n"
                                  "Если препарат нужно принять во время события, введите 0 (ноль)")
    else:
        dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_CONDITIONS)
        send_enter_conditions(user_id)


def send_enter_conditions(user_id):
    conditions = dbworker.get_conditions()
    condition_lines = [f"{str(c[0])}. {str(c[1])}" for c in conditions]
    condition_str = "\n".join(condition_lines)
    bot.send_message(user_id, "Выберите особые условия, которые нужно применить к правилу.\n" + condition_str +
                              "\nНапишите номера этих условий через пробел.\n"
                              "Для пропуска этого шага введите 0 (ноль)")


@bot.message_handler(func=lambda message: dbworker.get_user_state(message.chat.id) == State.ADD_PRESCR_ENTER_TIME)
def user_entered_time(message):
    user_id = message.chat.id
    time = message.text
    if time == '0':
        dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_CONDITIONS)
        bot.send_message(user_id, "Временной интервал не задан")
        send_enter_conditions(user_id)
    else:
        try:
            interval = parse_interval(time)
            dbworker.add_to_session_data(user_id, {
                'time_delta_days': interval.days,
                'time_delta_seconds': interval.seconds
            })
            dbworker.set_user_state(user_id, State.ADD_PRESCR_ENTER_CONDITIONS)
            send_enter_conditions(user_id)
        except:
            bot.send_message(user_id, "Время указано в неправильном формате. Введите время в указанном формате")


def parse_interval(time_str):
    is_minus = time_str[0] == '-'
    if is_minus:
        time_str = time_str[1:]
    t = datetime.datetime.strptime(time_str, time_format)
    delta = datetime.timedelta(hours=t.hour, minutes=t.minute)
    if is_minus:
        delta = -delta
    return delta


@bot.message_handler(func=lambda message: dbworker.get_user_state(message.chat.id) == State.ADD_PRESCR_ENTER_CONDITIONS)
def user_entered_time(message):
    user_id = message.chat.id
    user_text = message.text
    if user_text == '0':
        bot.send_message(user_id, "Особых условий не будет")
    conditions = dbworker.get_conditions()
    condition_ids = set([c[0] for c in conditions])
    user_condition_ids = user_text.split(' ')
    filtered_condition_ids = [uc_id for uc_id in user_condition_ids if uc_id in condition_ids]
    if filtered_condition_ids:
        dbworker.add_to_session_data(user_id, {'condition_ids': filtered_condition_ids})
    dbworker.set_user_state(user_id, None)
    construct_prescription(user_id)


def construct_prescription(user_id):
    session_data = dbworker.get_session_data(user_id)
    start_date = session_data.get('start_date')
    if start_date:
        start_date = datetime.datetime.strptime(start_date, date_format)
    end_date = session_data.get('end_date')
    if end_date:
        end_date = datetime.datetime.strptime(end_date, date_format)
    time_delta = None
    time_delta_days = session_data.get('time_delta_days')
    time_delta_seconds = session_data.get('time_delta_seconds')
    if time_delta_days and time_delta_seconds:
        time_delta = datetime.timedelta(days=time_delta_days, seconds=time_delta_seconds)
    dbworker.add_prescription(user_id, session_data['medication_id'], start_date, end_date, session_data['dose'],
                              session_data.get('event_id'), time_delta)
    bot.send_message(user_id, "Создано правило")
    dbworker.clear_session_data(user_id)


if __name__ == '__main__':
    bot.polling(none_stop=True)
