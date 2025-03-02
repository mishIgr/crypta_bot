import os
import time
import random
import subprocess
from dotenv import load_dotenv

from send_transaction import buy_token_bsc
from telegram_message import send_message, send_teg, send_info_message
from Counter import Counter


# Загружаем переменные окружения из файла .env
load_dotenv()

BEARER_TOKEN_COUNT = int(os.getenv("BEARER_TOKEN_COUNT"))

VENV_PYTHON = os.path.abspath("venv/bin/python")

CODE_MANY_REQUEST = int(os.getenv("CODE_MANY_REQUEST"))
CODE_SEND_TRANSACTION = int(os.getenv("CODE_SEND_TRANSACTION"))
CODE_UNIDENTIFIED = int(os.getenv("CODE_UNIDENTIFIED"))

AMOUNT_BNB = 0.36

PERSON_X_IDS = {
    os.getenv("VEST_X_ID"): "VEST_X_ID",
    os.getenv("RONALD_X_ID"): "RONALD_X_ID",
    os.getenv("DAVE_VEST_X_ID"): "DAVE_VEST_X_ID"
}

TIME_TO_SLEEP = 1000 // BEARER_TOKEN_COUNT * len(PERSON_X_IDS)

buy_contract = set()


def make_transaction(contract):
    try:
        buy_token_bsc(contract, AMOUNT_BNB)
        return
    except Exception as e:
        send_message(str(e))
        time.sleep(20)

    try:
        buy_token_bsc(contract, AMOUNT_BNB - 0.03)
        return
    except Exception as e:
        send_message(str(e))
    return


def handler(process, person_id):
    stderr = process.stderr

    if process.returncode == CODE_MANY_REQUEST:
        send_message(" Слишком много запросов!")

    elif process.returncode == CODE_SEND_TRANSACTION:
        send_message(f"🥰 Найден контракт <code>{stderr}</code>")
        send_teg()
        contract = stderr.strip()

        if contract not in buy_contract:
            make_transaction(contract)

        buy_contract.add(contract)

    elif process.returncode == CODE_UNIDENTIFIED:
        send_message(("💀 Произошла неопознаная ошибка при работе"
                     f"с аккаунтом{PERSON_X_IDS[person_id]}:\n {stderr}"))


def main():
    time.sleep(5)
    send_message(f"✅ Запуск, проверка каждые {TIME_TO_SLEEP / 60:.2f} мин")
    counter_id = Counter(BEARER_TOKEN_COUNT)
    statuses = []
    stderrs = []
    while True:
        statuses = []
        stderrs = []
        for person_id in PERSON_X_IDS:
            process = subprocess.run(
                [VENV_PYTHON, "check_twitter.py",
                 "--id_token", counter_id.next_str(),
                 "--twitter_id", person_id],
                capture_output=True, text=True
            )
            handler(process, person_id)
            statuses.append(process.returncode)
            stderrs.append(process.stderr)

        if all(map(lambda s: s == 0, statuses)):
            send_info_message()

        print(f'{statuses=}')
        print(f'{stderrs=}')

        time.sleep(TIME_TO_SLEEP + random.randint(5, 10))


if __name__ == '__main__':
    main()
