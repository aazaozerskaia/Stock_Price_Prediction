import telebot
from telebot import types
# import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import PIL
import datetime
from parser_yf import data_collection
from pred_week import week_prediction, plot_prediction
import warnings
warnings.filterwarnings("ignore")
matplotlib.use('agg')


token = ""
bot = telebot.TeleBot(token)

symbols = []

@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет! \n"
                                "В этом боте можно посмотреть динамику акций или прогноз на неделю вперёд. \n"
                                "Приступим? Выберите раздел:"):
    keyboard = types.ReplyKeyboardMarkup()
    it_1 = types.KeyboardButton("Индекс S&P 500")
    it_2 = types.KeyboardButton("Другие акции")
    keyboard.add(it_1)
    keyboard.add(it_2)
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard)
    bot.register_next_step_handler(message, first_step_choise)


@bot.message_handler(content_types=['text'])
def handle_errors(message):
    send_keyboard(message, text="Я не понимаю :( Давайте начнём с начала")


def first_step_choise(info):
    """get symbols from user"""
    act = info.text
    global symbols
    if act == "Индекс S&P 500":
        symbols = ["%5EGSPC"]
        keyboard = action_keyboard()
        answer = bot.send_message(info.chat.id, "Что будем делать?", reply_markup=keyboard)
        bot.register_next_step_handler(answer, action_section)
    elif act == "Другие акции":
        bot.send_message(info.chat.id, "Введите от 1 до 3 тикеров, котируемых на биржах США, через запятую \n"
                                                "пример: aapl, tsla, wmt")
        bot.register_next_step_handler(info, other_stocks)
    else:
        send_keyboard(info, 'Выберите раздел')


def other_stocks(info):
    global symbols
    text = info.text.split(',')
    symbols = sorted([i.strip().upper() for i in text])
    keyboard = action_keyboard()
    bot.send_message(info.chat.id, "Что будем делать?", reply_markup=keyboard)
    bot.register_next_step_handler(info, action_section)


def action_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    it_1 = types.KeyboardButton("Посмотрим динамику")
    it_2 = types.KeyboardButton("Поcмотрим прогноз на неделю")
    it_3 = types.KeyboardButton("Вернуться в начало")
    keyboard.add(it_1)
    keyboard.add(it_2)
    keyboard.add(it_3)
    return keyboard


def action_section(info):
    if info.text == "Посмотрим динамику":
        answer = bot.send_message(info.chat.id,
                             "Пожалуйста, введите дату начала и конца периода через запятую в формате год-месяц-день \n"
                             "пример: 2023-01-01, 2023-05-31")
        bot.register_next_step_handler(answer, send_dynamics)
    elif info.text == "Поcмотрим прогноз на неделю":
        bot.send_message(info.chat.id, text="Минутку..")
        try:
            images = send_prediction(info)
            for img in images:
                buf = io.BytesIO()
                img.savefig(buf, format='png')
                buf.seek(0)
                img = PIL.Image.open(buf)
                bot.send_photo(info.chat.id, img)

            bot.send_message(info.chat.id, "Что будем делать дальше?")
            send_keyboard(info, 'Выберите раздел')
        except:
            bot.send_message(info.chat.id, "Что-то пошло не так(")
            send_keyboard(info, 'Выберите раздел')
    else:
        send_keyboard(info, 'Выберите раздел')


def send_dynamics(info):
    try:
        # save given dates
        dates = info.text.split(',')
        time_int = sorted([day.strip() for day in dates])
        # for every ticker download data from y_finance
        for symb in symbols:
            tick = data_loader(symb, time_int)
            if tick.empty:
                bot.send_message(info.chat.id, "Некорректный тикер или даты")
                continue
            else:
                # plot and send picture
                if symb == "%5EGSPC":
                    symb = "S&P 500"
                plt.figure()
                tick.plot()
                plt.title(f"Динамика цены закрытия {symb}")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img = PIL.Image.open(buf)
                bot.send_photo(info.chat.id, img)
        # return first keyboard
        bot.send_message(info.chat.id, 'Чем ещё могу помочь?')
        send_keyboard(info, 'Выберите раздел')
    except:
        bot.send_message(info.chat.id, "Что-то пошло не так(")
        send_keyboard(info, 'Выберите раздел')


def send_prediction(info):
    images = []
    for symb in symbols:
        data = data_loader(symb, ['2020-01-01', datetime.date.today()])
        if data.empty:
            bot.send_message(info.chat.id, f"{symb} - некорректный тикер")
            continue
        else:
            pred_df = week_prediction(data)
            ts = data['adj close'].to_frame()
            if symb == "%5EGSPC":
                symb = "S&P 500"
            fig = plot_prediction(ts, pred_df, symb)
            images.append(fig)
    return images


def data_loader(symb, time_int):
    """collecting data of one ticker with given time interval"""
    p = data_collection(start_date=time_int[0], end_date=time_int[1])
    df = p.collect_yf_data(tickers=[symb]).set_index(keys='Date')[['Adj Close']]
    return df


bot.polling()
