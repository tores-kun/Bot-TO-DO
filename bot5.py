# -*- coding: utf-8 -*-
# бот-помощник для списка индивидуальных дел

import sqlite3
import telebot
from telebot import types

# создаем подключение к базе данных
conn = sqlite3.connect('tasks1.db', check_same_thread=False)
cursor = conn.cursor()

# создаем таблицу tasks
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER NOT NULL,
               task_text TEXT NOT NULL)''')
conn.commit()

bot = telebot.TeleBot(token=open('token.txt', 'r').read().strip())

allowed_users = ['831617436','416541312']

@bot.message_handler(commands=['start'])
def start_command(message):
    if str(message.from_user.id) in allowed_users:
        bot.send_message(message.chat.id, "Привет, я бот-помощник для списка индивидуальных дел. Чтобы добавить задачу, напиши ее текст. Используйте команду /help вывода всех команд.")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(commands=['list'])
def list_tasks(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        cursor.execute("SELECT task_text FROM tasks WHERE user_id=?", (user_id,))
        task_rows = cursor.fetchall()
        if task_rows:
            task_list = '\n'.join([row[0] for row in task_rows])
            bot.send_message(user_id, f"Ваши задачи:\n{task_list}")
        else:
            bot.send_message(user_id, "У вас пока нет задач")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(commands=['done'])
def task_done(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        cursor.execute("SELECT task_text FROM tasks WHERE user_id=?", (user_id,))
        task_rows = cursor.fetchall()
        if task_rows:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(*[row[0] for row in task_rows])
            msg = bot.send_message(user_id, "Выберите задачу, которую хотите отметить как выполненную", reply_markup=markup)
            bot.register_next_step_handler(msg, task_done_callback)
        else:
            bot.send_message(user_id, "У вас пока нет задач")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help_command(message):
    if str(message.from_user.id) in allowed_users:
        help_text = "/start - Начать работу с ботом\n" \
                    "/list - Показать список задач\n" \
                    "/done - Отметить задачу как выполненную\n"
        bot.send_message(message.chat.id, help_text)
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

def task_done_callback(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        task_text = message.text
        cursor.execute("DELETE FROM tasks WHERE user_id=? AND task_text=?", (user_id, task_text))
        conn.commit()
        bot.send_message(user_id, f"Задание '{task_text}' отмечено как выполненное")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(content_types=['text'])
def add_task(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        task_text = message.text
        cursor.execute("INSERT INTO tasks (user_id, task_text) VALUES (?, ?)", (user_id, task_text))
        conn.commit()
        bot.send_message(user_id, f"Добавлено задание: {task_text}")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if str(message.from_user.id) in allowed_users:
        bot.send_message(message.chat.id, "Извините, я не понимаю эту команду. Для начала работы напишите /start")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

bot.polling()