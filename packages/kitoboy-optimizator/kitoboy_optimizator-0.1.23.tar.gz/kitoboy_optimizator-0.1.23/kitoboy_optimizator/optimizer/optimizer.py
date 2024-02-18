import random as r
import numpy as np
import datetime as dt
import os

from kitoboy_optimizator.report_builder import StrategyTestResultCalculator, Reporter, HTMLBuilder
from kitoboy_optimizator.backtester import Backtester


class Optimizer:

    def __init__(
        self,
        optimization_id: str,
        optimization_group_id: str,
        strategy,
        optimizer_options: dict,
        backtest_options: dict,
        exchange_name: str,
        ohlcv: np.ndarray,
        interval: str,
        symbol_params: dict,
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
        self.exchange_name = exchange_name
        self.ohlcv = ohlcv
        self.symbol_params = symbol_params
        self.interval = interval
        self.start_timestamp = int(0.001 * ohlcv[0, 0])
        self.end_timestamp = int(0.001 * ohlcv[-1, 0])
        self.backtester = Backtester()
        self.reporter = Reporter(
            optimization_id=optimization_id,
            optimization_group_id=optimization_group_id,
            tg_id=tg_id,
            strategy_name=strategy.name,
            exchange_name=exchange_name,
            symbol=symbol_params.get("symbol"),
            interval=interval,
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            reports_dir=results_dir,
        )
        self.html_builder = HTMLBuilder()
        self.html_builder.init_bootstrap_folder(os.path.join(results_dir, "html/"))
        self.results_dir = results_dir

        # self.backtest_options["leverage"] = 1  # Make optimization without leverage

    async def execute(self):
        self.reporter.report_start_optimization()

        for i in range(self.number_of_starts):
            print(
                f"{self.strategy.name} {self.symbol_params.get('symbol')} {self.interval} loop #{i+1}"
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
                self.process_results()

        await self.reporter.finish_optimisation()

    def create_initial_population(self):
        self.samples = [
            [r.choice(j) for j in self.strategy.opt_parameters.values()]
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
        if r.randint(0, 1) == 0:
            score = self.__get_best_score_of_population(self.population)
            parent_1 = self.population[score][0]
            population_copy = self.population.copy()
            del population_copy[score]
            parent_2 = r.choice(list(population_copy.values()))[0]
            self.parents = [parent_1, parent_2]
        else:
            parents = r.sample(list(self.population.values()), 2)
            self.parents = [parents[0][0], parents[1][0]]

    def cross(self):
        r_number = r.randint(0, 1)

        if r_number == 0:
            delimiter = r.randint(1, self.sample_length - 1)
            self.child = self.parents[0][:delimiter] + self.parents[1][delimiter:]
        else:
            delimiter_1 = r.randint(1, self.sample_length // 2 - 1)
            delimiter_2 = r.randint(self.sample_length // 2 + 1, self.sample_length - 1)
            self.child = (
                self.parents[0][:delimiter_1]
                + self.parents[1][delimiter_1:delimiter_2]
                + self.parents[0][delimiter_2:]
            )

    def mutate(self):
        if r.randint(0, 100) < self.mutation_probability:
            gene_number = r.randint(0, self.sample_length - 1)
            gene_value = r.choice(
                list(self.strategy.opt_parameters.values())[gene_number]
            )
            self.child[gene_number] = gene_value

    def expand(self):
        metrics = self.fit(self.child)
        self.population[metrics[0]] = (self.child, metrics[1], metrics[2])
        self.reporter.report_expand_results(self.population[metrics[0]])
        return self.population[metrics[0]]

    def assimilate(self):
        if r.randint(0, 1000) / 10 < self.assimilation_probability:
            samples = [
                [r.choice(j) for j in self.strategy.opt_parameters.values()]
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

    def process_results(self):
        best_sample = self.population[self.best_score]

        best_sample_backtest_log = self.backtester.execute_backtest(
            strategy=self.strategy,
            strategy_params=best_sample[0],
            ohlcv=self.ohlcv,
            symbol_params=self.symbol_params,
            backtest_options=self.backtest_options,
        )

        html = self.html_builder.generate_html(
            strategy_name=self.strategy.name,
            exchange_name=self.exchange_name,
            symbol = self.symbol_params.get('symbol'),
            interval=self.interval,
            log = best_sample_backtest_log, 
            initial_capital=self.backtest_options.get("initial_capital")
        )
        timestamp_now = int(1000 * dt.datetime.now().timestamp())
        html_file_path = os.path.join(f"{self.results_dir}/html/{self.strategy.name}/{self.exchange_name}", f"{self.symbol_params.get('symbol')}_{self.interval}_{timestamp_now}.html")
        html_file_dir = os.path.dirname(html_file_path)
        bootstrap_dir = os.path.join(html_file_dir, "bootstrap")
        if not os.path.exists(html_file_dir):
            os.makedirs(html_file_dir)
        if not os.path.exists(bootstrap_dir):
            os.makedirs(bootstrap_dir)
        with open(html_file_path, "w") as f:
            f.write(html)
        best_params = best_sample[0]
        net_profit = best_sample[1]
        max_drawdown = best_sample[2]

        for count, value in enumerate(best_params):
            if isinstance(value, np.ndarray):
                best_params[count] = list(value)

        del self.population[self.best_score]
        self.best_score = self.__get_best_score_of_population(self.population)

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
"""
        report_text += "".join(
            [
                value + " = " + str(best_params[count]) + "\n"
                for count, value in enumerate(self.strategy.opt_parameters.keys())
            ]
        )
        report_text += "".join("=" * 35)

        self.reporter.report_optimization_results(report_text)


    def __get_best_score_of_population(self, population: np.ndarray) -> float:
        best_score = max(population)
        return best_score
