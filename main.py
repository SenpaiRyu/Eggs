import aiohttp
import asyncio
import logging
from pytoniq import LiteBalancer, WalletV4R2
from pytoniq_core import Address
from config import MNEMONICS, API_KEY, NFT_ADDRESS, NFT_COLLECTION_ADDRESS, NFT_PURCHASE_PRICE
from parse_sale import get_sale_data
from client import get_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": API_KEY
}

processed_addresses = set()

async def nft_buy(full_price, formatted_destination):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=MNEMONICS)

    transfer = {
        "destination": formatted_destination,
        "amount": full_price + 1000000000,
    }

    await wallet.transfer(**transfer)
    await provider.close_all()


async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            logging.error(f"Непредвидённый тип контента: {content_type}")
            return {} # Return an empty dictionary or handle the error as needed
        return await response.json()


async def get_transactions(client):
    async with aiohttp.ClientSession() as session:
        url = f"https://toncenter.com/api/v3/nft/transfers?address={NFT_ADDRESS}&collection_address={NFT_COLLECTION_ADDRESS}&direction=out&limit=2&offset=0&sort=desc"
        response = await fetch(session, url)
        if 'nft_transfers' in response:
            new_addresses = set(t['new_owner'] for t in response['nft_transfers']) - processed_addresses
            for destination in new_addresses:
                formatted_destination = Address(destination).to_str(is_user_friendly=True, is_bounceable=True, is_url_safe=True)
                processed_addresses.add(destination)
                # Fetch the sale data for the new address
                sale_data = await get_sale_data(client, formatted_destination)
                if sale_data is None:
                    # This destination is not a sale contract but an auction contract
                    logging.info(f"Адрес контракта аукциона: {formatted_destination}")
                else:
                    is_complete, nft_address, full_price = sale_data
                    formatted_price = float(full_price / 1000000000) # Extract the numeric part of the price
                    logging.info(f"Новый адрес контракта продажи: {formatted_destination} Цена: {formatted_price} ton")
                    if formatted_price <= NFT_PURCHASE_PRICE and not is_complete and full_price > 0:
                        await nft_buy(full_price, formatted_destination)
                        logging.warning(f"Купил NFT: {nft_address}, по цене: {formatted_price} ton")
        else:
            pass


logging.info("Начинаем работать....")

async def monitor_nft_sales():
    client = await get_client(0, False)
    while True:
        await get_transactions(client)

# Run the monitor_nft_sales function asynchronously
asyncio.run(monitor_nft_sales())
