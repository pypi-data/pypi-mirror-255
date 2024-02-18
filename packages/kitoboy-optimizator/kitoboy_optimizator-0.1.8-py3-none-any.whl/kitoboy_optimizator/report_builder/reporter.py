import numpy as np
import os
import asyncio
import aiohttp
# import requests
import json

from .numpy_encoder import NumpyEncoder


class Reporter:
    def __init__(
        self,
        optimization_id: str,
        optimization_group_id: str,
        tg_id: int,
        strategy_name: str,
        exchange_name: str,
        symbol: str,
        interval: str,
        start_timestamp: int,
        end_timestamp: int,
        reports_dir: str,
    ):
        self.optimization_id = optimization_id
        self.optimization_group_id = optimization_group_id
        self.tg_user_id = tg_id
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.interval = interval
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.exchange_name = exchange_name
        self.report_filepath = f"{reports_dir}/{strategy_name}/{exchange_name}_{symbol}_{interval}_{start_timestamp}_{end_timestamp}.txt"
        # print(f"Результат оптимизации будет в файле {self.report_filepath}")
        report_dir = os.path.dirname(self.report_filepath)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        self.jobs = []
        self.http_session = aiohttp.ClientSession()

    def report(self, msg: str, *args, **kwargs):
        self.jobs.append(asyncio.create_task(self.handle_report(msg)))
        print(msg)

    def report_optimization_results(self, report_text: str, *args, **kwargs):
        self.jobs.append(
            asyncio.create_task(self.handle_report_optimization_results(report_text))
        )

    def report_start_optimization(self, *args, **kwargs):
        self.jobs.append(asyncio.create_task(self.handle_report_start_optimization()))

    def report_initial_population(self, population: np.ndarray, *args, **kwargs):
        self.jobs.append(
            asyncio.create_task(self.handle_report_initial_population(population))
        )

    def report_expand_results(self, child_metrics, *args, **kwargs):
        self.jobs.append(
            asyncio.create_task(self.handle_report_expand_results(child_metrics))
        )

    def report_assimilation_results(self, new_population, *args, **kwargs):
        self.jobs.append(
            asyncio.create_task(self.handle_report_assimilation_results(new_population))
        )

    def report_new_best_scores(self, iteration: int, best_score, *args, **kwargs):
        self.jobs.append(
            asyncio.create_task(
                self.handle_report_new_best_scores(iteration, best_score)
            )
        )

    async def finish_optimisation(self):
        # finish all tasks
        await asyncio.gather(*self.jobs)
        title = "OPTIMIZATION FINISHED"
        msg = f"\n{title} {self.strategy_name} {self.symbol} {self.interval}"
        await self.send_report(title=title)
        await self.http_session.close()
        print(msg)

    async def handle_report(self, msg: str, title: str = "REPORT"):
        await self.send_report(title=title, msg=msg)
        # print(msg)

    async def handle_report_optimization_results(self, report_text: str):
        title = "OPTIMIZATION RESULTS"
        await self.send_report(title=title, msg=report_text)
        with open(self.report_filepath, "a") as f:
            print(report_text, file=f)
        msg = f"{title} {self.strategy_name} {self.symbol} {self.interval}\n{report_text}\n"
        msg += f"Результат оптимизации сохранены в файл {self.report_filepath}"
        print(msg)

    async def handle_report_start_optimization(self):
        title = "OPTIMIZATION STARTED"
        await asyncio.sleep(0.0001)
        # msg = f"{title} {self.strategy_name} {self.symbol} {self.interval}"
        # print(msg)
        await self.send_report(title=title)

    async def handle_report_initial_population(self, population: dict):
        title = "INITIAL POPULATION"
        await self.send_report(title=title, population=population)

    async def handle_report_expand_results(self, child_metrics):
        title = "EXPAND RESULTS"
        await self.send_report(title=title, population=child_metrics)

    async def handle_report_assimilation_results(self, new_population):
        title = "NEW POPULATION"
        await self.send_report(title=title, population=new_population)

    async def handle_report_new_best_scores(self, iteration, best_score):
        title = "NEW BEST SCORE"
        msg = f"Iteration #{iteration}, score = {best_score}"
        await self.send_report(title=title, msg=msg)
        # print(msg)

    async def send_report(
        self, title: str, msg: str | None = None, population: dict | None = None
    ):
        params = {
            "title": title,
            "exchange_name": self.exchange_name,
            "symbol": self.symbol,
            "interval": self.interval,
            "strategy_name": self.strategy_name,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "optimization_group_id": self.optimization_group_id,
            "optimization_id": self.optimization_id,
        }
        # if self.tg_user_id:
        #     params['tg_user_id'] = self.tg_user_id,
        
        # if population:
        #     population_string = json.dumps(population, cls=NumpyEncoder)
        #     params["population"] = population_string

        # if msg:
        #     params["msg"] = msg

        # # url = "http://webhook.milega.cc/optimizator/new-report"
        url = "https://alan-multy-opt-f166e6abcdf1.herokuapp.com/optimizator/new-report"
        # # url = "http://127.0.0.1:8005/optimizator/new-report"

        max_retries = 7
        retry_count = 0
        while retry_count < max_retries:
            try:
                async with self.http_session.post(url, json=params) as resp:
                    response_json = await resp.json()
                    return response_json  # Assuming you want to do something with this
                # requests.post(url=url, json=params)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Reporter error: {e}\n{self.strategy_name} {self.symbol} {self.interval} {self.exchange_name}")
            except Exception as e:  # Catching other unforeseen exceptions
                print(f"Unexpected error: {e}\n{self.strategy_name} {self.symbol} {self.interval} {self.exchange_name}")
            finally:
                await asyncio.sleep(1)  # Ensure sleep happens regardless of success or failure
                retry_count += 1

        # If loop exits and max retries were reached without a return
        print(f"Max retries reached, unable to send report.\n{self.strategy_name} {self.symbol} {self.interval} {self.exchange_name}")
        # try:
        #     async with self.http_session.post(url, json=params) as resp:
        #         response_json = await resp.json()
        # except Exception as e:
        #     pass