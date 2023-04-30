# -*- coding: utf-8 -*-
# бот-помощник для списка общих покупок.

import os
import pickle
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# список идентификаторов пользователей, которые могут использовать бота
ALLOWED_USERS = [831617436, 416541312]

# имя файла для хранения списка покупок
PICKLE_FILENAME = 'purchases.pickle'

# базовая функция для отправки сообщения
def send_message(update, text, reply_markup=None):
    show_purchases_button = InlineKeyboardButton("Показать список покупок", callback_data='show_purchases')
    if reply_markup:
        reply_markup.inline_keyboard.append([show_purchases_button])
    else:
        reply_markup = InlineKeyboardMarkup([[show_purchases_button]])
    update.message.reply_text(text, reply_markup=reply_markup)

# загрузка списка покупок из файла
def load_purchases():
    if not os.path.exists(PICKLE_FILENAME):
        return []
    with open(PICKLE_FILENAME, 'rb') as f:
        return pickle.load(f)

# сохранение списка покупок в файл    
def save_purchases(purchases):
    with open(PICKLE_FILENAME, 'wb') as f:
        pickle.dump(purchases, f)

# список для хранения покупок
purchases_list = load_purchases()

# обработчик команды /start
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Добавить покупку", callback_data='add_purchase')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    send_message(update, 'Привет! Я бот для списка покупок. Выбери, что хочешь сделать:', reply_markup)

# обработчик команды /add_purchase
def add_purchase_callback(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['adding_purchase'] = True
    send_message(query, 'Напиши мне название покупки:')

def add_purchase(update, context):
    global purchases_list
    # проверяем идентификатор пользователя
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        send_message(update, 'Извините, вы не можете использовать эту команду.')
        return
    # получаем текст сообщения пользователя
    purchase = update.message.text.lower() # приведение к строчным
    if purchase in [p.lower() for p in purchases_list]: # проверка на дублирование
        send_message(update, f'Покупка "{purchase}" уже существует в списке.')
    else:
        # добавляем покупку в список
        purchases_list.append(purchase)
        # сохраняем список покупок в файл
        save_purchases([p.title() for p in purchases_list]) # запись с заглавной
        # отправляем подтверждение пользователю
        send_message(update, f'Покупка "{purchase}" добавлена в список.')

# обработчик команды /purchases
def show_purchases_callback(update, context):
    query = update.callback_query
    query.answer()
    reply_markup = None
    if purchases_list:
        keyboard = [[InlineKeyboardButton(p, callback_data=f'delete_purchase|{i}')] + [InlineKeyboardButton("❌", callback_data=f'delete_purchase|{i}')] for i, p in enumerate(purchases_list)]
        keyboard.append([InlineKeyboardButton("❌ Удалить все покупки", callback_data='clear_purchases')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        purchases_text = '\n'.join(purchases_list)
    else:
        purchases_text = 'Список покупок пуст.'
    send_message(query, f'Список покупок:\n{purchases_text}', reply_markup)

def delete_purchase_callback(update, context):
    query = update.callback_query
    query.answer()
    index = int(query.data.split('|')[1])
    global purchases_list
    del purchases_list[index]
    save_purchases(purchases_list)
    send_message(query, f'Покупка удалена из списка.')

def clear_purchases_callback(update, context):
    query = update.callback_query
    query.answer()
    global purchases_list
    purchases_list = []
    save_purchases(purchases_list)
    send_message(query, 'Список покупок очищен.')

# создаем экземпляр бота    
updater = Updater(token=open('token1.txt', 'r').read().strip(), use_context=True)
# получаем диспетчер для регистрации обработчиков
dispatcher = updater.dispatcher
# регистрируем обработчик команды /start
dispatcher.add_handler(CommandHandler('start', start))
# регистрируем обработчик команды /add_purchase
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_purchase))
# регистрируем обработчик команды /purchases
dispatcher.add_handler(CallbackQueryHandler(show_purchases_callback, pattern='show_purchases'))
dispatcher.add_handler(CallbackQueryHandler(delete_purchase_callback, pattern='delete_purchase'))
dispatcher.add_handler(CallbackQueryHandler(clear_purchases_callback, pattern='clear_purchases'))

# запускаем бота
updater.start_polling()
updater.idle()