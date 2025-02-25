import requests
import os
from dotenv import load_dotenv


load_dotenv()

# Ваш токен, полученный от BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANEL_ID = os.getenv("TELEGRAM_CHANEL_ID")

# URL API для бота
url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'


def send_message(message):
    """Функция для отправки сообщения от имени бота"""
    params = {
        'chat_id': TELEGRAM_CHANEL_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    requests.get(url + '/sendMessage', params=params)
