from web3 import Web3
from web3.middleware import geth_poa_middleware

import os
import json
import requests
import time
from dotenv import load_dotenv

from telegram_message import send_message


load_dotenv()

# Blockchain Setup
BSC_RPC_URL = "https://bsc-dataseed.binance.org/"

# Подключение к блокчейну
web3_bsc = Web3(Web3.HTTPProvider(BSC_RPC_URL))
web3_bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

# Ключи кошельков (замени своими!)
BSC_PRIVATE_KEY = os.getenv("BSC_PRIVATE_KEY")

BSC_SCAN_API_KEY = os.getenv("BSC_SCAN_API_KEY")


def check_bsc_transaction(tx_hash):
    time.sleep(10)

    url = f"https://api.bscscan.com/api?module=transaction&action=gettxreceiptstatus&txhash={tx_hash}&apikey={BSC_SCAN_API_KEY}"
    response = requests.get(url).json()

    if response["status"] == "1":
        if response["result"]["status"] == "1":
            send_message(f"✅ Транзакция <code>{tx_hash}</code> успешна!")
        else:
            send_message(f"❌ Транзакция <code>{tx_hash}</code> не удалась!")
            raise RuntimeError('Транзакция не прошла')

        return
    else:
        send_message(f"⏳ Транзакция <code>{tx_hash}</code> в ожидании или не найдена.")
        check_bsc_transaction(tx_hash)


def get_abi(contract_address):
    url = f"https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={BSC_SCAN_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "1":
        return json.loads(data["result"])  # ABI в JSON-формате
    else:
        raise ValueError("Не удалось получить ABI: " + data["message"])


def buy_token_bsc(contract_address, amount_bnb, x_gas_price=3, gas=250000):
    """Функция покупки токена на BSC (PancakeSwap)"""

    # PancakeSwap Router
    router_address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

    pancakeswap_abi = '[{"constant":false,"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":true,"stateMutability":"payable","type":"function"}]'
    router_abi = json.loads(pancakeswap_abi)

    router_contract = web3_bsc.eth.contract(
        address=router_address, abi=router_abi
    )

    # Настройка транзакции
    account = web3_bsc.eth.account.from_key(BSC_PRIVATE_KEY)
    amount_wei = web3_bsc.to_wei(amount_bnb, "ether")
    path = [
        web3_bsc.to_checksum_address(
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"),  # WBNB
        web3_bsc.to_checksum_address(contract_address),
    ]
    deadline = web3_bsc.eth.get_block("latest")["timestamp"] + 600

    gas_price = web3_bsc.eth.gas_price * x_gas_price
    txn = router_contract.functions.swapExactETHForTokens(
        0, path, account.address, deadline
    ).build_transaction({
        "from": account.address,
        "value": amount_wei,
        "gas": gas,  # Запас газа
        "gasPrice": gas_price,
        "nonce": web3_bsc.eth.get_transaction_count(account.address),
    })

    # Подписываем и отправляем транзакцию
    signed_txn = web3_bsc.eth.account.sign_transaction(txn, account.key)
    txn_hash = web3_bsc.eth.send_raw_transaction(signed_txn.raw_transaction)
    send_message(
        f"✅ Покупка токена <code>{contract_address}</code> на BSC! "
        f"TX: <code>{web3_bsc.to_hex(txn_hash)}</code>"
    )

    check_bsc_transaction(web3_bsc.to_hex(txn_hash))


def sell_half_tokens_bsc(contract_address, x_gas_price=2, gas=250000):
    """Функция продажи половины токенов на BSC (PancakeSwap)"""

    # PancakeSwap Router
    router_address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

    pancakeswap_abi = '[{"constant":false,"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    router_abi = json.loads(pancakeswap_abi)

    router_contract = web3_bsc.eth.contract(
        address=router_address, abi=router_abi
    )

    # Настройка транзакции
    account = web3_bsc.eth.account.from_key(BSC_PRIVATE_KEY)
    token_contract = web3_bsc.eth.contract(
        address=web3_bsc.to_checksum_address(contract_address),
        abi=get_abi(contract_address)
    )

    balance = token_contract.functions.balanceOf(account.address).call()
    amount_to_sell = balance // 2  # Продаём половину баланса
    if amount_to_sell == 0:
        send_message("❌ Недостаточно токенов для продажи!")
        return

    path = [
        web3_bsc.to_checksum_address(contract_address),
        web3_bsc.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # WBNB
    ]
    deadline = web3_bsc.eth.get_block("latest")["timestamp"] + 600

    # Одобрение токенов для продажи
    gas_price = web3_bsc.eth.gas_price * x_gas_price
    approve_txn = token_contract.functions.approve(
        router_address, amount_to_sell
    ).build_transaction({
        "from": account.address,
        "gas": gas,
        "gasPrice": gas_price,
        "nonce": web3_bsc.eth.get_transaction_count(account.address),
    })
    signed_approve_txn = web3_bsc.eth.account.sign_transaction(approve_txn, account.key)
    web3_bsc.eth.send_raw_transaction(signed_approve_txn.raw_transaction)

    # Транзакция на продажу
    gas_price = web3_bsc.eth.gas_price * x_gas_price
    sell_txn = router_contract.functions.swapExactTokensForETH(
        amount_to_sell, 0, path, account.address, deadline
    ).build_transaction({
        "from": account.address,
        "gas": gas,
        "gasPrice": gas_price,
        "nonce": web3_bsc.eth.get_transaction_count(account.address) + 1,
    })

    # Подписываем и отправляем транзакцию
    signed_sell_txn = web3_bsc.eth.account.sign_transaction(sell_txn, account.key)
    txn_hash = web3_bsc.eth.send_raw_transaction(signed_sell_txn.raw_transaction)
    send_message(
        f"✅ Продажа половины токенов <code>{contract_address}</code> на BSC! "
        f"TX: <code>{web3_bsc.to_hex(txn_hash)}</code>"
    )

    check_bsc_transaction(web3_bsc.to_hex(txn_hash))
