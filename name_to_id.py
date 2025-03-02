import os
import requests
from dotenv import load_dotenv


load_dotenv()

# Твой Bearer Token от Twitter API
BEARER_TOKEN = os.getenv(f"BEARER_TOKEN_{9}")


def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("id")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
        return None


# Пример вызова
username = "DaveTrent9"  # Имя пользователя в Twitter
user_id = get_user_id(username)
print(f"User ID: {user_id}")
