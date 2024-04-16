import aiohttp
import asyncio
import logging
from pytoniq import LiteBalancer, WalletV4R2
from config import MNEMONICS, API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": API_KEY
}
# Самая важная часть, которая все еще работает колхозно, адреса что тут находятся это два последний адреса контракта продажи, если не хотите в пустую тратить бабки на комсу при каждом старте софта, то найдите по адресу EQBmSy9SfRj44LZPi84NyvI4seJlZYSz33MM0rl78DnkCb2Z последние два кошеля с контрактом продажи и напишите их тут
processed_addresses = {
    "EQAk5i9ti7_mUU1QLqUU8TBkZqpivzNwQXMXIfBge5c7QRZD",
    "EQDbMFUDqzo_5ZgaWivQRKoxIuaZpzTL5Qtz1OCCYaXDJP_4"
}


async def nft_buy(destination):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=MNEMONICS)
    # Здесь у нас куда пойдут бабки и сколько
    transfer = {
        "destination": destination,
        "amount": 3000000000,
    }

    await wallet.transfer(**transfer)
    await provider.close_all()

async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        await asyncio.sleep(0.05) 
        return await response.json()

async def get_transactions():
    async with aiohttp.ClientSession() as session:
        # Здесь указывается адрес кошелька, который будет парсить, в нашем случае это EQBmSy9SfRj44LZPi84NyvI4seJlZYSz33MM0rl78DnkCb2Z
        url = "https://toncenter.com/api/v2/getTransactions?address=EQBmSy9SfRj44LZPi84NyvI4seJlZYSz33MM0rl78DnkCb2Z&limit=4&to_lt=0&archival=false"
        response = await fetch(session, url)

        for transaction in response['result']:
            if 'out_msgs' in transaction and transaction['out_msgs']:
                for msg in transaction['out_msgs']:
                    if msg['value'] == '20000000':
                        destination = msg['destination']
                        if destination not in processed_addresses:
                            processed_addresses.add(destination)
                            await nft_buy(destination)
                            logging.info(f"Processed address: {destination}")



async def monitor_nft_sales():
    while True:
        await get_transactions()

# Run the monitor_nft_sales function asynchronously
asyncio.run(monitor_nft_sales())
