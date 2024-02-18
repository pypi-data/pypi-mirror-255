import os
from concurrent.futures import ProcessPoolExecutor
import asyncio
from typing import Callable

from kitoboy_optimizator.enums import Exchangies
from kitoboy_optimizator.downloader import HistoricalDataManager
from kitoboy_optimizator.data_structures import OptimizationTask
from kitoboy_optimizator.utils import (
    generate_optimization_tasks_list,
    generate_downloading_tasks_list,
)
from kitoboy_optimizator.optimizer import Optimizer

class MultyOptimizer:

    def __init__(self, data_dir: str, results_dir: str, tg_id: int):

        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        self.data_manager = HistoricalDataManager(data_dir)
        self.results_dir = results_dir
        self.tg_id = tg_id


    async def prepare_ohlcv(
        self,
        symbols: [str],
        intervals: [str],
        start_timestamp: int,
        end_timestamp: int,
        exchanges: [Exchangies]       
    ):
        downloading_tasks = generate_downloading_tasks_list(
            symbols=symbols,
            intervals=intervals,
            start=start_timestamp,
            end=end_timestamp,
            exchanges=exchanges,
        )
        await self.data_manager.execute_downloading_tasks(downloading_tasks)


    async def prepare_optimization_tasks(
        self,
        symbols: [str],
        intervals: [str],
        start_timestamp: int,
        end_timestamp: int,
        exchanges: [Exchangies],
        strategies: [Callable],
        optimizer_options: dict,
        backtest_options: dict,
    ) -> [OptimizationTask]:
        
        optimization_tasks = generate_optimization_tasks_list(
            symbols=symbols,
            intervals=intervals,
            start=start_timestamp,
            end=end_timestamp,
            exchanges=exchanges,
            strategies=strategies,
            optimizer_options=optimizer_options,
            backtest_options=backtest_options,
        )

        return optimization_tasks
        

    def sync_wrapper_execute_optimization_task(self, task):
        """
        Synchronous wrapper for the optimization task to be executed in the process pool.
        This function should handle converting the async `__execute_optimization_task` logic
        into a synchronous call, possibly using asyncio.run if needed.
        """
        try:
            print(f"START optimization {task.strategy.name} {task.symbol} {task.interval} {task.exchange.value}")
            result = asyncio.run(self.__execute_optimization_task(task))
            
        except Exception as e:
            print(f"FAILED to execute optimization task: {e}\n {task.strategy.name} {task.symbol} {task.interval} {task.exchange.value}\n")
        return result


    async def execute_optimizations(self, tasks: [OptimizationTask], max_cpu_threads=1):
        available_cpu_cores = os.cpu_count()

        if max_cpu_threads > 0:
            cores_for_use = min(available_cpu_cores, max_cpu_threads)
        elif max_cpu_threads < 0:
            cores_for_use = max(1, available_cpu_cores + max_cpu_threads)
        else:
            cores_for_use = available_cpu_cores

        print(f"Доступно {available_cpu_cores} ядер CPU!")
        if cores_for_use == available_cpu_cores:
            print("LET'S MAKE THEM SCREAM! $)")
        else:
            print(f"Optimization will use {cores_for_use} CPU cores")

        with ProcessPoolExecutor(max_workers=cores_for_use) as executor:
            # Map each job to a separate process
            results = list(executor.map(self.sync_wrapper_execute_optimization_task, tasks))

        print("ALL OPTIMIZATIONS FINISHED!")


    async def __execute_optimization_task(self, task: OptimizationTask):
        ohlcv = await self.data_manager.get_ohlcv(
                exchange=task.exchange,
                symbol=task.symbol,
                interval=task.interval,
                start_timestamp=task.start_timestamp,
                end_timestamp=task.end_timestamp
            )
        symbol_params = await self.data_manager.get_symbol_params(
            exchange=task.exchange,
            symbol=task.symbol
        )
        # strategy_class = StrategySelector().get_strategy_class(task.strategy)
        strategy_class = task.strategy
        optimizer = Optimizer(
            optimization_id=task.id,
            optimization_group_id=task.group_id,
            tg_id=self.tg_id,
            strategy=strategy_class,
            optimizer_options=task.optimizer_options,
            backtest_options=task.backtest_options,
            exchange_name=task.exchange.value,
            ohlcv=ohlcv,
            interval=task.interval,
            symbol_params=symbol_params,
            results_dir=self.results_dir
        )
        await optimizer.execute()