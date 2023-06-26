import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from layouts import customer_main_menu, speaker_main_menu, admin_main_menu, unregistered_customer_menu, customer_menu, \
    speaker_menu


# TO DO
# Запросы:
#     1. Получение статуса по tg_id и заполнение user_survey как {'status': 'admin'}, если нет записи о человеке, он автоматом {'status': 'unregistered_customer'} (строка 45)
#     2. Получение данных о расписании и вывод в виде str (строка 106)
#     3. Отправка заполненных данных о посетителе в БД (строка 226)
#     4. Отправка вопроса в БД (строка 243)
#     5. Получение вопроса из БД (желательно вместе с id) (строка 275)
#     6. Удаление вопроса на который дали ответ (удалить по id) (строка 294)
#     7. Запрос рандомной записи из анкет (строка 309)
#     8. Запросить все tg_id посетителей из БД (массовая рассылка) (строка 329)

# Тестовые данные для использования (для тестирования вставляй свой id)
# статус один из четырёх:
#  'admin'
#  'speaker'
#  'customer'
#  'unregistered_customer'

def check_user(user_id): # + запрос
    if user_id == 406682076:
        user_survey = {
            'id': 406682076,
            'status': 'admin'
                    }
    else:
        user_survey = {
            'id': 406682076,
            'status': 'customer'
        }
    return user_survey


# Главное меню
def start(update, context):
    user_survey.clear()

    print('до', user_survey)

    message = update.message
    user_id = message.from_user.id
    user_survey.update(check_user(user_id))     # обновляю данные на запрошенные

    if user_survey['status'] == 'speaker':
        main_menu = speaker_main_menu
    elif user_survey['status'] == 'admin':
        main_menu = admin_main_menu
    else:
        main_menu = customer_main_menu

    keyboard = ReplyKeyboardMarkup(main_menu, one_time_keyboard=True)
    message.reply_text('Выберите пункт меню:', reply_markup=keyboard)
    print('после', user_survey)


def open_speaker_menu(update, context):
    if user_survey['status'] not in ['speaker', 'admin']:
        speaker_menu_text = '⛔️ Т.к. вы не спикер, вы не можете воспользоваться данной командой...'
        keyboard = ReplyKeyboardMarkup(customer_main_menu, one_time_keyboard=True)
        update.message.reply_text(speaker_menu_text, reply_markup=keyboard)
        return

    speaker_menu_text = 'Вы можете отвечать на заданные вам вопросы по нажатию на кнопку ниже:'
    keyboard = ReplyKeyboardMarkup(speaker_menu, one_time_keyboard=True)
    update.message.reply_text(speaker_menu_text, reply_markup=keyboard)


