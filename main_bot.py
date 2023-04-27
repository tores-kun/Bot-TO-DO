# -*- coding: utf-8 -*-
# бот-помощник для списка общих дел

import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot(token=open('token.txt', 'r').read().strip())

# Инициализация базы данных
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY, task TEXT)''')
conn.commit()

allowed_users = ['831617436','416541312']

@bot.message_handler(commands=['start'])
def start_command(message):
    if str(message.from_user.id) in allowed_users:
        bot.send_message(message.chat.id, "Привет, я бот-помощник для списка дел. Чтобы добавить задачу, напиши ее текст. Используйте команду /help вывода всех команд.")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(commands=['list'])
def list_tasks(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        c.execute("SELECT task FROM tasks")
        tasks_list = c.fetchall()
        if tasks_list:
            tasks_text = [task[0] for task in tasks_list]
            task_list = '\n'.join(tasks_text)
            bot.send_message(user_id, f"Ваши задачи:\n{task_list}")
        else:
            bot.send_message(user_id, "У вас пока нет задач")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(commands=['done'])
def task_done(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        c.execute("SELECT task FROM tasks")
        tasks_list = c.fetchall()
        if tasks_list:
            tasks_text = [task[0] for task in tasks_list]
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(*tasks_text)
            msg = bot.send_message(user_id, "Выберите задачу, которую хотите отметить как выполненную", reply_markup=markup)
            bot.register_next_step_handler(msg, task_done_callback)
        else:
            bot.send_message(user_id, "У вас пока нет задач")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту")

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

@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    if str(message.from_user.id) in allowed_users:
        c.execute("DELETE FROM tasks")
        conn.commit()
        c.close()
        conn.close()
        bot.send_message(message.chat.id, "Список задач очищен.")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

def task_done_callback(message):
    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        task_text = message.text
        c.execute("DELETE FROM tasks WHERE task=?", (task_text,))
        conn.commit()
        bot.send_message(user_id, f"Задание '{task_text}' отмечено как выполненное")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(content_types=['text'])
def add_task(message):

    if str(message.from_user.id) in allowed_users:
        user_id = message.chat.id
        task_text = message.text
        c.execute("SELECT id FROM tasks WHERE task=?", (task_text,))
        if not c.fetchone():
            c.execute("INSERT INTO tasks (task) VALUES (?)", (task_text,))
            conn.commit()
            bot.send_message(user_id, f"Добавлено задание: {task_text}")
        else:
            bot.send_message(user_id, "Задача уже существует")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if str(message.from_user.id) in allowed_users:
        bot.send_message(message.chat.id, "Извините, я не понимаю эту команду. Для начала работы напишите /start")
    else:
        bot.reply_to(message, "У вас нет доступа к этому боту.")

bot.polling()
