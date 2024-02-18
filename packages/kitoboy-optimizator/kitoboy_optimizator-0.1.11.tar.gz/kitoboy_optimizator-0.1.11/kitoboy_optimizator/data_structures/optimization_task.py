from kitoboy_optimizator.enums import Exchangies, Strategies


class OptimizationTask:
    def __init__(
        self,
        id: str,
        group_id: str,
        strategy: Strategies,
        exchange: Exchangies,
        symbol: str,
        interval: str,
        start_timestamp: int,
        end_timestamp: int,
        optimizer_options: dict,
        backtest_options: dict,
    ):
        self.id = id
        self.group_id = group_id
        self.strategy = strategy
        self.exchange = exchange
        self.symbol = symbol
        self.interval = interval
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.optimizer_options = optimizer_options
        self.backtest_options = backtest_options
