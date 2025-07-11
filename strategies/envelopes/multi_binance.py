import datetime
import sys
import asyncio
import ta
import os

sys.path.append("./../Live-Tools-V2")

from utilities.binance_perp import PerpBinance

from secret import ACCOUNTS
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



async def main():
    public_api = os.getenv("BINANCE_API_KEY", "")
    secret_api = os.getenv("BINANCE_SECRET_KEY", "")

    margin_mode = "cross"  # Binance Perp supports 'isolated' and 'cross'
    leverage = 3
    hedge_mode = True  # Must be enabled in Binance account settings

    tf = "1h"
    sl = 0.3

    params = {
        "BTC/USDC": {
            "src": "close",
            "ma_base_window": 7,
            "envelopes": [0.07, 0.1, 0.15],
            "size": 0.1,
            "sides": ["long", "short"],
        },
        "ETH/USDC": {
            "src": "close",
            "ma_base_window": 5,
            "envelopes": [0.07, 0.1, 0.15],
            "size": 0.1,
            "sides": ["long", "short"],
        },
        # "ADA/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.09, 0.12, 0.15],
        #     "size": 0.1,
        #     "sides": ["long", "short"],
        # },
        # "AVAX/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.09, 0.12, 0.15],
        #     "size": 0.1,
        #     "sides": ["long", "short"],
        # },
        # "EGLD/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "KSM/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "OCEAN/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "REN/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "ACH/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "APE/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "CRV/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "DOGE/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "ENJ/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "FET/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "ICP/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "IMX/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "LDO/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "MAGIC/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "REEF/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "SAND/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "TRX/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
        # "XTZ/USDC": {
        #     "src": "close",
        #     "ma_base_window": 5,
        #     "envelopes": [0.07, 0.1, 0.15, 0.2],
        #     "size": 0.05,
        #     "sides": ["long", "short"],
        # },
    }

    exchange = PerpBinance(
        public_api,
        secret_api,
    )

    invert_side = {"long": "sell", "short": "buy"}

    print(f"--- Execution started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    try:
        await exchange.load_markets()

        for pair in list(params):
            info = exchange.get_pair_info(pair)
            if info is None:
                print(f"Pair {pair} not found, removing from params...")
                del params[pair]

        pairs = list(params)

        # try:
        #     print(f"Setting {margin_mode} x{leverage} on {len(pairs)} pairs...")
        #     tasks = [
        #         exchange.set_margin_mode_and_leverage(pair, margin_mode, leverage)
        #         for pair in pairs
        #     ]
        #     await asyncio.gather(*tasks)
        # except Exception as e:
        #     print(e)

        print(f"Getting data and indicators on {len(pairs)} pairs...")
        tasks = [exchange.get_last_ohlcv(pair, tf, 50) for pair in pairs]
        dfs = await asyncio.gather(*tasks)
        df_list = dict(zip(pairs, dfs))

        for pair, df in df_list.items():
            current_params = params[pair]
            src = df["close"] if current_params["src"] == "close" else \
                (df["close"] + df["high"] + df["low"] + df["open"]) / 4

            df["ma_base"] = ta.trend.sma_indicator(src, window=current_params["ma_base_window"])
            high_envelopes = [round(1 / (1 - e) - 1, 3) for e in current_params["envelopes"]]

            for i, e in enumerate(current_params["envelopes"], start=1):
                df[f"ma_high_{i}"] = df["ma_base"] * (1 + high_envelopes[i - 1])
                df[f"ma_low_{i}"] = df["ma_base"] * (1 - e)

        USDC_balance = await exchange.get_balance()
        print(f"Balance: {round(USDC_balance.total, 2)} USDC")

        # Cancel existing orders
        print("Canceling existing orders...")
        tasks = [exchange.cancel_orders(pair,  params={"marginMode": margin_mode}) for pair in pairs]
        await asyncio.gather(*tasks)

        print("Getting open positions...")
        positions = await exchange.get_all_positions(pairs, params={"marginMode": margin_mode})
        tasks_close = []
        tasks_open = []

        for position in positions:
            row = df_list[position.pair].iloc[-2]
            print(f"position on {position.pair}: {position.side} - {position.size}")

            # Close with limit + stop
            tasks_close.append(
                exchange.place_position(
                    pair=position.pair,
                    side=invert_side[position.side],
                    price=row["ma_base"],
                    size=position.size,
                    type="LIMIT",
                    reduce=True,
                    margin_mode=margin_mode,
                    hedge_mode=hedge_mode,
                )
            )

            sl_price = (
                position.entry_price * (1 - sl) if position.side == "long"
                else position.entry_price * (1 + sl)
            )
            tasks_close.append(
                exchange.place_position(
                    pair=position.pair,
                    side=invert_side[position.side],
                    price=None,
                    stop_price=sl_price,
                    size=position.size,
                    type="STOP_MARKET",
                    reduce=True,
                    margin_mode=margin_mode,
                    hedge_mode=hedge_mode,
                )
            )

        # Open orders for new orders or scaled orders
        for pair in pairs:
            row = df_list[pair].iloc[-2]
            active_order = next((p for p in orders if p.pair == pair), None)
            for i in range(len(params[pair]["envelopes"])):
                base_amount = (
                    (params[pair]["size"] * USDC_balance.total)
                    / len(params[pair]["envelopes"]) * leverage
                )
                size_buy = base_amount / row[f"ma_low_{i + 1}"]
                size_sell = base_amount / row[f"ma_high_{i + 1}"]

                if "long" in params[pair]["sides"]:
                    tasks_open.append(
                        exchange.place_order(
                            pair=pair,
                            side="buy",
                            price=row[f"ma_low_{i + 1}"],
                            stop_price=row[f"ma_low_{i + 1}"] * 1.005,
                            size=size_buy,
                            type="STOP_LIMIT",
                            reduce=False,
                            margin_mode=margin_mode,
                            hedge_mode=hedge_mode,
                        )
                    )
                if "short" in params[pair]["sides"]:
                    tasks_open.append(
                        exchange.place_order(
                            pair=pair,
                            side="sell",
                            price=row[f"ma_high_{i + 1}"],
                            stop_price=row[f"ma_high_{i + 1}"] * 0.995,
                            size=size_sell,
                            type="STOP_LIMIT",
                            reduce=False,
                            margin_mode=margin_mode,
                            hedge_mode=hedge_mode,
                        )
                    )

        print(f"Placing {len(tasks_close)} close orders...")
        await asyncio.gather(*tasks_close)

        print(f"Placing {len(tasks_open)} open orders...")
        await asyncio.gather(*tasks_open)

        await exchange.close()
        print(f"--- Execution finished at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    except Exception as e:
        await exchange.close()
        raise e


if __name__ == "__main__":
    asyncio.run(main())
