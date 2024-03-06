from background import keep_alive
from telebot_calendar import Calendar
from telebot_calendar import CallbackData
from telebot_calendar import RUSSIAN_LANGUAGE
from telebot import types, TeleBot
from datetime import datetime
from pytz import timezone
from pandas import read_excel
import codecs

token = '6563992719:AAFB8Gej6kneSNJvQ27FGW0k_Cbp61KemGg'
chat = -1957825416
book, chapters_list = '', ''

bot = TeleBot(token)
zone = timezone('Asia/Tomsk')
calendar1 = Calendar(language=RUSSIAN_LANGUAGE)
calendar2 = Calendar(language=RUSSIAN_LANGUAGE)
calendar_task = CallbackData(
    'calendar_task',
    'action',
    'year',
    'month',
    'day'
)
calendar_edification = CallbackData(
    'calendar_edification',
    'action',
    'year',
    'month',
    'day'
)


@bot.message_handler(commands=['start'])
def menu(message):
    keyboard = types.ReplyKeyboardMarkup()
    task = types.KeyboardButton(
        text='Узнать задание'
    )
    edification = types.KeyboardButton(
        text='Узнать назидание'
    )
    keyboard.add(
        task,
        edification
    )
    bot.send_message(
        message.from_user.id,
        'Выберите действие',
        reply_markup=keyboard
    )


@bot.message_handler(content_types=['text'])
def message(message):
    if '☦️📖' in message.text:
        save_edification(message)

    if message.chat.id == message.from_user.id:
        if message.text == 'Узнать задание':
            now = datetime.now(zone)
            bot.send_message(
                message.chat.id,
                'Выберите дату',
                reply_markup=calendar1.create_calendar(
                    name=calendar_task.prefix,
                    year=now.year,
                    month=now.month,
                ),
            )

    if message.chat.id == message.from_user.id:
        if message.text == 'Узнать назидание':
            now = datetime.now(zone)
            bot.send_message(
                message.chat.id,
                'Выберите дату',
                reply_markup=calendar2.create_calendar(
                    name=calendar_edification.prefix,
                    year=now.year,
                    month=now.month,
                ),
            )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        calendar_task.prefix
    )
)
def callback_task(call: types.CallbackQuery):
    name, action, year, month, day = call.data.split(
        calendar_task.sep
    )
    date = calendar1.calendar_query_handler(
        bot=bot,
        call=call,
        name=name,
        action=action,
        year=year,
        month=month,
        day=day
    )
    if action == 'DAY':
        now = datetime.now(zone)
        send_task(date, call.from_user.id, now)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        calendar_edification.prefix
    )
)
def callback__edification(call: types.CallbackQuery):
    name, action, year, month, day = call.data.split(
        calendar_edification.sep
    )
    date = calendar2.calendar_query_handler(
        bot=bot,
        call=call,
        name=name,
        action=action,
        year=year,
        month=month,
        day=day
    )
    if action == 'DAY':
        send_edification(date, call.from_user.id)


@bot.callback_query_handler(
    func=lambda call: call.data == 'textBible'
)
def send_textBible(call: types.CallbackQuery):
    text = ''
    text_list = []
    file = codecs.open('../Синодальный перевод - 77 книг - txt/' + book + '.txt', 'r', "utf-8")
    lines = [line.replace('\r', '\n') for line in file.read().split('\n')]
    file.close()
    global chapters_list
    chapters_list = str(chapters_list)
    if '_' in chapters_list:
        chapter = chapters_list.split('_')
    else:
        chapter = [chapters_list]
    for ind_chapter in range(len(chapter)):
        for i in range(len(lines)):
            if lines[i] == '=== ' + chapter[ind_chapter] + ' ===\n':
                adder = 0
                while (lines[i + adder] != '\n' or adder == 1):
                    text += lines[i + adder]
                    adder += 1
                break
        text_list.append(text)
        text = ''
        adder = 0
    for k in range(len(text_list)):
        text = text_list[k]
        if len(text) > 4096:
            for x in range(0, len(text), 4096):
                bot.send_message(
                    call.message.chat.id,
                    text[x: x + 4096]
                )
        else:
            bot.send_message(
                call.message.chat.id,
                text
            )

def send_task(
        date: datetime.date,
        userid: int,
        now: datetime.date
):
    taskdate = str(date.day) + '.'
    taskdate += str(date.month) + '.'
    taskdate += str(date.year)
    file = read_excel('base.xlsx')
    finder = False
    for i in range(len(file)):
        seriesdata = file[file.columns[0]].iloc[[i]].item()
        filedate = str(seriesdata.day) + '.'
        filedate += str(seriesdata.month) + '.'
        filedate += str(seriesdata.year)
        if filedate == taskdate:
            finder = True
            task = file[file.columns[1]].iloc[[i]].item()
            if str(task) != 'nan':
                global book, chapters_list
                book = file[file.columns[2]].iloc[[i]].item()
                chapters_list = file[file.columns[3]].iloc[[i]].item()
                textBible_keyboard = types.InlineKeyboardMarkup()
                textBible_button = types.InlineKeyboardButton(
                    'Открыть текст задания',
                    callback_data='textBible'
                )
                textBible_keyboard.add(
                    textBible_button
                )
                bot.send_message(
                    userid,
                    task,
                    reply_markup=textBible_keyboard
                )
            else:
                bot.send_message(
                    userid,
                    'Задания нет'
                )
    if not finder:
        bot.send_message(
            userid,
            'Задание не найдено'
        )


def send_edification(
        date: datetime.date,
        userid: int
):
    date = date.strftime('%d.%m.%y')
    file = codecs.open('edifications.txt', 'r', "utf-8")
    lines = [line + '\n' for line in file.read().split('\n')]
    file.close()
    finder = False
    endsymbol = '================================='
    endsymbol += '======================' + '\n'
    for i in range(len(lines)):
        if lines[i] == 'Дата: ' + date + '\n':
            finder = True
            j = i + 1
            edification = lines[j - 2] + lines[j]
            while lines[j] != endsymbol:
                j += 1
                if lines[j] != endsymbol:
                    edification += lines[j]
            if len(edification) > 4096:
                for x in range(0, len(edification), 4096):
                    bot.send_message(
                        userid,
                        edification[x: x + 4096]
                    )
            else:
                bot.send_message(
                    userid,
                    edification
                )
    if not finder:
        bot.send_message(
            userid,
            'Назидание не найдено'
        )


def save_edification(edification):
    now = datetime.now(zone)
    file = codecs.open('edifications.txt', 'a', "utf-8")
    file.write('Автор: ')
    file.write(str(edification.from_user.first_name) + ' ')
    file.write(str(edification.from_user.last_name) + ' (')
    file.write(str(edification.from_user.id) + ')\n')
    file.write('Дата: ')
    file.write(now.strftime('%d.%m.%y') + '\n')
    file.write(str(edification.text))
    file.write('\n')
    file.write(
        '======================================================='
    )
    file.write('\n\n\n\n')
    file.close()


keep_alive()
bot.infinity_polling()
