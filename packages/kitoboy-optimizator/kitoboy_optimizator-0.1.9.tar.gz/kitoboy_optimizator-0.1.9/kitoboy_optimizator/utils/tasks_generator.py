import uuid
from kitoboy_optimizator.enums import Exchangies, Strategies
from kitoboy_optimizator.data_structures import DownloadingTask, OptimizationTask


def generate_downloading_tasks_list(
    symbols: [str], intervals: [str], start: int, end: int, exchanges: [Exchangies]
):
    tasks = []
    for symbol in symbols:
        for interval in intervals:
            for exchange in exchanges:
                tasks.append(
                    DownloadingTask(
                        exchange=exchange,
                        symbol=symbol,
                        interval=interval,
                        start_timestamp=start,
                        end_timestamp=end,
                    )
                )
    return tasks


def generate_optimization_tasks_list(
    symbols: [str],
    intervals: [str],
    start: int,
    end: int,
    exchanges: [Exchangies],
    strategies: [Strategies],
    optimizer_options: dict,
    backtest_options: dict,
) -> list[OptimizationTask]:
    tasks = []
    super_id = str(uuid.uuid4())
    for strategy in strategies:
        for exchange in exchanges:
            for symbol in symbols:
                for interval in intervals:
                    optimization_id = str(uuid.uuid4())
                    tasks.append(
                        OptimizationTask(
                            strategy=strategy,
                            exchange=exchange,
                            symbol=symbol,
                            interval=interval,
                            start_timestamp=start,
                            end_timestamp=end,
                            optimizer_options=optimizer_options,
                            backtest_options=backtest_options,
                            id=optimization_id,
                            group_id=super_id
                        )
                    )
    return tasks
