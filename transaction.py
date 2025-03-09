from send_transaction import buy_token_bsc, sell_token_bsc
from telegram_message import send_message
from bnb_util import check_bsc_transaction, hash_to_hex, get_balance_token


contract = '0x4b0f1812e5df2a09796481ff14017e6005508003'
amount = get_balance_token(contract)

tx_hash = sell_token_bsc(contract, amount // 2)
tx_hash = hash_to_hex(tx_hash)
send_message((
    f"🚀 Покупка токена <code>{contract}</code>. "
    f"Хэш: <code>{tx_hash}</code>"
))

if check_bsc_transaction(tx_hash):
    send_message(f"✅ Транзакция <code>{tx_hash}</code> успешна!")
else:
    send_message(f"❌ Транзакция <code>{tx_hash}</code> не удалась!")
