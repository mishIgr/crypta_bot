import tweepy
import os
import sys
import argparse
import re
from dotenv import load_dotenv


load_dotenv()

parser = argparse.ArgumentParser(description="Пример аргументов")
parser.add_argument("--id_token", type=int, required=True, help="id токена \
                    для работы  с X api")

args = parser.parse_args()

BEARER_TOKEN = os.getenv(f"BEARER_TOKEN_{args.id_token}")

if BEARER_TOKEN is None:
    raise ValueError(f'Токен с id {args.id_token} не найден.')

client = tweepy.Client(bearer_token=BEARER_TOKEN)

VEST_X_ID = os.getenv("VEST_X_ID")
MIKHAIL_X_ID = os.getenv("MIKHAIL_X_ID")

# Регулярные выражения для контрактов
patterns = {
    "BSC": r"0x[a-fA-F0-9]{40}",  # Адреса Binance Smart Chain
}

CODE_MANY_REQuEST = int(os.getenv("CODE_MANY_REQuEST"))
CODE_SEND_TRANSACTION = int(os.getenv("CODE_SEND_TRANSACTION"))
CODE_UNIDENTIFIED = int(os.getenv("CODE_UNIDENTIFIED"))


def find_contracts(text):
    """Функция для поиска контрактов"""
    found = {}
    for network, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            found[network] = matches
    return found


def get_latest_posts_and_buy(user_id):
    """Получаем последние посты и совершаем покупки"""
    try:
        # Получаем твиты пользователя с помощью API v2
        response = client.get_users_tweets(user_id)

        if not response.data:
            return

        for tweet in response.data:
            contracts = find_contracts(tweet.text)
            if contracts:
                for network, addresses in contracts.items():
                    for address in addresses:
                        if network == "BSC":
                            print(address, file=sys.stderr)
                            sys.exit(CODE_SEND_TRANSACTION)

    except tweepy.TooManyRequests as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(CODE_MANY_REQuEST)

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(CODE_UNIDENTIFIED)


get_latest_posts_and_buy(int(VEST_X_ID))
