from web3 import Web3
import requests
import os
import json
from dotenv import load_dotenv


load_dotenv()

# Подключение к BSC
web3_bsc = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
BSC_PRIVATE_KEY = os.getenv("BSC_PRIVATE_KEY")
account = web3_bsc.eth.account.from_key(BSC_PRIVATE_KEY)
BSC_SCAN_API_KEY = os.getenv("BSC_SCAN_API_KEY")

URL_BNB_SCAN_API = "https://api.bscscan.com/api"


def hash_to_hex(tx_hash):
    return web3_bsc.to_hex(tx_hash)


def check_bsc_transaction(tx_hash):
    """Проверка успешности транзакции"""
    receipt = web3_bsc.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.status == 1


def get_abi(contract_address):
    """Получить abi по токену"""

    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": BSC_SCAN_API_KEY,
    }
    response = requests.get(URL_BNB_SCAN_API, params=params)
    data = response.json()

    if data["status"] == "1":
        return json.loads(data["result"])  # ABI в JSON-формате
    else:
        raise ValueError("Не удалось получить ABI: " + data["message"])


def get_balance_bnb():
    """Баланс bnb"""
    balance_wei = web3_bsc.eth.get_balance(account.address)
    return web3_bsc.from_wei(balance_wei, 'ether')


def get_balance_token(token_address):
    """Баланс token_address"""

    checksum_address = Web3.to_checksum_address(token_address)

    token_contract = web3_bsc.eth.contract(
        address=checksum_address, abi=get_abi(checksum_address)
    )

    balance_wei = token_contract.functions.balanceOf(account.address).call()
    return web3_bsc.from_wei(balance_wei, 'ether')


def check_bnb_balance(amount):
    """Проверка баланса BNB"""
    balance_bnb = web3_bsc.eth.get_balance(account.address)

    return balance_bnb > web3_bsc.to_wei(amount, "ether")


def check_token_balance(token_address, amount):
    """Проверка баланса токена"""
    token_contract = web3_bsc.eth.contract(
        address=token_address, abi=get_abi(token_address)
    )
    balance_token = token_contract.functions.balanceOf(account.address).call()

    return balance_token > web3_bsc.to_wei(amount, "ether")


def get_gas_price(default=5):
    """
    Получить рекомендуемую цену газа (gasPrice) в Gwei.
    Используется API BscScan для получения текущей средней цены газа.
    """
    params = {
        "module": "gastracker",
        "action": "gasoracle",
        "apikey": BSC_SCAN_API_KEY,  # Замените на ваш API-ключ BscScan
    }
    response = requests.get(URL_BNB_SCAN_API, params=params)
    data = response.json()

    if data["status"] == "1":
        # Используем среднюю цену газа (ProposeGasPrice)
        gas_price_gwei = data["result"]["ProposeGasPrice"]
        return Web3.to_wei(float(gas_price_gwei), "gwei")
    else:
        # Если API не работает, используем фиксированное значение
        return Web3.to_wei(default, "gwei")  # 5 Gwei по умолчанию


def approve_token(chain_id, token_address, spender_address, amount,
                  gas=200000):
    """
    Дать разрешение (approve) на управление токенами.
    :param token_address: Адрес контракта токена.
    :param spender_address: Адрес контракта, которому дается разрешение
        (например, роутер).
    :param amount_in_wei: Количество токенов для разрешения (в wei).
    :return: Хэш транзакции.
    """
    # Получаем ABI токена
    token_abi = get_abi(token_address)

    # Создаем объект контракта токена
    token_contract = web3_bsc.eth.contract(
        address=Web3.to_checksum_address(token_address), abi=token_abi
    )

    # Подготовка транзакции для вызова approve
    transaction = token_contract.functions.approve(
        Web3.to_checksum_address(spender_address),
        web3_bsc.to_wei(amount, "ether")
    ).build_transaction({
        "chainId": chain_id,  # Chain ID для BSC
        "gas": gas,  # Лимит газа (можно увеличить, если нужно)
        "gasPrice": get_gas_price(default=5),  # Цена газа
        "nonce": web3_bsc.eth.get_transaction_count(account.address),
    })

    # Подписание транзакции
    signed_txn = web3_bsc.eth.account.sign_transaction(transaction, 
                                                       BSC_PRIVATE_KEY)

    # Отправка транзакции
    txn_hash = web3_bsc.eth.send_raw_transaction(signed_txn.raw_transaction)

    return txn_hash
