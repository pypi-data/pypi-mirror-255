import binance
import numpy as np
import asyncio


kline_intervals = {
        '1m': '1m', 1: '1m',
        '3m': '3m', 3: '3m',
        '5m': '5m', 5: '5m',
        '15m': '15m', 15: '15m',
        '30m': '30m', 30: '30m',
        '1h': '1h', 60: '1h',
        '2h': '2h', 120: '2h',
        '4h': '4h', 240: '4h',
        '6h': '6h', 360: '6h',
        '12h': '12h', 720: '12h',
        '1d': '1d', 'D': '1d',
        '1w': '1w', 'W': '1w',
        '1M': '1M', 'M': '1M'   
    }


class BinanceAPI():

    def __init__(self, api_key: str| None = None, api_secret: str| None = None):
        self.client = binance.Client(testnet=False, api_key=api_key, api_secret=api_secret)
    

    @staticmethod
    async def fetch_futures_ohlcv(symbol, interval, start_timestamp: int, end_timestamp: int) -> np.ndarray:
        client = binance.Client(testnet=False)
        interval_corrected = kline_intervals[interval]

        ohlcv = []

        while start_timestamp < end_timestamp:
            await asyncio.sleep(0.1) 
            klines = client.get_historical_klines(
                symbol=symbol,
                interval=interval_corrected,
                start_str=str(start_timestamp),
                end_str=str(end_timestamp),
                limit=1000
            )

            if not klines:
                break

            # Convert and append the new batch
            new_batch = np.array(klines)[:, :6].astype(float)
            ohlcv.append(new_batch)

            # Update start_timestamp for the next batch
            start_timestamp = int(new_batch[-1, 0]) + 1

        # Concatenate all batches into a single array
        ohlcv = np.vstack(ohlcv) if ohlcv else np.array([])

        # Optionally, trim the data to end_timestamp
        ohlcv = ohlcv[ohlcv[:, 0] <= end_timestamp]

        return ohlcv
    

    @staticmethod
    async def get_futures_symbol_params(symbol) -> dict:
        client = binance.Client(testnet=False)
        symbols_info = client.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        price_precision = float(symbol_info['filters'][0]['tickSize'])
        qty_precision = float(symbol_info['filters'][1]['minQty'])

        return {
            "price_precision": price_precision,
            "qty_precision": qty_precision
        }

    

    @staticmethod
    def get_futures_price_precision(symbol):
        client = binance.Client(testnet=False)
        symbols_info = client.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        return float(symbol_info['filters'][0]['tickSize'])
    

    @staticmethod
    def get_futures_qty_precision(symbol):
        client = binance.Client(testnet=False)
        symbols_info = client.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        return float(symbol_info['filters'][1]['minQty'])