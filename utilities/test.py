import asyncio
from binance_perp import PerpBinance
import os
import ccxt.async_support as ccxt


async def main():
    # Remplace avec tes clés API si nécessaire
    public_key = os.getenv("BINANCE_API_KEY", "")
    secret_key = os.getenv("BINANCE_SECRET_KEY", "")
    
    params = {"type": "margin", "marginMode": "cross"}
    
    client = PerpBinance(public_api=public_key, secret_api=secret_key)
    await client.load_markets()

    order = await client.place_order(pair="BTC/USDC", side="buy", size=0.0001, price=115000, type="limit", params=params)
    info = await client.cancel_orders("BTC/USDC", params=params)
    print(info.message)
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
