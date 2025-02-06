import asyncio
import base64
import struct
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction, TransactionInstruction
from solana.rpc.types import TxOpts
from solana.account import Account  # For keypair management

# Replace these with your actual values.
PROGRAM_ID = PublicKey("6wZt5YSnUqaBe1budKMmjRFaehamd9wXnu3kZRbsg8k7")
PRICE_FEED_ACCOUNT = PublicKey("6wZt5YSnUqaBe1budKMmjRFaehamd9wXnu3kZRbsg8k7")
# Load or create your user account. For real usage, load from a secure key store.
USER_ACCOUNT = Account()  

TARGET_PRICE = 100  # Example target price; adjust based on your logic.
RPC_ENDPOINT = "https://api.devnet.solana.com"  # Change to mainnet endpoint when ready.

async def hunt():
    async with AsyncClient(RPC_ENDPOINT) as client:
        # 1. Fetch the price feed account data.
        resp = await client.get_account_info(PRICE_FEED_ACCOUNT)
        account_info = resp.get("result", {}).get("value")
        if account_info is None:
            print("Failed to fetch price feed account data.")
            return

        # Assume the price is stored as an 8-byte little-endian unsigned integer.
        data_base64 = account_info["data"][0]
        data_bytes = base64.b64decode(data_base64)
        current_price = struct.unpack("<Q", data_bytes[:8])[0]
        print(f"Current price: {current_price}")

        # 2. Check if current price meets our sniping criteria.
        if current_price <= TARGET_PRICE:
            print("Sniping opportunity detected!")

            # 3. Prepare the instruction data.
            # For example, the on-chain program might expect the target price as an 8-byte integer.
            instruction_data = struct.pack("<Q", TARGET_PRICE)

            # Define the accounts required by your on-chain program.
            # Here we assume:
            # - PRICE_FEED_ACCOUNT is writable (to update state or record the trade).
            # - USER_ACCOUNT is a signer (authorizing the transaction).
            keys = [
                {"pubkey": PRICE_FEED_ACCOUNT, "is_signer": False, "is_writable": True},
                {"pubkey": USER_ACCOUNT.public_key(), "is_signer": True, "is_writable": False},
            ]

            # Create the instruction to call your smart contract’s "hunt" function.
            instruction = TransactionInstruction(
                keys=keys,
                program_id=PROGRAM_ID,
                data=instruction_data,
            )

            # Build the transaction.
            tx = Transaction()
            tx.add(instruction)

            # Send the transaction.
            print("Sending transaction...")
            tx_response = await client.send_transaction(tx, USER_ACCOUNT, opts=TxOpts(skip_confirmation=False))
            print("Transaction response:", tx_response)
        else:
            print("No opportunity detected.")

if __name__ == '__main__':
    asyncio.run(hunt())