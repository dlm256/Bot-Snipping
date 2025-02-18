import asyncio
import base64
import struct
import sys

from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction, TransactionInstruction
from solana.rpc.types import TxOpts
from solana.keypair import Keypair  # Correct import for key management

# Replace these with your actual values.
PROGRAM_ID = PublicKey("6wZt5YSnUqaBe1budKMmjRFaehamd9wXnu3kZRbsg8k7")
PRICE_FEED_ACCOUNT = PublicKey("6wZt5YSnUqaBe1budKMmjRFaehamd9wXnu3kZRbsg8k7")
# Load or create your user account securely
USER_ACCOUNT = Keypair.generate()  # Replace with loading from a secure key store

TARGET_PRICE = 100  # Example target price; adjust based on your logic.
RPC_ENDPOINT = "https://api.devnet.solana.com"  # Change to mainnet when ready.

async def hunt():
    async with AsyncClient(RPC_ENDPOINT) as client:
        # 1. Fetch the price feed account data.
        resp = await client.get_account_info(PRICE_FEED_ACCOUNT)
        account_info = resp.get("result", {}).get("value")
        
        if account_info is None or "data" not in account_info:
            print("Failed to fetch price feed account data.")
            return

        # Decode base64 data
        try:
            data_base64 = account_info["data"][0]
            data_bytes = base64.b64decode(data_base64)
        except (IndexError, KeyError, base64.binascii.Error) as e:
            print(f"Error decoding price feed data: {e}")
            return
        
        if len(data_bytes) < 8:
            print("Unexpected data format in price feed account.")
            return
        
        # Assume the price is stored as an 8-byte little-endian unsigned integer.
        try:
            current_price = struct.unpack("<Q", data_bytes[:8])[0]
            print(f"Current price: {current_price}")
        except struct.error as e:
            print(f"Error unpacking price data: {e}")
            return

        # 2. Check if current price meets our sniping criteria.
        if current_price <= TARGET_PRICE:
            print("Sniping opportunity detected!")

            # 3. Prepare the instruction data.
            instruction_data = struct.pack("<Q", TARGET_PRICE)

            # Define the accounts required by your on-chain program.
            keys = [
                (PRICE_FEED_ACCOUNT, False, True),  # Writable account
                (USER_ACCOUNT.public_key, True, False)  # Signer account
            ]

            # Create the instruction to call your smart contract’s "hunt" function.
            instruction = TransactionInstruction(
                keys=[{"pubkey": key[0], "is_signer": key[1], "is_writable": key[2]} for key in keys],
                program_id=PROGRAM_ID,
                data=instruction_data,
            )

            # Build the transaction.
            tx = Transaction()
            tx.add(instruction)

            # Send the transaction.
            print("Sending transaction...")
            try:
                tx_response = await client.send_transaction(tx, USER_ACCOUNT, signers=[USER_ACCOUNT], opts=TxOpts(skip_confirmation=False))
                print("Transaction response:", tx_response)
            except Exception as e:
                print(f"Transaction failed: {e}")
        else:
            print("No opportunity detected.")

if __name__ == '__main__':
    asyncio.run(hunt())