def open_customer_menu(update, context):
    if user_survey['status'] not in ['customer', 'speaker', 'admin']:
        customer_keyboard = unregistered_customer_menu
    else:
        customer_keyboard = customer_menu
    keyboard = ReplyKeyboardMarkup(customer_keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите пункт меню:', reply_markup=keyboard)


def go_back(update, context):
    menu_pattern = user_survey['status']
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text('Выберите пункт меню:', reply_markup=keyboard)


def get_info(update, context):
    menu_pattern = user_survey['status']
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text('Данный бот 🤖 предназначен для отслеживания актуальной '
                              'информации по расписанию выступлений\n'
                              'менеджмента рубрик вопрос/ответ во время докладов,\n'
                              'а так же для поиска собеседников и единомышленников\n'
                              'Да, всё у вас в гаджете 🤳',
                              parse_mode='HTML',
                              reply_markup=keyboard)


def get_schedule(update, context):
    menu_pattern = user_survey['status']
    # ❓ Добавить цикл по запросу времени и названиям
    # schedule = str([f'{start_time} - {end_time}: {speech}\n{about_speech}' for speech in speeches])
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text(schedule,
                              parse_mode='HTML',
                              reply_markup=keyboard)


def notificate_all(update, context):
    menu_pattern = user_survey['status']
    if menu_pattern != 'admin':
        access_denied = '⛔️ Т.к. вы не админ, вы не можете воспользоваться данной командой...'
        keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
        update.message.reply_text(access_denied, reply_markup=keyboard)
        return
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text('', reply_markup=keyboard)


# Заглушка, удалить после окончания
def under_construction(update, context):
    menu_pattern = user_survey['status']
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text(
        '🚧 К сожалению данная часть бота на реконструкции 🚧',
        reply_markup=keyboard)


def error(update, context):
    print(f'Update {update} caused error {context.error}')


# Регистрация новой заявки

def start_polling(update, context):
    if user_survey['status'] != 'unregistered_customer':
        speaker_menu_text = '⛔️ Ваша анкета уже присутствует в базе, вы не можете воспользоваться данной командой...'
        keyboard = ReplyKeyboardMarkup(customer_main_menu, one_time_keyboard=True)
        update.message.reply_text(speaker_menu_text, reply_markup=keyboard)
        return
    reply_keyboard = [['Отменить']]  # добавляем кнопку для отмены
    update.message.reply_text(f'Добро пожаловать в анкету! Введите /cancel, чтобы прервать опрос.\n{QUESTION_1}',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 1


# функция-обработчик ответа на первый вопрос
def question_1(update, context):
    global answers
    text = update.message.text
    answers["name"] = text
    reply_keyboard = [['Отменить']]
    update.message.reply_text(QUESTION_2,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 2


# функция-обработчик ответа на второй вопрос
def question_2(update, context):
    global answers
    text = update.message.text
    answers["age"] = text
    reply_keyboard = [['Отменить']]
    update.message.reply_text(QUESTION_3,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 3


# функция-обработчик ответа на третий вопрос
def question_3(update, context):
    global answers
    text = update.message.text
    answers["job"] = text
    reply_keyboard = [['Отменить']]
    update.message.reply_text(QUESTION_4,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 4


# функция-обработчик ответа на четвертый вопрос
def question_4(update, context):
    global answers
    text = update.message.text
    answers["stack"] = text
    reply_keyboard = [['Отменить']]
    update.message.reply_text(QUESTION_5,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 5


# функция-обработчик ответа на пятый вопрос
def question_5(update, context):
    global answers
    text = update.message.text
    answers["hobby"] = text
    reply_keyboard = [['Отменить']]
    update.message.reply_text(QUESTION_6,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 6


# функция-обработчик ответа на пятый вопрос
def question_6(update, context):
    global answers
    text = update.message.text
    answers["purpose"] = text
    reply_keyboard = [['Отменить']]
    update.message.reply_text(QUESTION_7,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 7


# функция-обработчик ответа на пятый вопрос и окончания опроса
def question_7(update, context):
    global answers
    text = update.message.text
    answers["region"] = text
    update.message.reply_text('✅ Спасибо за ответы на вопросы! Ваши данные были сохранены.',
                              reply_markup=ReplyKeyboardRemove())
    print(answers)
    # ❓ Добавить отправление данных в БД и запуск главного меню для перепроверки пользователя

    # очищаем словарь с ответами после завершения опроса
    answers = {}
    return ConversationHandler.END


def ask_question(update, context):
    reply_keyboard = [['Отменить']]  # добавляем кнопку для отмены
    update.message.reply_text('📝 Теперь вы можете написать свой вопрос, он будет передан ведущему:\n',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 1


def send_question(update, context):
    question_text = update.message.text

    # ❓ Отправить вопрос в базу данных
    print(question_text)
    # конец тестовых данных

    menu_pattern = user_survey['status']
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text('✅ Ваш вопрос отправлен, теперь стоит дождаться ответа от спикера', reply_markup=keyboard)

    return ConversationHandler.END


def get_admin_text(update, context):
    menu_pattern = user_survey['status']
    if menu_pattern != 'admin':
        speaker_menu_text = '⛔️ Вы не можете воспользоваться данной командой...'
        keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
        update.message.reply_text(speaker_menu_text, reply_markup=keyboard)
        return
    reply_keyboard = [['Отменить']]  # добавляем кнопку для отмены
    update.message.reply_text('📝 Написанный вами текст будет отправлен всем пользователям:\n',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 1


def answer_question(update, context):
    menu_pattern = user_survey['status']
    if user_survey['status'] != 'speaker':
        speaker_menu_text = '⛔️ Вы не можете воспользоваться данной командой...'
        keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
        update.message.reply_text(speaker_menu_text, reply_markup=keyboard)
        return

    # ❓ Заменить на запрос к БД
    asked_question = 'Чо у вас тут происходит?'
    # конец тестовых данных

    question_menu = InlineKeyboardButton("Вопрос отвечен", callback_data='get_next_question')
    keyboard = [[question_menu]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=asked_question,
                     reply_markup=reply_markup)


def get_next_question(update, context):
    chat_id = update.callback_query.message.chat.id
    message_id = update.callback_query.message.message_id
    keyboard = ReplyKeyboardMarkup(speaker_menu, one_time_keyboard=True)
    update.callback_query.message.reply_text('✅ Вопрос отвечен', reply_markup=keyboard)
    bot.delete_message(chat_id=chat_id, message_id=message_id)

    # ❓ Отправить запрос в БД на удаление записи с вопросом

    query = update.callback_query
    query.answer()
    return


def find_interlocutor(update, context):
    menu_pattern = user_survey['status']
    if user_survey['status'] == 'unregistered_customer':
        speaker_menu_text = '⛔️ Вы не можете воспользоваться данной командой...'
        keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
        update.message.reply_text(speaker_menu_text, reply_markup=keyboard)
        return

    # ❓ Заменить на запрос к БД по рандомному числу
    customer_form = {'tg_nick': '@Fulllmental', 'name': 'Арсений', 'age': '15', 'job': 'Лоботряс', 'stack': 'Питон', 'hobby': 'Игра на нервах', 'purpose': 'Найти работу', 'region': 'Москва'}
    # конец тестовых данных

    promo_form = f'👋 Приветствую, меня зовут {customer_form["name"]}\n' \    
                 f'<b>мне</b> {customer_form["age"]}, обычно я: {customer_form["job"]}\n' \
                 f'<b>хобби</b>: {customer_form["hobby"]}\n' \
                 f'<b>стэк технологий</b>: {customer_form["stack"]}\n' \
                 f'<b>цель</b> общения: {customer_form["purpose"]}\n' \
                 f'<b>регион</b>: {customer_form["region"]}\n<b>контакт</b>: {customer_form["tg_nick"]}'
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    bot.send_message(chat_id=update.message.chat_id,
                     text=promo_form,
                     parse_mode='HTML',
                     reply_markup=keyboard)


def send_announcement(update, context):
    announcement_text = update.message.text

    # ❓ Запросить все контакты из БД в список user_ids
    print(announcement_text)
    user_ids = [406682076]
    # конец тестовых данных

    for user_id in user_ids:
        bot.send_message(chat_id=user_id, text=announcement_text)

    menu_pattern = user_survey['status']
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text('✅ Рассылка окончена', reply_markup=keyboard)

    return ConversationHandler.END


# функция-обработчик отмены опроса
def cancel(update, context):
    menu_pattern = user_survey['status']
    keyboard = ReplyKeyboardMarkup(menu_patterns[menu_pattern], one_time_keyboard=True)
    update.message.reply_text('❌ Текущий выбор был отменён ❌', reply_markup=keyboard)

    # очищаем словарь с ответами после отмены опроса
    global answers
    answers = {}

    return ConversationHandler.END


if __name__ == '__main__':
    answers = {}
    user_survey = {}
    menu_patterns = {'admin': admin_main_menu,
                     'speaker': speaker_main_menu,
                     'customer': customer_main_menu,
                     'unregistered_customer': customer_main_menu}

    # определяем константы для опроса
    QUESTION_1 = 'Введите ваше ФИО:'
    QUESTION_2 = 'Сколько вам лет?'
    QUESTION_3 = 'Какой ваш род деятельности?'
    QUESTION_4 = 'Поделитесь своим стэком технологий?'
    QUESTION_5 = 'Какое у вас хобби?'
    QUESTION_6 = 'Какая у вас цель знакомства?'
    QUESTION_7 = 'Из какого вы региона?'

    registration = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('✅ Зарегистрировать анкету'), start_polling)],
        states={
            1: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_1)],
            2: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_2)],
            3: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_3)],
            4: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_4)],
            5: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_5)],
            6: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_6)],
            7: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, question_7)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    question_to_speaker = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('❔ Задать вопрос'), ask_question)],
        states={
            1: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, send_question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    mass_sending = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('📢 Массовая рассылка'), get_admin_text)],
        states={
            1: [MessageHandler(Filters.regex('^(Отменить)$'), cancel),
                MessageHandler(Filters.text, send_announcement)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    load_dotenv()
    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(tg_token)
    bot = Bot(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(MessageHandler(Filters.text('🎤 Меню докладчика'), open_speaker_menu))
    dispatcher.add_handler(MessageHandler(Filters.text('🤓 Меню участника'), open_customer_menu))
    dispatcher.add_handler(MessageHandler(Filters.text('❓ ЧаВо'), get_info))
    dispatcher.add_handler(MessageHandler(Filters.text('🕜 Расписание'), get_info))
    dispatcher.add_handler(MessageHandler(Filters.text('👋 Найти собеседника'), find_interlocutor))
    dispatcher.add_handler(MessageHandler(Filters.text('👈 Назад'), go_back))

    dispatcher.add_handler(registration)
    dispatcher.add_handler(question_to_speaker)
    dispatcher.add_handler(mass_sending)

    dispatcher.add_handler(MessageHandler(Filters.text('✨ Ответить на вопрос'), answer_question))
    dispatcher.add_handler(CallbackQueryHandler(get_next_question, pattern='^get_next_question$'))

    # доделать
    dispatcher.add_handler(MessageHandler(Filters.text('💸 Донат'), under_construction))

    dispatcher.add_error_handler(error)
    updater.start_polling()
