import aiohttp
import asyncio
import logging
from pytoniq import LiteBalancer, WalletV4R2
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

async def nft_buy(full_price, destination):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=MNEMONICS)
    # На какой адрес, какая сумма пойдет, +1000000000 это комиссия гетгемса, чтобы ваша транза точно прошла, вам вернется все что не было потрачено на комсу
    transfer = {
        "destination": destination,
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
                processed_addresses.add(destination)
                # Парсим данные контракта
                sale_data = await get_sale_data(client, destination)
                if sale_data is None:
                    # Если мы не получили цену контракта, значит это аукцион
                    logging.info(f"Адрес контракта аукциона: {destination}")
                else:
                    is_complete, nft_address, full_price = sale_data
                    formatted_price = float(full_price / 1000000000) # Форматирует цену из нано в тоны
                    logging.info(f"Новый адрес контракта продажи: {destination}, Цена: {formatted_price} Ton")
                    # Если цена меньше или равно вашему параметру и нфт еще не купили, то вы покупаете нфт
                    if formatted_price <= NFT_PURCHASE_PRICE and not is_complete and full_price > 0:
                        await nft_buy(full_price, destination)
                        logging.warning(f"Купил NFT: {nft_address}, по цене: {formatted_price}")
        else:
            pass


logging.info("Начинаем работать....")

async def monitor_nft_sales():
    client = await get_client(1, False)
    while True:
        await get_transactions(client)


asyncio.run(monitor_nft_sales())
