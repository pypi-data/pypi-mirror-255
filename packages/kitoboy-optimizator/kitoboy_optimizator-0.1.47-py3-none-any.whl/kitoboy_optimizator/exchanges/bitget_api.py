# https://www.bitget.com/api-doc/contract/market/Get-History-Candle-Data
# curl "https://api.bitget.com/api/v2/mix/market/history-candles?symbol=BTCUSDT&granularity=1W&limit=200&productType=usdt-futures"
import numpy as np
import asyncio
from enum import Enum
import aiohttp
import datetime as dt
from kitoboy_optimizator.exchanges.utils import filter_rows_within_time_range

DATA_SIZE_LIMIT = 100

class ProductType(Enum):
    USDT_FUTURES = "usdt-futures"
    COIN_FUTURES = "coin-futures"
    USDC_FUTURES = "usdc-futures"
    SUSDT_FUTURES = "s-usdt-futures"
    SCOIN_FUTURES = "s-coin_futures"
    SUSDC_FUTURES = "s-usdc-futures"


interval_step = {
    "1m": 60*1000,
    "3m": 60*1000*3,
    "5m": 60*1000*5,
    "15m": 60*1000*15,
    "30m": 60*1000*30,
    "1H": 60*1000*60,
    "4H": 60*1000*60*4,
    "6H": 60*1000*60*6,
    "12H": 60*1000*60*12,
    "1D": 60*1000*60*24,
    "1W": 60*1000*60*24*7,
    "1M": 60*1000*60*24*30
}

timeframes = {
    "1m": "1m",
    "3m": "3m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1H",
    "4h": "4H",
    "6h": "6H",
    "12h": "12H",
    "1d": "1D",
    "1w": "1W",
    "1M": "1M"
}

