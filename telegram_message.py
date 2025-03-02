import requests
import os
from dotenv import load_dotenv


load_dotenv()

# Ваш токен, полученный от BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANEL_ID = os.getenv("TELEGRAM_CHANEL_ID")

TEG_MESSAGE_CHAT_ID = os.getenv("TEG_MESSAGE_CHAT_ID")

# URL API для бота
url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'


def send_message(message, chat_id=TELEGRAM_CHANEL_ID):
    """Функция для отправки сообщения от имени бота"""
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    response = requests.get(f'{url}/sendMessage', params=params)
    return response.json()


def send_teg():
    """Отправляет тег"""
    return send_message('teg: wakeywakey', chat_id=TEG_MESSAGE_CHAT_ID)


def delete_message(chat_id, message_id):
    """Удаляет сообщение по message_id"""
    params = {
        'chat_id': chat_id,
        'message_id': message_id
    }

    response = requests.get(f'{url}/deleteMessage', params=params)
    return response.json()


last_info_message_id = None


def send_info_message():
    """Отправить информационное сообщение"""

    global last_info_message_id

    if last_info_message_id:
        delete_message(TELEGRAM_CHANEL_ID, last_info_message_id)
        last_info_message_id = None

    data = send_message('🔍 Твиты просмотрены')

    if data.get("ok"):
        last_info_message_id = data["result"]["message_id"]
