import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types
from io import BytesIO
import requests
import telebot
import random
import os

from constants import MOVIES, NEWS_URL, GENRE_MAPPING

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

user_data = {}

# /start
@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'watched': [], 'stats': {}}
    bot.send_message(
        message.chat.id,
        'Привіт! Я допоможу тобі знайти ідеальний фільм 🎬\n'
        'Обери команду:\n'
        '/recommend - отримати рекомендацію\n'
        '/new_movies - поради актуальних новинок\n'
        '/survey - пройти анкету для рекомендацій\n'
        '/stats - переглянути свою статистику'
    )

# /recommend
@bot.message_handler(commands=['recommend'])
def recommend(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for genre in MOVIES.keys():
        markup.add(genre)
    bot.send_message(
        message.chat.id,
        'Обери жанр, щоб отримати рекомендацію 🎥:',
        reply_markup=markup
    )
    bot.register_next_step_handler(message, recommend_movie)

def recommend_movie(message):
    genre = message.text
    if genre in MOVIES:
        movie = random.choice(MOVIES[genre])
        bot.send_message(
            message.chat.id,
            f'Рекомендую до перегляду: *{movie}* ({genre})',
            parse_mode='Markdown'
        )
        save_watched_movie(message.chat.id, genre, movie)
    else:
        bot.send_message(message.chat.id, 'Вибач, я не знаю такого жанру 😔')

# Collect data about watched films
def save_watched_movie(chat_id, genre, movie):
    user_data[chat_id]['watched'].append({'genre': genre, 'movie': movie})
    if genre in user_data[chat_id]['stats']:
        user_data[chat_id]['stats'][genre] += 1
    else:
        user_data[chat_id]['stats'][genre] = 1

# News
@bot.message_handler(commands=['new_movies'])
def new_movies(message):
    response = requests.get(NEWS_URL)
    new_movies_list = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        movie_blocks = soup.find_all('div', class_='item__data')
        
        for block in movie_blocks:
            try:
                name = block.find('div', class_='name').text.strip()
                genre = block.find('a', class_='info__item--genre').text.strip()
                
                genre = GENRE_MAPPING.get(genre, genre)
            
                new_movies_list.append({'name': name, 'genre': genre})
            except AttributeError:
                continue
    else:
        print(f'Error in request: {response.status_code}')
        return

    new_movies_list_sorted = sorted(new_movies_list, key=lambda x: x['genre'])
    formatted_list = "\n".join([f"🎬 *{movie['name']}* — _{movie['genre']}_" for movie in new_movies_list_sorted])

    bot.send_message(
        message.chat.id, 
        f"Список фильмов:\n\n{formatted_list}", 
        parse_mode="Markdown"
    )

# Survey
@bot.message_handler(commands=['survey'])
def survey(message):
    bot.send_message(message.chat.id, 'Як тебе звати?')
    bot.register_next_step_handler(message, survey_name)

def survey_name(message):
    user_data[message.chat.id]['name'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Комедії', 'Драми', 'Фантастика', 'Мультфільми')
    bot.send_message(
        message.chat.id,
        'Який твій улюблений жанр?',
        reply_markup=markup
    )
    bot.register_next_step_handler(message, survey_genre)

def survey_genre(message):
    user_data[message.chat.id]['favorite_genre'] = message.text
    bot.send_message(
        message.chat.id,
        f'Дякую за відповіді, {user_data[message.chat.id]['name']}! '
        f'Тепер я знаю, що твій улюблений жанр — {message.text}. 😊'
    )

# Statistics
@bot.message_handler(commands=['stats'])
def stats(message):
    stats_data = user_data.get(message.chat.id, {}).get('stats', {})
    if not stats_data:
        bot.send_message(message.chat.id, 'Немає даних для статистики 😔')
        return

    # Build a chart
    genres = list(stats_data.keys())
    counts = list(stats_data.values())

    plt.figure(figsize=(8, 6))
    plt.bar(genres, counts, color='skyblue')
    plt.xlabel('Жанри')
    plt.ylabel('Кількість переглядів')
    plt.title('Статистика переглянутих фільмів')

    # Save chart to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    bot.send_photo(message.chat.id, buf)

# Processing text
@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.send_message(
        message.chat.id,
        'Не розумію цю команду 😅. Спробуй /recommend або /stats!'
    )

# Launch bot
if __name__ == '__main__':
    print('Bot is running...')
    bot.infinity_polling()
