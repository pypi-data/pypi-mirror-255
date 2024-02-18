import binance
import numpy as np
import asyncio
from kitoboy_optimizator.exchanges.utils import filter_rows_within_time_range

# DATA_SIZE_LIMIT = 5

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
    async def fetch_futures_ohlcv(symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> np.ndarray:
        client = binance.Client(testnet=False)
        interval_corrected = kline_intervals[interval]

        ohlcv = []
        since = start_timestamp
        end = end_timestamp
        await asyncio.sleep(0.1) # for async oportunity to get other data
        while since < end:
            klines = client.get_historical_klines(
                symbol=symbol,
                interval=interval_corrected,
                start_str=str(since),
                end_str=str(end),
            )
            if not klines:
                break

            ohlcv.extend(klines)
            # Update start_timestamp for the next batch
            since = int(klines[-1][0]) + 1
            await asyncio.sleep(0.5) 

        result_ohlcv = np.array(ohlcv)[:, :6].astype(float)

        return filter_rows_within_time_range(data=result_ohlcv, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    

    @staticmethod
    async def get_futures_symbol_params(symbol) -> dict:
        client = binance.Client(testnet=False)
        symbols_info = client.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        price_precision = float(symbol_info['filters'][0]['tickSize'])
        qty_precision = float(symbol_info['filters'][1]['minQty'])

        return {
            "symbol": symbol,
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
    

async def main():
    start_timestamp = 1609459200000
    # start_timestamp = 1625000400000
    # start_timestamp = 1622000400000
    start_timestamp = 1702724400000
    # start_timestamp = 1706724400000
    end_timestamp = 1706826509000
    symbol = "SOLUSDT"
    api = BinanceAPI(api_key="", api_secret="")
    ohlcv = await api.fetch_futures_ohlcv(
        symbol=symbol,
        interval="1h",
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    symbol_params = await api.get_futures_symbol_params(symbol)


    print(ohlcv)
    print(f"len: {len(ohlcv)}")
    # print_timedelta(start=start_timestamp, end=end_timestamp)
    for item in ohlcv[:10,0]:
        print(item)
    for item in ohlcv[-10:,0]:
        print(item)
    # print(ohlcv[:1,0][0])
    # print(ohlcv[-1:,0][0])
    # print("Timedelta in hours:", get_timedelta_in_hours(ohlcv[:1,0][0], ohlcv[-1:,0][0]))
    # print("Timedelta in minutes:", get_timedelta_in_minutes(ohlcv[:1,0][0], ohlcv[-1:,0][0]))
    print(f"Symbol params: {symbol_params}")



if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

