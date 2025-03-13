from web3 import Web3
import json
import time
from eth_account import Account

# === Configuration ===
INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # ⚠️ Store securely!
WALLET_ADDRESS = "YOUR_WALLET_ADDRESS"

# Uniswap Router and Factory addresses
UNISWAP_FACTORY = Web3.to_checksum_address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
UNISWAP_ROUTER = Web3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")

# WETH Address (Ethereum Wrapped Token)
WETH = Web3.to_checksum_address("0xC02aaa39b223FE8D0A0e5C4F27eaD9083C756Cc2")

# Connect to Ethereum
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Load Uniswap Factory ABI
with open("uniswap_factory_abi.json", "r") as f:
    UNISWAP_FACTORY_ABI = json.load(f)

factory_contract = web3.eth.contract(address=UNISWAP_FACTORY, abi=UNISWAP_FACTORY_ABI)

# === Monitor for New Liquidity Pools ===
def check_new_pairs():
    latest_block = web3.eth.block_number
    event_filter = factory_contract.events.PairCreated.create_filter(fromBlock=latest_block)

    print("[INFO] Monitoring new Uniswap pairs...")

    while True:
        for event in event_filter.get_new_entries():
            token0 = event['args']['token0']
            token1 = event['args']['token1']
            pair_address = event['args']['pair']

            print(f"[NEW PAIR] Detected - {token0} & {token1} at {pair_address}")

            if token0 == WETH or token1 == WETH:
                target_token = token1 if token0 == WETH else token0
                print(f"[BUY] Sniping token: {target_token}")
                buy_token(target_token)

        time.sleep(5)  # Avoid spamming requests

# === Buy Tokens on Uniswap ===
def buy_token(token_address):
    # Load Uniswap Router ABI
    with open("uniswap_router_abi.json", "r") as f:
        UNISWAP_ROUTER_ABI = json.load(f)

    router_contract = web3.eth.contract(address=UNISWAP_ROUTER, abi=UNISWAP_ROUTER_ABI)

    # Transaction Details
    amount_in_wei = web3.to_wei(0.01, 'ether')  # Amount of ETH to swap
    deadline = int(time.time()) + 60  # Transaction deadline

    path = [WETH, Web3.to_checksum_address(token_address)]
    min_tokens_out = 0  # Set slippage tolerance accordingly

    # Build Transaction
    txn = router_contract.functions.swapExactETHForTokens(
        min_tokens_out,
        path,
        WALLET_ADDRESS,
        deadline
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'value': amount_in_wei,
        'gas': 300000,
        'gasPrice': web3.to_wei('5', 'gwei'),
        'nonce': web3.eth.get_transaction_count(WALLET_ADDRESS),
    })

    # Sign & Send Transaction
    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"[TXN SENT] {tx_hash.hex()}")

# === Run the Sniping Bot ===
if __name__ == "__main__":
    check_new_pairs()