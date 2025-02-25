from dotenv import load_dotenv

from send_transaction import sell_half_tokens_bsc


# Загружаем переменные окружения из файла .env
load_dotenv()

contract = ''

sell_half_tokens_bsc(contract)
