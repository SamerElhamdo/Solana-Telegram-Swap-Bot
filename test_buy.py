from swap import Swap
from secret import TEST_PRIVATE_KEY, RPC_URL
import asyncio

swap = Swap(rpc_url=RPC_URL, private_key=TEST_PRIVATE_KEY)

async def main():
    await swap.swap_token("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "So11111111111111111111111111111111111111112", 0.001, 15)


asyncio.run(main())