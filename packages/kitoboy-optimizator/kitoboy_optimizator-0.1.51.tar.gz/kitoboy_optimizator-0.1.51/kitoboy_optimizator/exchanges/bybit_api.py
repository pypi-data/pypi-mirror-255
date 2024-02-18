from pybit.unified_trading import HTTP
import numpy as np
import asyncio
from kitoboy_optimizator.exchanges.utils import filter_rows_within_time_range


DATA_SIZE_LIMIT = 1000

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
    async def fetch_futures_ohlcv(symbol, interval, start_timestamp: int, end_timestamp: int, limit: int = DATA_SIZE_LIMIT) -> np.ndarray:
        client = HTTP(testnet=False)
        category = "linear"
        interval_corrected = kline_intervals[interval]

        ohlcv = []
        since = start_timestamp
        end = end_timestamp
        await asyncio.sleep(0.1) # for async oportunity to get other data
        while since < end:
            klines = client.get_kline(
                symbol=symbol,
                interval=interval_corrected,
                start=str(since),
                limit=limit,
                category=category
            )['result']['list']

            if not klines:
                break

            #ByBit return data in reverse
            ohlcv.extend(klines[::-1])
            # Update start_timestamp for the next batch
            since = int(ohlcv[-1][0]) + 1
            await asyncio.sleep(0.5) 
        
        result_ohlcv = np.array(ohlcv)[:, :6].astype(float)
        return filter_rows_within_time_range(data=result_ohlcv, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    

    @staticmethod
    async def get_futures_symbol_params(symbol) -> dict:
        client = HTTP(testnet=False)
        symbol_info = client.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        price_precision = float(symbol_info['priceFilter']['tickSize'])
        qty_precision = float(symbol_info['lotSizeFilter']['qtyStep'])

        return {
            "symbol": symbol,
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
    




async def main():
    start_timestamp = 1609459200000
    start_timestamp = 1702724400000
    # start_timestamp = 1706724400000
    end_timestamp = 1706826509000
    symbol = "SOLUSDT"
    api = BybitAPI(api_key="", api_secret="")
    ohlcv = await api.fetch_futures_ohlcv(
        symbol=symbol,
        interval="1h",
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    symbol_params = await api.get_futures_symbol_params(symbol)


    # print(ohlcv)
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