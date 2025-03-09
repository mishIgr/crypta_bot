from web3 import Web3
from web3.middleware import geth_poa_middleware

import os
from dotenv import load_dotenv

from odos import approve, payload_assemble, payload_quote, \
    BNB_ODOS_NATIVE_ADDRESS
from bnb_util import check_bsc_transaction


load_dotenv()

# Blockchain Setup
BSC_RPC_URL = "https://bsc-dataseed.binance.org/"

# Подключение к блокчейну
web3_bsc = Web3(Web3.HTTPProvider(BSC_RPC_URL))
web3_bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

# Ключи кошельков (замени своими!)
BSC_PRIVATE_KEY = os.getenv("BSC_PRIVATE_KEY")


def create_transaction(data_assemble):
    if "transaction" not in data_assemble:
        raise RuntimeError("Ошибка при получении данных для транзакции:",
                           data_assemble)

    transaction_data = data_assemble["transaction"]

    # Подготовка транзакции
    tx = {
        "to": transaction_data["to"],
        "data": transaction_data["data"],
        "value": int(transaction_data["value"]),
        "gas": int(transaction_data["gas"]),
        "gasPrice": int(transaction_data["gasPrice"]),
        "nonce": int(transaction_data["nonce"]),
        "chainId": int(transaction_data["chainId"]),
    }

    # Подписание транзакции
    signed_tx = web3_bsc.eth.account.sign_transaction(tx, BSC_PRIVATE_KEY)

    # Отправка транзакции
    txn_hash = web3_bsc.eth.send_raw_transaction(signed_tx.raw_transaction)
    return txn_hash


def buy_token_bsc(contract_address, amount_bnb, slippage_limit_percent=1.0):
    """Функция покупки токена на BSC через ODOS Router"""

    data_quote = payload_quote(BNB_ODOS_NATIVE_ADDRESS, contract_address,
                               amount_bnb, slippage_limit_percent)

    data_assemble = payload_assemble(data_quote)

    return create_transaction(data_assemble)


def sell_token_bsc(contract_address, amount_token, slippage_limit_percent=1.0):
    """Функция покупки токена на BSC через ODOS Router"""

    approve_tx_hash = approve(contract_address, amount_token)
    print(check_bsc_transaction(approve_tx_hash))

    data_quote = payload_quote(contract_address, BNB_ODOS_NATIVE_ADDRESS,
                               amount_token, slippage_limit_percent)

    data_assemble = payload_assemble(data_quote)

    return create_transaction(data_assemble)
