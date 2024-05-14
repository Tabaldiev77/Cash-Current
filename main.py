# токен бота : 6911034530:AAEdU7eG7Kl9ZHjj_AnTDorcw44hg7yBFyQ

import telebot
from telebot import types
import sqlite3
from currency_converter import CurrencyConverter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io

bot = telebot.TeleBot('6911034530:AAEdU7eG7Kl9ZHjj_AnTDorcw44hg7yBFyQ')

# Create the 'transactions' table if it doesn't exist
conn = sqlite3.connect('finance_bot.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL
                  )''')
conn.commit()
conn.close()

currency = CurrencyConverter()

markup = types.InlineKeyboardMarkup()
btn1 = types.InlineKeyboardButton(text='Расходы', callback_data='expenses')
btn2 = types.InlineKeyboardButton(text='Доходы', callback_data='income')
btn3 = types.InlineKeyboardButton(text='Статистика', callback_data='statistics')
btn4 = types.InlineKeyboardButton(text='Курс Валюты', callback_data='exchange_rates')
markup.add(btn1, btn2, btn3, btn4)
button = types.KeyboardButton('Главная меню')
button3 = types.ReplyKeyboardMarkup(resize_keyboard=True)
button3.add(button)

@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    if callback.data == 'expenses':
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Добавить расходы', callback_data='add_expense')
        keyboard.add(button1)
        button2 = types.InlineKeyboardButton(text='Отменить последнюю транзакцию', callback_data='cancel_last_transaction')
        keyboard.add(button2)
        bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=keyboard)
        bot.send_message(callback.message.chat.id, 'Для возвращения в главное меню нажмите на кнопку ниже', reply_markup=button3)
    elif callback.data == 'income':
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Добавить доходы', callback_data='add_income')
        keyboard.add(button1)
        button2 = types.InlineKeyboardButton(text='Отменить последнюю транзакцию', callback_data='cancel_last_transaction')
        keyboard.add(button2)
        bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=keyboard)
        bot.send_message(callback.message.chat.id, 'Для возвращения в главное меню нажмите на кнопку ниже', reply_markup=button3)
    elif callback.data == 'add_expense':
        bot.send_message(callback.message.chat.id, "Введите сумму расхода:")
        bot.register_next_step_handler(callback.message, process_expense)
    elif callback.data == 'add_income':
        bot.send_message(callback.message.chat.id, "Введите сумму дохода:")
        bot.register_next_step_handler(callback.message, process_income)
    elif callback.data == 'cancel_last_transaction':
        cancel_last_transaction(callback.message, cursor, conn, bot)
    elif callback.data == 'statistics':
        bot.send_message(callback.message.chat.id, 'Для возвращения в главное меню нажмите на кнопку ниже',
                         reply_markup=button3)
        bot.register_next_step_handler(callback.message, send_statistics)
    elif callback.data == 'exchange_rates':
        bot.send_message(callback.message.chat.id, 'Это конвертер валют, '
                                                   'который использует исторические курсы '
                                                   'по отношению к базовой валюте (евро). '
                                                   'Введите сумму')
        bot.register_next_step_handler(callback.message, conversion_amount)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'CashCurrent: Учет Финансов в Твоих Руках**: Отслеживайте свои расходы и доходы, а также получайте статистику и информацию о курсах валют - все это с CashCurrent. Чтобы начать, просто выберите из одной команды: «Расходы», «Доходы», «Статистика» или «Курс валют', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Главная меню')
def main_menu(message):
    bot.send_message(message.chat.id, 'CashCurrent: Учет Финансов в Твоих Руках**: Отслеживайте свои расходы и доходы, а также получайте статистику и информацию о курсах валют - все это с CashCurrent. Чтобы начать, просто выберите из одной команды: «Расходы», «Доходы», «Статистика» или «Курс валют', reply_markup=markup)

def check_and_notify_balance(message):
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    total_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    total_expenses = cursor.fetchone()[0] or 0
    balance = total_income - total_expenses
    conn.close()

    if balance <= 0:
        bot.send_message(message.chat.id, "Внимание! Ваш баланс заканчивается.")

def process_expense(message):
    try:
        amount = float(message.text)
        conn = sqlite3.connect('finance_bot.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", ('expense', amount))
        conn.commit()
        bot.send_message(message.chat.id, f"Расход на сумму {amount} добавлен.")
        check_and_notify_balance(message)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите числовое значение для суммы расхода.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении расхода: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def process_income(message):
    try:
        amount = float(message.text)
        conn = sqlite3.connect('finance_bot.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", ('income', amount))
        conn.commit()
        bot.send_message(message.chat.id, f"Доход на сумму {amount} добавлен.")
        check_and_notify_balance(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при добавлении дохода. Пожалуйста, укажите сумму.")
    finally:
        cursor.close()
        conn.close()

def cancel_last_transaction(message, cursor, conn, bot):
    try:
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1")
        last_transaction = cursor.fetchone()

        if last_transaction:
            transaction_id, transaction_type, amount = last_transaction
            cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"Последняя транзакция ({transaction_type} на сумму {amount}) отменена.")
        else:
            bot.send_message(message.chat.id, "Нет транзакций для отмены.")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка отмены последней транзакции.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_statistics():
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    total_expenses = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    total_income = cursor.fetchone()[0] or 0
    conn.close()

    months = ['January', 'February', 'March', 'April', 'May']

    plt.plot(months, [total_expenses] * len(months), marker='o', label='Расходы')
    plt.plot(months, [total_income] * len(months), marker='o', label='Доходы')

    plt.xlabel('Месяц')
    plt.ylabel('Сумма ($)')
    plt.title('Статистика расходов и доходов')
    plt.legend()
    plt.xticks(rotation=45)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    return img_buffer

def send_statistics(message):
    img_buffer = get_statistics()
    bot.send_photo(message.chat.id, img_buffer)

def conversion_amount(message):
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат. Введите сумму')
        bot.register_next_step_handler(message, conversion_amount)

    if amount > 0:
        mark = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text='Главное меню', callback_data='home')
        mark.add(btn)
        bot.send_message(message.chat.id, 'Введите пару валют через /', reply_markup=mark)
        bot.register_next_step_handler(message, my_conversion)
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше нуля')
        bot.register_next_step_handler(message, conversion_amount)

def my_conversion(message):
    try:
        values = message.text.upper().split('/')
        num = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'{amount} равно: {round(num, 2)}. Можете ввести число заново')
        bot.register_next_step_handler(message, conversion_amount)
    except Exception:
        bot.send_message(message.chat.id, 'Введите заново')
        bot.register_next_step_handler(message, my_conversion)

bot.polling(non_stop=True)

#
import telebot
from telebot import types
import sqlite3
from currency_converter import CurrencyConverter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io


bot = telebot.TeleBot('6911034530:AAEdU7eG7Kl9ZHjj_AnTDorcw44hg7yBFyQ')

currency = CurrencyConverter()
amount = 0

markup = types.InlineKeyboardMarkup()
btn1 = types.InlineKeyboardButton(text='Расходы', callback_data='expenses')
btn2 = types.InlineKeyboardButton(text='Доходы', callback_data='income')
btn3 = types.InlineKeyboardButton(text='Статистика', callback_data='statistics')
btn4 = types.InlineKeyboardButton(text='Курс Валюты', callback_data='exchange_rates')
markup.add(btn1, btn2, btn3, btn4)
button = types.KeyboardButton('Главная меню')
button3 = types.ReplyKeyboardMarkup(resize_keyboard=True)
button3.add(button)


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    if callback.data == 'expenses':
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Добавить расходы', callback_data='add_expense')
        keyboard.add(button1)
        button2 = types.InlineKeyboardButton(text='Отменить последнюю транзакцию', callback_data='cancel_last_transaction')
        keyboard.add(button2)
        bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=keyboard)
        bot.send_message(callback.message.chat.id, 'Для возвращение в главная меню нажмите на кнопку ниже', reply_markup=button3)
    elif callback.data == 'income':
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Добавить доходы', callback_data='add_income')
        keyboard.add(button1)
        button2 = types.InlineKeyboardButton(text='Отменить последнюю транзакцию', callback_data='cancel_last_transaction')
        keyboard.add(button2)
        bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=keyboard)
        bot.send_message(callback.message.chat.id, 'Для возвращение в главная меню нажмите на кнопку ниже', reply_markup=button3)
    elif callback.data == 'add_expense':
        bot.send_message(callback.message.chat.id, "Введите сумму расхода:")
        bot.register_next_step_handler(callback.message, process_expense)
    elif callback.data == 'add_income':
        bot.send_message(callback.message.chat.id, "Введите сумму дохода:")
        bot.register_next_step_handler(callback.message, process_income)
    elif callback.data == 'cancel_last_transaction':
        cancel_last_transaction(callback.message, cursor, conn, bot)
    elif callback.data == 'statistics':
        bot.send_message(callback.message.chat.id, 'Для возвращение в главная меню нажмите на кнопку ниже',
                         reply_markup=button3)
        bot.register_next_step_handler(callback.message, send_statistics)
    elif callback.data == 'exchange_rates':
        bot.send_message(callback.message.chat.id, 'Это конвертер валют, '
                                                   'который использует исторические курсы '
                                                   'по отношению к базовой валюте (евро). '
                                                   'Введите сумму')
        bot.register_next_step_handler(callback.message, conversion_amount)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет я твой виртуальный помощник по считыванию денег✋', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Главная меню')
def main_menu(message):
    bot.send_message(message.chat.id, 'Привет я твой виртуальный помощник по считыванию денег✋', reply_markup=markup)


def check_balance(message):
    conn = sqlite3.connect('expenses_income.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    total_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    total_expenses = cursor.fetchone()[0] or 0
    balance = total_income - total_expenses
    conn.close()

    if balance <= 0:
        bot.send_message(message.chat.id, "Внимание! Ваш баланс заканчивается.")


def process_expense(message):
    try:
        amount = float(message.text)
        conn = sqlite3.connect('finance_bot.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", ('expense', amount))
        conn.commit()
        bot.send_message(message.chat.id, f"Расход на сумму {amount} добавлен.")
        check_balance(message)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите числовое значение для суммы расхода.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении расхода: {str(e)}")
    finally:
        cursor.close()
        conn.close()



def process_income(message):
    try:
        amount = float(message.text)
        conn = sqlite3.connect('finance_bot.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", ('income', amount))
        conn.commit()
        bot.send_message(message.chat.id, f"Доход на сумму {amount} добавлен.")
        check_balance(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при добавлении дохода. Пожалуйста, укажите сумму.")
    finally:
        cursor.close()
        conn.close()


def cancel_last_transaction(message, cursor, conn, bot):
    try:
        # Check if the last transaction exists
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1")
        last_transaction = cursor.fetchone()

        if last_transaction:
            transaction_id, transaction_type, amount = last_transaction
            cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
            conn.commit()  # Commit changes to the database
            bot.send_message(message.chat.id, f"Последняя транзакция ({transaction_type} за сумму {amount}) отменена.")
        else:
            bot.send_message(message.chat.id, "Нет транзакций для отмены.")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка отмены последней транзакции..")
    finally:
        # Close cursor
        if cursor:
            cursor.close()
        # Close connection
        if conn:
            conn.close()


def get_statistics():
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    total_expenses = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    total_income = cursor.fetchone()[0] or 0
    conn.close()

    months = ['January', 'February', 'March', 'April', 'May']

    # Create a line plot for expenditure
    plt.plot(months, [total_expenses] * len(months), marker='o', label='Expenditure')

    # Create a line plot for income
    plt.plot(months, [total_income] * len(months), marker='o', label='Income')

    # Add labels and title
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.title('Expenditure and Income Statistics')
    plt.legend()  # Show legend

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Save the plot as a BytesIO object
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    # Return the BytesIO object containing the image data
    return img_buffer


def send_statistics(message):
    img_buffer = get_statistics()
    bot.send_photo(message.chat.id, img_buffer)


def conversion_amount(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Не верный формат. Введите сумму')
        bot.register_next_step_handler(message, conversion_amount)

    if amount > 0:
        mark = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text='Главное меню', callback_data='home')
        mark.add(btn)
        bot.send_message(message.chat.id, 'Введите пару валют через /', reply_markup=mark)
        bot.register_next_step_handler(message, my_conversion)
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше нуля')
        bot.register_next_step_handler(message, conversion_amount)


def my_conversion(message):
    try:
        values = message.text.upper().split('/')
        num = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'{amount} выходить: {round(num, 2)}. Можете заново вводить число')
        bot.register_next_step_handler(message, conversion_amount)
    except Exception:
        bot.send_message(message.chat.id, 'Вводите заново')
        bot.register_next_step_handler(message, my_conversion)


bot.polling(non_stop=True)