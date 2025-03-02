from dotenv import load_dotenv

from send_transaction import sell_half_tokens_bsc, buy_token_bsc


load_dotenv()

contract = '0x8B9ABDD229ec0C4A28E01b91aacdC5dAAFc25C2b'

# sell_half_tokens_bsc(contract)
buy_token_bsc(contract, 0.001)
