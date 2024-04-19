import asyncio
import base64
from client import *

async def get_sale_data(client: TonlibClient, address):

    stack = await run_get_method(client, address=address, method='get_sale_data', stack=[])
    
    fix_magic = '0x46495850'
    if stack[0][1] == fix_magic:
        is_complete = bool(int(stack[1][1], 16))
        created_at = int(stack[2][1], 16)
        marketplace_address = Cell.one_from_boc(base64.b64decode(stack[3][1]['bytes'])).begin_parse().read_msg_addr().to_string(True, True, True)
        nft_address = Cell.one_from_boc(base64.b64decode(stack[4][1]['bytes'])).begin_parse().read_msg_addr().to_string(True, True, True)
        nft_owner_address = Cell.one_from_boc(base64.b64decode(stack[5][1]['bytes'])).begin_parse().read_msg_addr().to_string(True, True, True)
        full_price = int(stack[6][1], 16)

        return is_complete, nft_address, full_price
    else:
        return None
        
async def pytonlib():
    client = await get_client(1, False)
    # Здесь можно не зависимо от использования основного main.py узнать статус контракта продажи
    result = await get_sale_data(client, 'EQAEFZf5wv9lUGhbBSX4vd615SQUOOeIDg94N8J-VXuxQrL5')

    print(result)

    await client.close()

if __name__ == '__main__':
    asyncio.run(pytonlib())
