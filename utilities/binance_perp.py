from typing import List
import ccxt.async_support as ccxt
import asyncio
import pandas as pd
import time
import itertools
from pydantic import BaseModel


class USDCBalance(BaseModel):
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
                "defaultType": "margin",
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

    def pair_to_ext_pair(self, pair) -> str:
        return pair.replace("/USDC", "")

    def get_pair_info(self, pair) -> str:
        return self.market.get(pair)

    def amount_to_precision(self, pair: str, amount: float) -> float:
        try:
            return float(self._session.amount_to_precision(pair, amount))
        except Exception:
            return 0

    def price_to_precision(self, pair: str, price: float) -> float:
        return float(self._session.price_to_precision(pair, price))

    async def get_last_ohlcv(self, pair, timeframe, limit=1000) -> pd.DataFrame:
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

    async def get_balance(self) -> USDCBalance:
        resp = await self._session.fetch_balance(params={"type": "margin"})
        return USDCBalance(
            total=resp["total"].get("USDC", 0),
            free=resp["free"].get("USDC", 0),
            used=resp["used"].get("USDC", 0),
        )

    async def set_margin_mode_and_leverage(self, pair, margin_mode, leverage):
        if margin_mode not in ["crossed", "isolated"]:
            raise Exception("Margin mode must be either 'crossed' or 'isolated'")
        try:
            await self._session.set_margin_mode(
                margin_mode,
                pair,
                # params={"productType": "USDT-FUTURES", "marginCoin": "USDT"},
            )
        except Exception as e:
            pass
        try:
            if margin_mode == "isolated":
                tasks = []
                tasks.append(
                    self._session.set_leverage(
                        leverage,
                        pair,
                        # params={
                        #     "productType": "USDT-FUTURES",
                        #     "marginCoin": "USDT",
                        #     "holdSide": "long",
                        # },
                    )
                )
                # tasks.append(
                #     self._session.set_leverage(
                #         leverage,
                #         pair,
                #         # params={
                #         #     "productType": "USDT-FUTURES",
                #         #     "marginCoin": "USDT",
                #         #     "holdSide": "short",
                #         # },
                #     )
                # )
                await asyncio.gather(*tasks)
            else:
                await self._session.set_leverage(
                    leverage,
                    pair,
                    # params={"productType": "USDT-FUTURES", "marginCoin": "USDT"},
                )
        except Exception as e:
            pass

        return Info(
            success=True,
            message=f"Margin mode and leverage set to {margin_mode} and {leverage}x",
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
                reduce=bool(resp.get("reduceOnly", reduce)),
                filled=resp["filled"],
                remaining=resp["remaining"],
                timestamp=resp["timestamp"],
            )
        except Exception as e:
            print(f"Error placing order: {e}")
            if error:
                raise e
            return None

    async def get_open_orders(self, pair, params) -> List[Order]:
        resp = await self._session.fetch_open_orders(pair, params=params)
        return [
            Order(
                id=order["id"],
                pair=self.pair_to_ext_pair(order["symbol"]),
                type=order["type"],
                side=order["side"],
                price=order["price"],
                size=order["amount"],
                reduce=bool(order.get("reduceOnly", False)),
                filled=order["filled"],
                remaining=order["remaining"],
                timestamp=order["timestamp"],
            )
            for order in resp
        ]

    async def get_all_open_orders(self, pairs, params) -> List[Order]:
        all_orders = []
        for pair in pairs:
            orders = await self.get_open_orders(pair, params=params)
            all_orders.extend(orders)
        return all_orders


    async def cancel_orders(self, pair, params={}) -> Info:
        try:
            resp = await self._session.cancel_all_orders(symbol=pair, params=params)
            return Info(success=True, message=f"{len(resp)} orders cancelled")
        except Exception as e:
            return Info(success=False, message=f"Cancel failed: {e}")
        
    async def get_position(self, pair: str) -> Position:
        """
        Récupère les 'positions' en trading de marge (Cross margin) sur Binance.
        Retourne une liste d’actifs avec un solde ou un emprunt non nul.
        """
        # Nécessite un sous-type de compte
        margin_balance = await self._session.sapi_get_margin_account()

        positions = []
        for asset in margin_balance['userAssets']:
            free = float(asset['free'])
            borrowed = float(asset['borrowed'])
            interest = float(asset['interest'])

            if free != 0 or borrowed != 0 or interest != 0:
                positions.append({
                    'asset': asset['asset'],
                    'free': free,
                    'borrowed': borrowed,
                    'interest': interest,
                    'netAsset': float(asset['netAsset'])
                })

        return positions
