from kitoboy_optimizator.enums import Exchangies

class DownloadingTask:

    def __init__(self, exchange: Exchangies, symbol: str, interval: str, start_timestamp: int, end_timestamp: int):
        self.exchange = exchange
        self.symbol = symbol
        self.interval = interval
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp