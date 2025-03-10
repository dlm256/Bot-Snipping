import asyncio
import requests
from web3 import Web3

# Replace with your Infura/Alchemy or any Ethereum RPC provider
RPC_ENDPOINT = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))

# Replace with your private key and wallet address
PRIVATE_KEY = "0xc4efc84f95191bd5cb132fae2c2d3fd960e2bf9ef9e89ead3c96720c6ad0a9d4"
WALLET_ADDRESS = w3.to_checksum_address("0x89C4C40e77fA5a1Bb57bf0c02090c4b1d42A1fFe")

# Set the contract details
CONTRACT_ADDRESS = w3.to_checksum_address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")  # Example (Uniswap Factory)
TARGET_PRICE = 2000  # Set your Ethereum target price in USD
GAS_PRICE_GWEI = 20  # Set gas price in Gwei

def get_eth_price():
    """Fetch Ethereum price from CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data["ethereum"]["usd"]
    except Exception as e:
        print(f"Error fetching ETH price: {e}")
        return None

def create_transaction():
    """Creates and sends a transaction when sniping conditions are met."""
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    
    tx = {
        'nonce': nonce,
        'to': WALLET_ADDRESS,  # Example: self-transfer to test transaction
        'value': w3.to_wei(0.001, 'ether'),  # Adjust value as needed
        'gas': 21000,
        'gasPrice': w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    print(f"Transaction sent! Hash: {w3.to_hex(tx_hash)}")

async def snipe():
    """Continuously checks for ETH price and executes a transaction when the condition is met."""
    while True:
        eth_price = get_eth_price()
        
        if eth_price:
            print(f"Current ETH Price: ${eth_price}")
            if eth_price <= TARGET_PRICE:
                print("Sniping opportunity detected! Executing transaction...")
                create_transaction()
                break  # Stop the bot after sniping
        
        await asyncio.sleep(30)  # Check price every 30 seconds

if __name__ == '__main__':
    asyncio.run(snipe())
