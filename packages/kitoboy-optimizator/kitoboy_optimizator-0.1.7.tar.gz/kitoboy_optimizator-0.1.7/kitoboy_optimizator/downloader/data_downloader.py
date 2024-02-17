import asyncio
import os
import numpy as np

from kitoboy_optimizator.enums import Exchangies
from kitoboy_optimizator.data_structures import DownloadingTask
from kitoboy_optimizator.exchanges import BinanceAPI, BybitAPI


class HistoricalDataManager:
    
    def __init__(self, data_dir: str):
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_dir = data_dir
        print(f"Data dir: {data_dir}")


    async def execute_downloading_tasks(self, tasks: [DownloadingTask]):
        print("Start downloading data...")
        downloading_jobs = []
        for task in tasks:
            filepath = self.get_ohlcv_filepath(task.exchange.value, task.symbol, task.interval, task.start_timestamp, task.end_timestamp)
            if not os.path.exists(filepath):
                downloading_jobs.append(asyncio.create_task(self.download_and_save_ohlcv(task, filepath)))

        await asyncio.gather(*downloading_jobs)
        print("Data downloaded!")


    def get_ohlcv_filepath(self, exchange_name: str, symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> str:
        if exchange_name == "binance_futures":
            subfolder = "binance/futures"
        elif exchange_name == "bybit_futures":
            subfolder = "bybit/futures"
        else:
            raise ValueError(f"Exchange {exchange_name} is not supported for ohlcv downloading!")
        
        return f"{self.data_dir}/{subfolder}/{symbol}_{interval}_{str(start_timestamp)}_{str(end_timestamp)}.csv"
    

    async def download_and_save_ohlcv(self, task:DownloadingTask, filepath: str) -> np.ndarray:
        print(f"Downloading {task.symbol} {task.interval}: {task.start_timestamp}-{task.end_timestamp} from {task.exchange.value}")
        ohlcv = await self.fetch_ohlcv(task)
        save_np_to_csv(filepath=filepath, data=ohlcv)
        print(f"{task.symbol} {task.interval}: {task.start_timestamp}-{task.end_timestamp} from {task.exchange.value} saved at {filepath}")
        return ohlcv


    async def fetch_ohlcv(self, task: DownloadingTask):
        if task.exchange == Exchangies.BINANCE_FUTURES:
            ohlcv = await get_ohlcv_from_binance_futures(task.symbol, task.interval, task.start_timestamp, task.end_timestamp)
        elif task.exchange == Exchangies.BYBIT_FUTURES:
            ohlcv = await get_ohlcv_from_bybit_futures(task.symbol, task.interval, task.start_timestamp, task.end_timestamp)
        else:
            raise ValueError(f"Exchange {task.exchange.value} is not supported.")
        return ohlcv
    

    async def get_ohlcv(self, exchange: Exchangies, symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> np.ndarray:
        filepath = self.get_ohlcv_filepath(exchange.value, symbol, interval, start_timestamp, end_timestamp)
        if not os.path.exists(filepath):
            task = DownloadingTask(
                exchange=exchange,
                symbol=symbol,
                interval=interval,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp
            )
            ohlcv = await self.download_and_save_ohlcv(task, filepath)
        else:
            ohlcv = np.loadtxt(filepath, delimiter=',')
        return ohlcv
    

    async def get_symbol_params(self, exchange: Exchangies, symbol: str) -> dict:
        if exchange == Exchangies.BINANCE_FUTURES:
            params = await BinanceAPI.get_futures_symbol_params(symbol)
        elif exchange == Exchangies.BYBIT_FUTURES:
            params = await BybitAPI.get_futures_symbol_params(symbol)
        else:
            raise ValueError(f"Exchange {exchange.value} is not supported.")
        params["symbol"] = symbol
        return params



async def get_ohlcv_from_binance_futures(symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> np.ndarray:

    return await BinanceAPI.fetch_futures_ohlcv(
        symbol=symbol,
        interval=interval,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp
    )


async def get_ohlcv_from_bybit_futures(symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> np.ndarray:

    return await BybitAPI.fetch_futures_ohlcv(
        symbol=symbol,
        interval=interval,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp
    )

def save_np_to_csv(filepath: str, data: np.array, delimiter: str = ','):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    np.savetxt(filepath, data, delimiter=delimiter)
