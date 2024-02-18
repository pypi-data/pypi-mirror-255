import random
import numpy as np
import datetime as dt
import os

from kitoboy_optimizator.report_builder import StrategyTestResultCalculator, Reporter, HTMLBuilder
from kitoboy_optimizator.backtester import Backtester
from kitoboy_optimizator.downloader import HistoricalDataManager
from kitoboy_optimizator.enums import Exchangies


class Optimizer:

    def __init__(
        self,
        optimization_id: str,
        optimization_group_id: str,
        strategy,
        symbol: str,
        optimizer_options: dict,
        backtest_options: dict,
        forwardtest_options: dict,
        exchange: Exchangies,
        # ohlcv: np.ndarray,
        interval: str,
        data_manager: HistoricalDataManager,
        # symbol_params: dict,
        results_dir: str,
        tg_id: int,
    ):
        self.strategy = strategy
        self.iterations = optimizer_options.get("iterations")
        self.number_of_starts = optimizer_options.get("number_of_starts")
        self.optimization_type = optimizer_options.get("optimization_type")
        self.min_max_drawdown = optimizer_options.get("min_max_drawdown")
        self.population_size = optimizer_options.get("population_size")
        self.max_population_size = optimizer_options.get("max_population_size")
        self.mutation_probability = optimizer_options.get("mutation_probability")
        self.assimilation_probability = optimizer_options.get(
            "assimilation_probability"
        )
        self.final_results = optimizer_options.get("final_results")
        self.backtest_options = backtest_options
        self.forwardtest_options = forwardtest_options
        self.exchange = exchange
        self.exchange_name = exchange.value
        # self.ohlcv = ohlcv
        self.interval = interval
        # self.start_timestamp = int(0.001 * ohlcv[0, 0])
        # self.end_timestamp = int(0.001 * ohlcv[-1, 0])
        self.start_timestamp = optimizer_options.get('start_timestamp')
        self.end_timestamp = optimizer_options.get('end_timestamp')
        self.data_manager = data_manager
        # self.symbol_params = symbol_params
        self.symbol = symbol
        self.start_forwardtest_after_optimization = optimizer_options.get("start_forwardtest_after_optimization")

        self.backtester = Backtester()
        self.reporter = Reporter(
            optimization_id=optimization_id,
            optimization_group_id=optimization_group_id,
            tg_id=tg_id,
            strategy_name=strategy.name,
            exchange_name=exchange.value,
            symbol=symbol,
            interval=interval,
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            reports_dir=results_dir,
        )
        self.html_builder = HTMLBuilder()
        self.html_builder.init_bootstrap_folder(os.path.join(results_dir, "html/"))
        # self.strategy_test_result_calculator = StrategyTestResultCalculator()
        self.results_dir = results_dir

        # self.backtest_options["leverage"] = 1  # Make optimization without leverage

    async def execute(self):
        await self.prepare_execution()
        self.reporter.report_start_optimization()

        for i in range(self.number_of_starts):
            print(
                f"{self.strategy.name} {self.symbol} {self.interval} loop #{i+1}"
            )
            try: 
                self.create_initial_population()
            except Exception as e:
                print(f"Error of creating popuation: {e}")

            for j in range(self.iterations):
                self.iteration = j + 1
                self.select()
                self.cross()
                self.mutate()
                self.expand()
                self.assimilate()
                self.elect()
                self.kill()

            print("Let's process results!")
            for i in range(self.final_results):
                await self.process_results()

        await self.reporter.finish_optimisation()

    
    async def prepare_execution(self):
        self.symbol_params = await self.data_manager.get_symbol_params(
            exchange=self.exchange,
            symbol=self.symbol
        )
        self.ohlcv = await self.data_manager.get_ohlcv(
            exchange=self.exchange,
            symbol=self.symbol,
            interval=self.interval,
            start_timestamp=self. start_timestamp,
            end_timestamp=self.end_timestamp
        )


    def create_initial_population(self):
        self.samples = [
            [random.choice(j) for j in self.strategy.opt_parameters.values()]
            for i in range(self.population_size)
        ]
        self.population = {
            k[0]: (v, k[1], k[2])
            for k, v in zip(map(self.fit, self.samples), self.samples)
        }
        self.sample_length = len(self.strategy.opt_parameters)
        self.actual_population_size = len(self.population)
        self.best_score = float("-inf")
        self.reporter.report_initial_population(self.population)
        return self.population

    def fit(self, sample):
        log = self.backtester.execute_backtest(
            strategy=self.strategy,
            strategy_params=sample,
            ohlcv=self.ohlcv,
            symbol_params=self.symbol_params,
            backtest_options=self.backtest_options,
        )
        metrics = StrategyTestResultCalculator.get_optimized_metrics(
            log, self.backtest_options.get("initial_capital")
        )

        if self.optimization_type == 0:
            score = metrics[0]
        else:
            if metrics[1] > self.min_max_drawdown:
                score = metrics[0] / metrics[1]
            else:
                score = 0

        metrics = (score, metrics[0], metrics[1])
        return metrics

    def select(self):
        if random.randint(0, 1) == 0:
            score = self.__get_best_score_of_population(self.population)
            parent_1 = self.population[score][0]
            population_copy = self.population.copy()
            del population_copy[score]
            parent_2 = random.choice(list(population_copy.values()))[0]
            self.parents = [parent_1, parent_2]
        else:
            parents = random.sample(list(self.population.values()), 2)
            self.parents = [parents[0][0], parents[1][0]]

    def cross(self):
        r_number = random.randint(0, 1)

        if r_number == 0:
            delimiter = random.randint(1, self.sample_length - 1)
            self.child = self.parents[0][:delimiter] + self.parents[1][delimiter:]
        else:
            delimiter_1 = random.randint(1, self.sample_length // 2 - 1)
            delimiter_2 = random.randint(self.sample_length // 2 + 1, self.sample_length - 1)
            self.child = (
                self.parents[0][:delimiter_1]
                + self.parents[1][delimiter_1:delimiter_2]
                + self.parents[0][delimiter_2:]
            )

    def mutate(self):
        if random.randint(0, 100) < self.mutation_probability:
            gene_number = random.randint(0, self.sample_length - 1)
            gene_value = random.choice(
                list(self.strategy.opt_parameters.values())[gene_number]
            )
            self.child[gene_number] = gene_value

    def expand(self):
        metrics = self.fit(self.child)
        self.population[metrics[0]] = (self.child, metrics[1], metrics[2])
        self.reporter.report_expand_results(self.population[metrics[0]])
        return self.population[metrics[0]]

    def assimilate(self):
        if random.randint(0, 1000) / 10 < self.assimilation_probability:
            samples = [
                [random.choice(j) for j in self.strategy.opt_parameters.values()]
                for i in range(len(self.population) // 2)
            ]
            population = {
                k[0]: (v, k[1], k[2]) for k, v in zip(map(self.fit, samples), samples)
            }
            self.population.update(population)
            self.reporter.report_assimilation_results(population)
            return population

    def elect(self):
        if self.best_score < self.__get_best_score_of_population(self.population):
            self.best_score = self.__get_best_score_of_population(self.population)
            self.reporter.report_new_best_scores(self.iteration, self.best_score)
        return self.best_score

    def kill(self):
        while len(self.population) > self.max_population_size:
            del self.population[min(self.population)]

    async def process_results(self):
        # print("Process results")
        best_params = self.population[self.best_score][0]
        result_id = f"{int(1000 * dt.datetime.now().timestamp())}_{random.randint(0, 100)}"
        backtest_report_text = await self.create_and_save_results_report(
            strategy_params=best_params,
            initial_capital=self.backtest_options.get("initial_capital"),
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            result_id=result_id)
        # print("Backtest results processed!")
        self.reporter.report_optimization_results(backtest_report_text)
        if self.start_forwardtest_after_optimization:

            forwardtest_report_text = await self.create_and_save_results_report(
                strategy_params=best_params,
                initial_capital=self.backtest_options.get("initial_capital"),
                start_timestamp=self.forwardtest_options.get('start_timestamp'),
                end_timestamp=self.forwardtest_options.get('end_timestamp'),
                result_id=result_id)
            self.reporter.report_optimization_results(forwardtest_report_text)

        del self.population[self.best_score]
        self.best_score = self.__get_best_score_of_population(self.population)
        


    def __generate_txt(self, strategy_params: dict) -> str:
        result = ""
        for key, param_name in enumerate(self.strategy.opt_parameters.keys()):
            if isinstance(strategy_params[key], np.ndarray):
                param_value = list(strategy_params[key])
            else:
                param_value = strategy_params[key]
            result += f"{param_name} = {param_value}\n"
        return result


    def __get_best_score_of_population(self, population: np.ndarray) -> float:
        best_score = max(population)
        return best_score
    

    # async def execute_forwardtest(self, strategy_params: dict):
    #     ohlcv = await self.data_manager.get_ohlcv(
    #         exchange=self.exchange_name,
    #         symbol=self.symbol,
    #         interval=self.interval,
    #         start_timestamp=self.forwardtest_options.get('start_timestamp'),
    #         end_timestamp=self.forwardtest_options.get('end_timestamp')
    #     )
    #     forwardtest_log = self.backtester.execute_backtest(
    #         strategy=self.strategy,
    #         strategy_params=strategy_params,
    #         ohlcv=ohlcv,
    #         symbol_params=self.symbol_params,
    #         backtest_options=self.backtest_options,
    #     )
    #     return forwardtest_log
    

    async def create_and_save_results_report(self, strategy_params: dict, initial_capital: float, start_timestamp: int, end_timestamp: int, result_id: str):
        print("Downloading OHLCV for final results")
        print("start timestamp: ", start_timestamp)
        print("end timestamp: ", end_timestamp)
        print(f"strategy params: {strategy_params}")
        print(f"result id: {result_id}")
        print(f"initial capital: {initial_capital}")
        ohlcv = await self.data_manager.get_ohlcv(
            exchange=self.exchange,
            symbol=self.symbol,
            interval=self.interval,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        print("execute test")
        backtest_log = self.backtester.execute_backtest(
            strategy=self.strategy,
            strategy_params=strategy_params,
            ohlcv=ohlcv,
            symbol_params=self.symbol_params,
            backtest_options=self.backtest_options,
        )
        print("calculate metrics")
        net_profit, max_drawdown = StrategyTestResultCalculator.get_optimized_metrics(backtest_log, initial_capital)
        print(f"net profit: {net_profit}, max drawdown: {max_drawdown}")

        html = self.html_builder.generate_html(
            strategy_name=self.strategy.name,
            exchange_name=self.exchange_name,
            symbol = self.symbol,
            interval=self.interval,
            log = backtest_log, 
            initial_capital=self.backtest_options.get("initial_capital")
        )
        print(f"Strategy params for txt: {strategy_params}")
        txt = self.__generate_txt(strategy_params)

        html_file_path = os.path.join(f"{self.results_dir}/html/{self.strategy.name}/{self.exchange_name}", f"{self.symbol}_{self.interval}_{result_id}_{start_timestamp}_{end_timestamp}_{net_profit}_{max_drawdown}.html")
        txt_file_path = os.path.join(f"{self.results_dir}/txt/{self.strategy.name}/{self.exchange_name}", f"{self.symbol}_{self.interval}_{result_id}.txt")
        txt_file_dir = os.path.dirname(txt_file_path)
        html_file_dir = os.path.dirname(html_file_path)
        if not os.path.exists(txt_file_dir):
            os.makedirs(txt_file_dir)
        if not os.path.exists(html_file_dir):
            os.makedirs(html_file_dir)
        with open(html_file_path, "w") as f:
            f.write(html)
        with open(txt_file_path, "w") as f:
            f.write(txt)

        net_profit = strategy_params[1]
        max_drawdown = strategy_params[2]

        start_time = dt.datetime.utcfromtimestamp(self.start_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        end_time = dt.datetime.utcfromtimestamp(self.end_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        report_text = f"""Period: {start_time} — {end_time}
Net profit, %: {str(net_profit)}
Max drawdown, %: {str(max_drawdown)}
{"=" * 35}
{txt}
{"=" * 35}
"""        
        return report_text