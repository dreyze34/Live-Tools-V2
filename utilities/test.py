import asyncio
from binance_perp import PerpBinance  # adapte ce nom au vrai fichier
import os
import ccxt.async_support as ccxt  # 👈 version asynchrone !


async def main():
    # Remplace avec tes clés API si nécessaire
    public_key = os.getenv("BINANCE_API_KEY", "")
    secret_key = os.getenv("BINANCE_SECRET_KEY", "")

    client = PerpBinance(public_api=public_key, secret_api=secret_key)
    await client.load_markets()

    await client.set_margin_mode_and_leverage("BTCUSDC", "crossed", 3)

    print("📈 Testing get_pair_info('BTC'):")
    info = client.get_pair_info("BTC")
    print(info)

    print("\n💰 Testing get_balance():")
    balance = await client.get_balance()
    print(balance)

    print("\n🕒 Testing get_last_ohlcv('BTC/USDC', '1m', 100):")
    ohlcv = await client.get_last_ohlcv("BTC/USDC", "1m", limit=100)
    print(ohlcv.tail())

    print("\n📋 Testing get_open_orders('BTC'):")
    open_orders = await client.get_open_orders("BTC/USDC", params={})
    for order in open_orders:
        print(order)

    print("\n Testing get_all_positions():")
    positions = await client.get_position("BTC/USDC")
    for position in positions:
        print(position)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
