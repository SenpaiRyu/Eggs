import aiohttp
import asyncio
import logging
from pytoniq import LiteBalancer, WalletV4R2
from config import MNEMONICS, API_KEY, NFT_ADDRESS, NFT_COLLECTION_ADDRESS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": API_KEY
}

processed_addresses = set()


async def nft_buy(destination):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=MNEMONICS)

    transfer = {
        "destination": destination,
        "amount": 3000000000,
    }

    await wallet.transfer(**transfer)
    await provider.close_all()

async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        await asyncio.sleep(0.1) # Sleep for 100 milliseconds to stay within the rate limit
        return await response.json()

async def get_transactions():
    async with aiohttp.ClientSession() as session:
        url = f"https://toncenter.com/api/v3/nft/transfers?address={NFT_ADDRESS}&collection_address={NFT_COLLECTION_ADDRESS}&direction=out&limit=2&offset=0&sort=desc"
        response = await fetch(session, url)

        # Check if 'nft_transfers' key exists in the response
        if 'nft_transfers' in response:
            for transfer in response['nft_transfers']:
                destination = transfer['new_owner']
                # Add the first two addresses to processed_addresses
                if len(processed_addresses) < 2:
                    processed_addresses.add(destination)
                    logging.info(f"Отработанные адреса: {destination}")
                else:
                    # Check if the current address is not already processed
                    if destination not in processed_addresses:
                        processed_addresses.add(destination)
                        await nft_buy(destination)
                        logging.info(f"Новый адрес контракта продажи: {destination}")
        else:
            logging.error("Не найдены кокошки(")

logging.info("Начинаем работать....")

async def monitor_nft_sales():
    while True:
        await get_transactions()

# Run the monitor_nft_sales function asynchronously
asyncio.run(monitor_nft_sales())
