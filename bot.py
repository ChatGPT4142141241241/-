# ml_helper_bot (Flask + pyTelegramBotAPI)

from flask import Flask, request
import telebot
import json
import os

# === CONFIG ===
BOT_TOKEN = '7822505947:AAF02J4Zq-EcylSvn24Nw9txsm-l4Z8e0KM'
ADMIN_ID = 6180147473

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === DATA FILES ===
USER_DATA_FILE = 'data/users.json'
SHOP_DATA_FILE = 'data/shop.json'
QUIZ_DATA_FILE = 'data/quiz.txt'

# === LOAD/INIT DATA ===
os.makedirs('data', exist_ok=True)
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump({}, f)

# === HELPERS ===
def load_users():
    with open(USER_DATA_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_or_create_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {'diamonds': 0, 'name': '', 'favs': []}
        save_users(users)
    return users[uid]

# === BOT HANDLERS ===
@bot.message_handler(commands=['start'])
def start(message):
    user = get_or_create_user(message.from_user.id)
    bot.send_message(message.chat.id, f"👋 Привет, {message.from_user.first_name}!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == '📦 Магазин')
def store(message):
    bot.send_message(message.chat.id, "🛍 Магазин пока в разработке. Будет топ!")

@bot.message_handler(func=lambda m: m.text == '📘 Гайды')
def guides(message):
    bot.send_message(message.chat.id, "🧠 Гайды скоро появятся здесь.")

@bot.message_handler(func=lambda m: m.text == '❓ Викторина')
def quiz(message):
    bot.send_message(message.chat.id, "🎯 Викторина будет доступна позже!")

@bot.message_handler(func=lambda m: m.text == '📚 Термины')
def terms(message):
    bot.send_message(message.chat.id, "📖 Здесь будут термины ML с пояснениями.")

@bot.message_handler(func=lambda m: m.text == '⚙️ Настройки')
def settings(message):
    user = get_or_create_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💎 Твои алмазы: {user['diamonds']}")

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ У тебя нет доступа.")
    bot.send_message(message.chat.id, "🔧 Админ-панель. Здесь ты можешь добавить предметы, награды и пр.")

# === MAIN MENU ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📦 Магазин', '📘 Гайды')
    markup.add('❓ Викторина', '📚 Термины')
    markup.add('⚙️ Настройки')
    return markup

# === FLASK HOOK ===
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "", 200

@app.route("/")
def index():
    return "👋 ML Helper Bot работает!"

# === WEBHOOK SETUP (для локального теста отключить) ===
import threading

def run_webhook():
    import time
    time.sleep(1)
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = f"https://ml-helper-bot.onrender.com/{BOT_TOKEN}"
    requests.get(url, params={'url': webhook_url})

threading.Thread(target=run_webhook).start()

# === RUN FLASK ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