class BitgetAPI:
    BASE_URL = "https://api.bitget.com"

    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret

    async def fetch_futures_ohlcv(
        self, symbol: str, timeframe: str, start_timestamp: int, end_timestamp: int
    ) -> np.ndarray:
        http_session = aiohttp.ClientSession()
        product_type = ProductType.USDT_FUTURES
        
        timeframe = timeframes.get(timeframe)
    
        since = start_timestamp 
        end = end_timestamp
        # prev_timestamp = start_timestamp - 60*60*1000
        all_ohlcv = []
        try:
            while since < end:
                # print(f"since: {since} end: {end}")
                ohlcv = await self.__fetch_historical_candlestick_from_api(
                    http_session=http_session, 
                    symbol=symbol, 
                    timeframe=timeframe, 
                    product_type=product_type,
                    start_timestamp=since, 
                    limit=DATA_SIZE_LIMIT
                )
                if not ohlcv:
                    break  # No more data available
                all_ohlcv.extend(ohlcv)
                since = self.__get_end_time_for_historical_data_request(start_time=int(ohlcv[-1][0]), timeframe=timeframe, limit=1)  # Set 'since' to the timestamp of the last fetched candle + 1 millisecond
                await asyncio.sleep(0.5)

            result_ohlcv = np.array(all_ohlcv)[:, :6].astype(float)
        
        except Exception as e:
            print(f"Bitget API error: {e}")
            raise e
        finally:
            await http_session.close()

        return filter_rows_within_time_range(data=result_ohlcv, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
        

    async def get_futures_symbol_params(self, symbol: str) -> dict:
        http_session = aiohttp.ClientSession()
        try:
            symbol_info = await self.__fetch_spot_symbol_parameters_from_api(
                http_session=http_session, symbol=symbol
            )
        except Exception as e:
            print(f"Bitget API error: {e}")
            raise e
        finally:
            await http_session.close()

        price_precision = float(pow(10, -int(symbol_info['pricePrecision'])))
        qty_precision = float(pow(10, -int(symbol_info['quantityPrecision'])))

        return {
            "symbol": symbol,
            "price_precision": price_precision,
            "qty_precision": qty_precision
        }
    

    @classmethod
    async def __fetch_historical_candlestick_from_api(
        cls,
        http_session: aiohttp.ClientSession,
        symbol: str,
        timeframe: str,
        product_type: ProductType,
        start_timestamp: int,
        end_timestamp: int | None = None,
        limit: int = DATA_SIZE_LIMIT,
    ) -> list:
        endpoint = "/api/v2/mix/market/history-candles"
        if not end_timestamp:
            end_timestamp = cls.__get_end_time_for_historical_data_request(
                start_time=start_timestamp, 
                timeframe=timeframe,
                limit=limit
            )

        params = {
            "symbol": symbol,
            "granularity": timeframe,
            "startTime": start_timestamp,
            "endTime": end_timestamp,
            "limit": limit,
            "productType": product_type.value,
        }
        url = f"{cls.BASE_URL}{endpoint}"

        async with http_session.get(url, params=params) as resp:
            response_json = await resp.json()
            # print(response_json)
            if resp.status == 200:
                return response_json["data"]
            else:
                # print(resp.status)
                # print(response_json)
                raise Exception(response_json["msg"])
            

    @classmethod
    def __get_end_time_for_historical_data_request(cls, start_time: int, timeframe: str, limit:int = DATA_SIZE_LIMIT) -> int:
        end_time = start_time + limit * interval_step.get(timeframe)
        return end_time
    

    @classmethod
    async def __fetch_spot_symbol_parameters_from_api(cls, http_session: aiohttp.ClientSession, symbol: str) -> dict:
        endpoint = "/api/v2/spot/public/symbols"
        params = {
            "symbol": symbol
        }
        url = f"{cls.BASE_URL}{endpoint}"
        async with http_session.get(url, params=params) as resp:
            response_json = await resp.json()
            if resp.status == 200:
                return response_json["data"][0]
            else:
                raise Exception(response_json["msg"])



def print_timedelta(start: int, end: int):
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    
    # Calculate timedelta
    delta = end - start
    
    # Extract days, seconds and then hours and minutes from seconds
    days = delta.days
    seconds_in_day = delta.seconds
    hours = seconds_in_day // 3600
    minutes = (seconds_in_day % 3600) // 60

    total_seconds = delta.total_seconds()
    total_hours = total_seconds // 3600
    total_minutes = total_seconds // 60
    
    print(f"{days} days, {hours} hours and {minutes} minutes")
    print(f"HOURS: {total_hours}")
    print(f"MINUTES: {total_minutes}")


def get_timedelta_in_hours(start: int, end: int) -> float:
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    # Calculate timedelta
    delta = end - start
    total_seconds = delta.total_seconds()
    total_hours = total_seconds // 3600
    return total_hours


def get_timedelta_in_minutes(start: int, end: int) -> float:
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    # Calculate timedelta
    delta = end - start
    total_seconds = delta.total_seconds()
    total_hours = total_seconds // 60
    return total_hours

def get_timedelta_in_days(start: int, end: int) -> float:
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    # Calculate timedelta
    delta = end - start
    return delta.days






async def main():
    start_timestamp = 1609459200000
    # start_timestamp = 1625000400000
    # start_timestamp = 1622000400000
    start_timestamp = 1702724400000
    # start_timestamp = 1706724400000
    end_timestamp = 1706826509000
    symbol = "SOLUSDT"
    api = BitgetAPI(api_key="", api_secret="")
    ohlcv = await api.fetch_futures_ohlcv(
        symbol=symbol,
        timeframe="1h",
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    symbol_params = await api.get_futures_symbol_params(symbol)


    print(ohlcv)
    print(f"len: {len(ohlcv)}")
    print_timedelta(start=start_timestamp, end=end_timestamp)
    for item in ohlcv[:3,0]:
        print(item)
    for item in ohlcv[-3:,0]:
        print(item)
    # print(ohlcv[:1,0][0])
    # print(ohlcv[-1:,0][0])
    print("Timedelta in hours:", get_timedelta_in_hours(ohlcv[:1,0][0], ohlcv[-1:,0][0]))
    print("Timedelta in minutes:", get_timedelta_in_minutes(ohlcv[:1,0][0], ohlcv[-1:,0][0]))
    print(f"Symbol params: {symbol_params}")



async def test_mvp():
    pass




if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
