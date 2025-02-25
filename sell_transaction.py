from dotenv import load_dotenv

from send_transaction import sell_half_tokens_bsc


load_dotenv()

contract = ''

sell_half_tokens_bsc(contract, x_gas_price=1, gas=200000)
