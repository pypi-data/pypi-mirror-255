from pybit.unified_trading import HTTP
import numpy as np
import asyncio


kline_intervals = {
        1: 1, '1m': 1,
        3: 3, '3m': 3,
        5: 5, '5m': 5,
        15: 15, '15m': 15,
        30: 30, '30m': 30,
        60: 60, '1h': 60,
        120: 120, '2h': 120,
        240: 240, '4h': 240,
        360: 360, '6h': 360,
        720: 720, '12h': 720,
        'D': 'D', '1d': 'D',
        'W': 'W', '1w': 'W',
        'M': 'M', '1M': 'M'
    }

class BybitAPI():


    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.client = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)

    
    @staticmethod
    async def fetch_futures_ohlcv(symbol, interval, start_timestamp: int, end_timestamp: int) -> np.ndarray:
        client = HTTP(testnet=False)
        category = "linear"
        interval = kline_intervals[interval]

        # ohlcv_batch = client.get_kline(
        #         category=category,
        #         symbol=symbol,
        #         interval=interval,
        #         start=start_timestamp,
        #         limit=1000
        #     )
        # print(f"\n\nOHLCV Batch:\n{ohlcv_batch}")
        ohlcv = np.array(
            client.get_kline(
                category=category,
                symbol=symbol,
                interval=interval,
                start=start_timestamp,
                limit=1000
            )['result']['list']
        )[:0:-1, :6].astype(float)

        while True:
            await asyncio.sleep(1)
            start_timestamp = int(ohlcv[-1, 0])

            if start_timestamp >= end_timestamp:
                ohlcv = ohlcv[
                    : np.where(ohlcv[:, 0] == end_timestamp)[0][0]
                ]
                break
            else:
                last_ohlcv_batch = np.array(
                    client.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval,
                        start=start_timestamp,
                        limit=1000
                    )['result']['list']
                )[-2:0:-1, :6].astype(float)

                if last_ohlcv_batch.shape[0] > 0:
                    ohlcv = np.vstack((ohlcv, last_ohlcv_batch))
                else:
                    break
        return ohlcv
    

    @staticmethod
    async def get_futures_symbol_params(symbol) -> dict:
        client = HTTP(testnet=False)
        symbol_info = client.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        price_precision = float(symbol_info['priceFilter']['tickSize'])
        qty_precision = float(symbol_info['lotSizeFilter']['qtyStep'])

        return {
            "price_precision": price_precision,
            "qty_precision": qty_precision
        }


    @staticmethod
    def get_futures_price_precision(symbol: str):
        client = HTTP(testnet=False)
        symbol_info = client.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        return float(symbol_info['priceFilter']['tickSize'])


    @staticmethod
    def get_futures_qty_precision(symbol):
        client = HTTP(testnet=False)
        symbol_info = client.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        return float(symbol_info['lotSizeFilter']['qtyStep'])