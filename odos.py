from web3 import Web3
from web3.middleware import geth_poa_middleware

import requests
import os
from dotenv import load_dotenv

from bnb_util import approve_token


load_dotenv()

# Подключение к BSC
web3_bsc = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
web3_bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

BSC_PRIVATE_KEY = os.getenv("BSC_PRIVATE_KEY")

account = web3_bsc.eth.account.from_key(BSC_PRIVATE_KEY)

CHAIN_ID = 56

# Адрес для нативного BNB
BNB_ODOS_NATIVE_ADDRESS = "0x0000000000000000000000000000000000000000"
ODOS_ROUTE_ADDRESS = "0x89b8AA89FDd0507a99d334CBe3C808fAFC7d850E"


def payload_quote(sell_token_address, buy_token_address, amount,
                  slippage_limit_percent=1.0):
    """Запрос к ODOS API"""
    url_quote = "https://api.odos.xyz/sor/quote/v2"
    payload_quote = {
        "chainId": CHAIN_ID,  # Chain ID для BSC
        "inputTokens": [
            {
                # Используем нулевой адрес для BNB
                "tokenAddress": sell_token_address,

                # Количество BNB в wei
                "amount": str(web3_bsc.to_wei(amount, "ether")),
            }
        ],
        "outputTokens": [
            {
                "tokenAddress": buy_token_address,  # Адрес выходного токена
                "proportion": 1.0,  # 100% выходного токена
            }
        ],
        "slippageLimitPercent": slippage_limit_percent,  # Проскальзывание 1%
        "userAddr": account.address,  # Адрес вашего кошелька
        "referralCode": 0,  # Реферальный код (если есть)
        "disableRFQs": False,  # Разрешить RFQ
        "compact": False,  # Использовать полный формат
    }
    headers = {"Content-Type": "application/json"}

    response_quote = requests.post(url_quote, json=payload_quote,
                                   headers=headers)
    return response_quote.json()


def payload_assemble(data_quote):

    if "pathId" not in data_quote:
        raise RuntimeError("Ошибка при получении pathId:", data_quote)

    path_id = data_quote["pathId"]

    # Запрос к `/sor/assemble`
    url_assemble = "https://api.odos.xyz/sor/assemble"
    payload_assemble = {
        "userAddr": account.address,
        "pathId": path_id,
        "simulate": False,
    }
    headers = {"Content-Type": "application/json"}

    response_assemble = requests.post(url_assemble, json=payload_assemble,
                                      headers=headers)
    return response_assemble.json()


def approve(token_address, amount):
    return approve_token(CHAIN_ID, token_address, ODOS_ROUTE_ADDRESS, amount)
