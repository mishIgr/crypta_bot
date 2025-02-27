import os
import time
import subprocess
from dotenv import load_dotenv

from send_transaction import buy_token_bsc, sell_half_tokens_bsc
from telegram_message import send_message


# Загружаем переменные окружения из файла .env
load_dotenv()

BEARER_TOKEN_COUNT = int(os.getenv("BEARER_TOKEN_COUNT"))

TIME_TO_SLEEP = 900 // BEARER_TOKEN_COUNT + 10

VENV_PYTHON = os.path.abspath("venv/bin/python")

CODE_MANY_REQuEST = int(os.getenv("CODE_MANY_REQuEST"))
CODE_SEND_TRANSACTION = int(os.getenv("CODE_SEND_TRANSACTION"))
CODE_UNIDENTIFIED = int(os.getenv("CODE_UNIDENTIFIED"))


def main():
    time.sleep(5)
    send_message(f"✅ Запуск, проверка каждые {TIME_TO_SLEEP / 60:.2f} мин")
    counter_id = 0
    while True:
        process = subprocess.run(
            [VENV_PYTHON, "check_twitter.py", "--id_token", str(counter_id)],
            capture_output=True, text=True
        )
        stderr = process.stderr

        if process.returncode == CODE_MANY_REQuEST:
            send_message(" Слишком много запросов! Ожидание 7.5 минут...")
            send_message(f"Консоль {stderr}")
            time.sleep(900 // 2)  # 15 / 2 минут паузы

        elif process.returncode == CODE_SEND_TRANSACTION:
            send_message(f"🥰 Найден контракт <code>{stderr}</code>\nteg: @$#_#$@")
            buy_token_bsc(stderr.strip(), 0.36)
            return

        elif process.returncode == CODE_UNIDENTIFIED:
            send_message(f"💀 Произошла неопознаная ошибка:\n {stderr}")
            time.sleep(TIME_TO_SLEEP)

        elif process.returncode == 0:
            if counter_id == 0:
                send_message("🔍 Твиты просмотрены")
            time.sleep(TIME_TO_SLEEP)

        counter_id = (counter_id + 1) % BEARER_TOKEN_COUNT


if __name__ == '__main__':
    main()
