import telebot
import telebot_calendar
import logging
import json
import datetime

from telebot.types import ReplyKeyboardRemove

from dbworker import DbWorker
from user_service import UserService
from medication_service import MedicationService
from settings import *
from state import State
from telebot_calendar import CallbackData

logging.basicConfig(filename='medbot.log', level=logging.DEBUG)
bot = telebot.TeleBot(bot_token)
dbworker = DbWorker()
user_service = UserService(dbworker)
medication_service = MedicationService(dbworker)
calendar = CallbackData("calendar", "action", "year", "month", "day")
logger = logging.getLogger(__name__)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.chat.id
    logger.debug(f"Received start command from user {user_id}")
    username = message.from_user.first_name
    reply = user_service.add_user_if_needed(user_id, username)
    bot.send_message(user_id, reply)


@bot.message_handler(commands=["addmedication"])
def cmd_add_medication(message):
    user_id = message.chat.id
    logger.debug(f"Received addmedication command from user {user_id}")
    user_service.set_user_state(user_id, State.ADD_MED_ENTER_NAME)
    bot.send_message(user_id, "Введите название препарата")


@bot.message_handler(func=lambda message: user_service.get_user_state(message.chat.id) == State.ADD_MED_ENTER_NAME)
def user_entering_name(message):
    user_id = message.chat.id
    medication_name = message.text.strip()
    if medication_name:
        existing_medication = medication_service.get_medication(medication_name)
        if not existing_medication:
            medication_service.add_medication(user_id, medication_name)
            user_service.set_user_state(user_id, None)
            reply = f"Препарат {medication_name} успешно создан"
        else:
            reply = f"Препарат {medication_name} уже зарегистрирован"
    else:
        reply = "Ай-яй, строчка-то пустая!"
    bot.send_message(user_id, reply)


@bot.message_handler(commands=["addprescription"])
def cmd_add_prescription(message):
    user_id = message.chat.id
    logger.debug(f"Received addprescription command from user {user_id}")
    medications = medication_service.get_for_user(user_id)
    user_service.set_user_state(user_id, State.ADD_PRESCR_SELECT_MED)
    if medications:
        medications_buttons = [{'text': m[1], "callback_data": m[0]} for m in medications]
        keyboard = json.dumps({"inline_keyboard": [medications_buttons]})
        bot.send_message(user_id, "gth", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "У вас ещё нет препаратов. Создайте новый командой /addmedication")


@bot.callback_query_handler(func=lambda call: user_service.get_user_state(call.message.chat.id) == State.ADD_PRESCR_SELECT_MED)
def user_selected_med(call):
    user_id = call.message.chat.id
    med_id = call.data
    user_service.add_to_session_data(user_id, [{"medication_id": med_id}])
    user_service.set_user_state(user_id, State.ADD_PRESCR_ENTER_DOSE)
    bot.send_message(user_id, "Введите дозировку препарата (целое число)")


@bot.message_handler(func=lambda message: user_service.get_user_state(message.chat.id) == State.ADD_PRESCR_ENTER_DOSE)
def user_entered_dose(message):
    user_id = message.chat.id
    if message.text.isdigit():
        dose = int(message.text)
        user_service.add_to_session_data(user_id, [{"dose": dose}])
        user_service.set_user_state(user_id, State.ADD_PRESCR_ENTER_START_DATE)
        now = datetime.datetime.now()
        start_calendar_keyboard = telebot_calendar.create_calendar(calendar.prefix, now.year, now.month)
        bot.send_message(user_id, "Выберите дату начала правила", reply_markup=start_calendar_keyboard)
    else:
        bot.send_message(user_id, "Сообщение не удается распознать как целое число")


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar.prefix))
def callback_inline(call):
    user_id = call.message.chat.id
    name, action, year, month, day = call.data.split(calendar.sep)
    date = telebot_calendar.calendar_query_handler(bot, call, name, action, year, month, day)
    user_state = user_service.get_user_state(user_id)
    if action == "DAY":
        if user_state == State.ADD_PRESCR_ENTER_START_DATE:
            # выбрали стартовую дату
            user_service.add_to_session_data(user_id, [{"start_date": str(date)}])
            user_service.set_user_state(user_id, State.ADD_PRESCR_ENTER_END_DATE)
            now = datetime.datetime.now()
            end_calendar_keyboard = telebot_calendar.create_calendar(calendar.prefix, now.year, now.month)
            bot.send_message(user_id, f"Установлена дата начала {date.strftime('%d.%m.%Y')}",
                             reply_markup=ReplyKeyboardRemove())
            bot.send_message(user_id, "Выберите дату окончания правила", reply_markup=end_calendar_keyboard)
        elif user_state == State.ADD_PRESCR_ENTER_END_DATE:
            # задали конечную дату
            pass
    elif action == "CANCEL":
        if user_state == State.ADD_PRESCR_ENTER_START_DATE:
            # отменили стартовую дату
            bot.send_message(user_id, "Дата начала правила не задана (не ограниченное время в прошлом)",
                             reply_markup=ReplyKeyboardRemove())
            user_service.set_user_state(user_id, State.ADD_PRESCR_ENTER_END_DATE)
            now = datetime.datetime.now()
            end_calendar_keyboard = telebot_calendar.create_calendar(calendar.prefix, now.year, now.month)
            bot.send_message(user_id, "Выберите дату окончания правила", reply_markup=end_calendar_keyboard)
        elif user_state == State.ADD_PRESCR_ENTER_END_DATE:
            # отменили конечную дату
            bot.send_message(user_id, "Дата окончания правила не задана", reply_markup=ReplyKeyboardRemove())
            user_service.set_user_state(user_id, State.ADD_PRESCR_SELECT_EVENT)
            events = dbworker.get_events()
            event_buttons = [{'text': e[1], "callback_data": e[0]} for e in events]
            keyboard = json.dumps({"inline_keyboard": [event_buttons]})
            bot.send_message(user_id, "Выберите событие приёма (если нужно)", reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)
