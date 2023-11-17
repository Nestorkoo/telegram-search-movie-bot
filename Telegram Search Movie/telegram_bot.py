
import json
import random

import requests
from googletrans import Translator
from PIL import Image

import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.token)

genre_translations = {
    'Action': 'Екшн, Бойовик',
    'Adventure': 'Пригоди',
    'Animation': 'Анімація',
    'Comedy': 'Комедія',
    'Crime': 'Кримінал',
    'Documentary': 'Документальний',
    'Drama': 'Драма',
    'Family': 'Сімейний',
    'Fantasy': 'Фентезі',
    'History': 'Історичний',
    'Horror': 'Жахи, Хоррор',
    'Music': 'Музичний',
    'Mystery': 'Таємниця, Містика',
    'Romance': 'Романтика',
    'Science Fiction': 'Наукова фантастика',
    'Thriller': 'Трилер',
    'War': 'Воєнний',
    'Western': 'Вестерн'
}


@bot.message_handler(commands=['start'])
def test(message):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('🎬 Кіно')
    item2 = types.KeyboardButton('🔍 Знайди фільм')
    
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Привіт, {0.first_name} {0.last_name}!'.format(message.from_user, parse_mode='html'), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def first(message):
    if message.chat.type == 'private':
        if message.text == '🎬 Кіно':
            msg = bot.send_message(message.chat.id, 'Напишіть назву фільму')
            bot.register_next_step_handler(msg, process_film_name)
        if message.text == '🔍 Знайди фільм':
            msg = bot.send_message(message.chat.id, 'Напиши жанри які ти хочеш бачити у фільмі :)')
            bot.register_next_step_handler(msg, second_mode)
        


def process_film_name(message):
    film_name = message.text
    print(film_name)

    url_for_id = f"https://api.themoviedb.org/3/search/movie?query={film_name}&include_adult=true&language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZGM4ZWZlNDRmNWMxMWU5OWMyNzgxNjllODQxOTgzYSIsInN1YiI6IjY0OTQ2N2I5YWY2ZTk0MDBhZGVjN2FmYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.mKKqzs-Sov5bkqyNpO6Zbc2WyKgQfwQUdbbwFgad6GA"
    }
    response_id = requests.get(url_for_id, headers=headers)
    data = response_id.json()

    if 'results' in data and len(data['results']) > 0:
        first_movie = data['results'][0]
        id_film = first_movie['id']

        url = f"https://api.themoviedb.org/3/movie/{id_film}?language=en-US"
        response_photo = requests.get(url, headers=headers)
        data = response_photo.json()
        imagename = data['poster_path']
        image_url = f"https://image.tmdb.org/t/p/original{imagename}"
        image_response = requests.get(image_url)
        image_data = image_response.content
        with open("poster.jpg", "wb") as image_file:
            image_file.write(image_data)

        genres = [genre_translations[genre['name']] for genre in data['genres']]
        genres_str = ', '.join(genre for genre in genres if genre)

        # Оригінальна назва фільму
        original_title = data['original_title']

        bot.send_photo(message.chat.id, open('poster.jpg', 'rb'), caption=f'Назва: {original_title}\nID: {id_film}\nЖанр: {genres_str}')
    else:
        bot.send_message(message.chat.id, 'Фільм не знайдено!')

def second_mode(message):
    source_lang = 'uk'
    target_lang = 'en'
    genre_film_ua = message.text
    translator = Translator()
    translation = translator.translate(genre_film_ua, src=source_lang, dest=target_lang)
    translated_word = translation.text
    
    wrong_word = {
        'Ekhn': 'Action',
        'militant': 'Action',
        'choir': 'Horror',
        'Musical': 'Music',
        'Mysticism': 'Mystery',
        'Sci-fi': 'Science Fiction',
        'Military': 'War',
        'Historical': 'History'
    }

    if translated_word in wrong_word:
        translated_word = wrong_word[translated_word]


    API_KEY = '8dc8efe44f5c11e99c278169e841983a'

    def get_genre_id(genre_name):
        endpoint = f'https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}'
        response = requests.get(endpoint)

        if response.status_code == 200:
            genres = response.json()['genres']
            for genre in genres:
                if genre['name'].lower() == genre_name.lower():
                    return genre['id']

        return None

    genre_names = translated_word
    genres = [genre.strip() for genre in genre_names.split(',')]

    not_found_genres = []
    found_genres = {}

    for genre_name in genres:
        genre_id = get_genre_id(genre_name)
        if genre_id is not None:
            found_genres[genre_name] = genre_id
        else:
            not_found_genres.append(genre_name)

    


    def search_movies_by_genre(api_key, genre_id):
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            movies = data['results']
            return movies
        else:
            return None

    api_key = '8dc8efe44f5c11e99c278169e841983a'

    genre_id = genre_id

    movies = search_movies_by_genre(api_key, genre_id)

    if movies is not None:
        for movie in movies:
            bot.send_message(message.chat.id,movie['title'])
    else:
        bot.send_message(message.chat.id, "Помилка під час пошуку фільмів.")


bot.polling(none_stop=True)




