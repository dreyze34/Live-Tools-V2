from typing import List
import ccxt.async_support as ccxt
import asyncio
import pandas as pd
import time
import itertools
from pydantic import BaseModel


class UsdtBalance(BaseModel):
    total: float
    free: float
    used: float


class Info(BaseModel):
    success: bool
    message: str


class Order(BaseModel):
    id: str
    pair: str
    type: str
    side: str
    price: float
    size: float
    reduce: bool
    filled: float
    remaining: float
    timestamp: int


class TriggerOrder(BaseModel):
    id: str
    pair: str
    type: str
    side: str
    price: float
    trigger_price: float
    size: float
    reduce: bool
    timestamp: int


class Position(BaseModel):
    pair: str
    side: str
    size: float
    usd_size: float
    entry_price: float
    current_price: float
    unrealizedPnl: float
    liquidation_price: float
    margin_mode: str
    leverage: float
    hedge_mode: bool
    open_timestamp: int
    take_profit_price: float
    stop_loss_price: float


class PerpBinance:
    def __init__(self, public_api=None, secret_api=None):
        binance_auth_object = {
            "apiKey": public_api,
            "secret": secret_api,
            "enableRateLimit": True,
            "rateLimit": 100,
            "options": {
                "defaultType": "future",
            },
        }
        if not secret_api:
            self._auth = False
            self._session = ccxt.binance()
        else:
            self._auth = True
            self._session = ccxt.binance(binance_auth_object)

    async def load_markets(self):
        self.market = await self._session.load_markets()

    async def close(self):
        await self._session.close()

    def ext_pair_to_pair(self, ext_pair) -> str:
        return f"{ext_pair}/USDT"

    def pair_to_ext_pair(self, pair) -> str:
        return pair.replace("/USDT", "")

    def get_pair_info(self, ext_pair) -> str:
        pair = self.ext_pair_to_pair(ext_pair)
        return self.market.get(pair)

    def amount_to_precision(self, pair: str, amount: float) -> float:
        pair = self.ext_pair_to_pair(pair)
        try:
            return float(self._session.amount_to_precision(pair, amount))
        except Exception:
            return 0

    def price_to_precision(self, pair: str, price: float) -> float:
        pair = self.ext_pair_to_pair(pair)
        return float(self._session.price_to_precision(pair, price))

    async def get_last_ohlcv(self, pair, timeframe, limit=1000) -> pd.DataFrame:
        pair = self.ext_pair_to_pair(pair)
        bitget_limit = 1500
        ts_dict = {
            "1m": 60 * 1000,
            "5m": 5 * 60 * 1000,
            "15m": 15 * 60 * 1000,
            "1h": 60 * 60 * 1000,
            "2h": 2 * 60 * 60 * 1000,
            "4h": 4 * 60 * 60 * 1000,
            "1d": 24 * 60 * 60 * 1000,
        }
        end_ts = int(time.time() * 1000)
        start_ts = end_ts - ((limit) * ts_dict[timeframe])
        current_ts = start_ts
        tasks = []
        while current_ts < end_ts:
            req_end_ts = min(current_ts + (bitget_limit * ts_dict[timeframe]), end_ts)
            tasks.append(
                self._session.fetch_ohlcv(
                    pair,
                    timeframe,
                    limit=bitget_limit,
                    params={
                        "startTime": str(current_ts),
                        "endTime": str(req_end_ts),
                    },
                )
            )
            current_ts += (bitget_limit * ts_dict[timeframe]) + 1
        ohlcv_unpack = await asyncio.gather(*tasks)
        ohlcv_list = list(itertools.chain.from_iterable(ohlcv_unpack))
        df = pd.DataFrame(
            ohlcv_list, columns=["date", "open", "high", "low", "close", "volume"]
        )
        df = df.set_index(df["date"])
        df.index = pd.to_datetime(df.index, unit="ms")
        df = df.sort_index()
        del df["date"]
        return df

    async def get_balance(self) -> UsdtBalance:
        resp = await self._session.fetch_balance()
        return UsdtBalance(
            total=resp["total"].get("USDT", 0),
            free=resp["free"].get("USDT", 0),
            used=resp["used"].get("USDT", 0),
        )

    async def place_order(
        self,
        pair,
        side,
        price,
        size,
        type="limit",
        reduce=False,
        margin_mode="crossed",
        hedge_mode=False,
        error=False,
    ) -> Order:
        try:
            pair = self.ext_pair_to_pair(pair)
            params = {"reduceOnly": reduce}
            resp = await self._session.create_order(
                symbol=pair,
                type=type,
                side=side,
                amount=size,
                price=price if type == "limit" else None,
                params=params,
            )
            return Order(
                id=resp["id"],
                pair=self.pair_to_ext_pair(resp["symbol"]),
                type=resp["type"],
                side=resp["side"],
                price=resp["price"],
                size=resp["amount"],
                reduce=resp.get("reduceOnly", reduce),
                filled=resp["filled"],
                remaining=resp["remaining"],
                timestamp=resp["timestamp"],
            )
        except Exception as e:
            print(f"Error placing order: {e}")
            if error:
                raise e
            return None

    async def get_open_orders(self, pair) -> List[Order]:
        pair = self.ext_pair_to_pair(pair)
        resp = await self._session.fetch_open_orders(pair)
        return [
            Order(
                id=order["id"],
                pair=self.pair_to_ext_pair(order["symbol"]),
                type=order["type"],
                side=order["side"],
                price=order["price"],
                size=order["amount"],
                reduce=order.get("reduceOnly", False),
                filled=order["filled"],
                remaining=order["remaining"],
                timestamp=order["timestamp"],
            )
            for order in resp
        ]

    async def cancel_orders(self, pair, ids=[]):
        try:
            pair = self.ext_pair_to_pair(pair)
            resp = await self._session.cancel_orders(ids, symbol=pair)
            return Info(success=True, message=f"{len(resp)} orders cancelled")
        except Exception as e:
            return Info(success=False, message=f"Cancel failed: {e}")
