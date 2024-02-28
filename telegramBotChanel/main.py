import telebot
import schedule
import time
from telebot import types
import json
import random

TOKEN = '6871683373:AAGKA6SKFp-99GvoNIQNcsUCJv2JkxX2MDE'
CHANNEL_NAME = '-1002094781489'
bot = telebot.TeleBot(TOKEN)

def load_posts_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

posts = load_posts_from_json('posts.json')

def send_post():
    if not posts:
        print("No more posts to send.")
        return
    post = posts.pop(0)
    posts.append(post)  # Переміщуємо пост в кінець списку для циклічної відправки
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Перейти", url="https://t.me/your_username")
    markup.add(button)

    if post['type'] == 'text':
        bot.send_message(CHANNEL_NAME, post['text'], reply_markup=markup)
    elif post['type'] == 'image':
        if len(post['images']) > 1:
            media = [types.InputMediaPhoto(open(img, 'rb'), caption=(post['text'] if i == 0 else "")) for i, img in enumerate(post['images'])]
            bot.send_media_group(CHANNEL_NAME, media)
        else:
            with open(post['images'][0], 'rb') as photo:
                bot.send_photo(CHANNEL_NAME, photo, caption=post.get('text', ''), reply_markup=markup)
    elif post['type'] == 'video':
        with open(post['video'], 'rb') as video:
            bot.send_video_note(CHANNEL_NAME, video)
            bot.send_message(CHANNEL_NAME, "НАПИШИ МНЕ \U0001F44B", reply_markup=markup)
    elif post['type'] == 'audio':
        with open(post['audio'], 'rb') as audio:
            bot.send_audio(CHANNEL_NAME, audio, reply_markup=markup)

# Налаштовуємо графік відправлення
def send_poll():
    question = "Кто заработал ?"
    options = ['Я', 'Я еще думаю']
    bot.send_poll(CHANNEL_NAME, question, options, is_anonymous=True)

def schedule_posts():
    schedule.every().day.at("08:00").do(send_poll)  # Для опитування
    schedule.every().day.at("07:00").do(send_post)  # Перше повідомлення
    for hour in range(9, 21, 2):  # Наступні повідомлення
        schedule_time = f"{hour:02d}:00"
        schedule.every().day.at(schedule_time).do(send_post)

schedule_posts()

while True:
    schedule.run_pending()
    time.sleep(1)