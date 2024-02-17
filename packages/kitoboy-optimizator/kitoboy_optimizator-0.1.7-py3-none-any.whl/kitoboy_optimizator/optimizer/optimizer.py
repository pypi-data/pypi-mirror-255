import random as r
import numpy as np
import datetime as dt

from kitoboy_optimizator.report_builder import StrategyTestResultCalculator, Reporter


class Optimizer:

    def __init__(self, optimization_id: str, optimization_group_id: str,  strategy, optimizer_options: dict, backtest_options: dict, exchange_name: str, ohlcv: np.ndarray, interval: str, symbol_params: dict, results_dir: str, tg_id: int):
        self.strategy = strategy
        self.iterations = optimizer_options.get('iterations')
        self.number_of_starts = optimizer_options.get('number_of_starts')
        self.optimization_type = optimizer_options.get('optimization_type')
        self.min_max_drawdown = optimizer_options.get('min_max_drawdown')
        self.population_size = optimizer_options.get('population_size')
        self.max_population_size = optimizer_options.get('max_population_size')
        self.mutation_probability = optimizer_options.get('mutation_probability')
        self.assimilation_probability = optimizer_options.get('assimilation_probability')
        self.final_results = optimizer_options.get('final_results')
        self.backtest_options = backtest_options
        self.ohlcv = ohlcv
        self.symbol_params = symbol_params
        self.interval = interval
        self.start_timestamp = int(0.001 * ohlcv[0, 0])
        self.end_timestamp = int(0.001 * ohlcv[-1, 0])
        self.reporter = Reporter(
            optimization_id=optimization_id,
            optimization_group_id=optimization_group_id,
            tg_id=tg_id,
            strategy_name=strategy.name,
            exchange_name=exchange_name,
            symbol=symbol_params.get('symbol'),
            interval=interval,
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            reports_dir=results_dir
        )
        self.results_dir = results_dir
        self.backtest_options["leverage"] = 1 # Make optimization without leverage
       
        
    def create_initial_population(self):
        self.samples = [
            [               
                r.choice(j) 
                    for j in self.strategy.opt_parameters.values()
            ]
            for i in range(self.population_size)
        ]
        self.population = {
            k[0]: (v, k[1], k[2]) for k, v in zip(
                map(self.fit, self.samples), self.samples
            )
        }
        self.sample_length = len(self.strategy.opt_parameters)
        self.actual_population_size = len(self.population)
        self.best_score = float('-inf')
        self.reporter.report_initial_population(self.population)
        return self.population

    def fit(self, sample):
        strategy = self.strategy(
            ohlcv=self.ohlcv,
            symbol_params=self.symbol_params,
            opt_parameters=sample
        )
        initial_capital = self.backtest_options.get('initial_capital')
        log = strategy.start(
            margin_type=self.backtest_options.get('margin_type'),             # 0 - 'ISOLATED', 1 - 'CROSSED'
            direction=self.backtest_options.get('direction'),              # 0 - 'all', 1 - 'longs', 2 - 'shorts'
            initial_capital=initial_capital,
            min_capital=self.backtest_options.get('min_capital'),
            commission=self.backtest_options.get('commission'),
            order_size_type=self.backtest_options.get('order_size_type'),         # 0 - 'PERCENT', 1 - 'CURRENCY'
            order_size=self.backtest_options.get('order_size'),
            leverage=self.backtest_options.get('leverage')
        )

        metrics = StrategyTestResultCalculator.get_optimized_metrics(log, initial_capital)

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
            score = max(self.population)
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
            self.child = (self.parents[0][:delimiter] 
                        + self.parents[1][delimiter:])
        else:
            delimiter_1 = r.randint(1, self.sample_length // 2 - 1)
            delimiter_2 = r.randint(
                self.sample_length // 2 + 1, self.sample_length - 1)
            self.child = (self.parents[0][:delimiter_1]
                        + self.parents[1][delimiter_1:delimiter_2]
                        + self.parents[0][delimiter_2:])

    def mutate(self):
        if r.randint(0, 100) < self.mutation_probability:
            gene_number = r.randint(0, self.sample_length - 1)
            gene_value = r.choice(
                list(
                    self.strategy.opt_parameters.values()
                )[gene_number]
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
                [
                    r.choice(j) 
                        for j in self.strategy.opt_parameters.values()
                ]
                for i in range(len(self.population) // 2)
            ]
            population = {
                k[0]: (v, k[1], k[2]) for k, v in zip(
                    map(self.fit, samples), samples
                )
            }
            self.population.update(population)
            self.reporter.report_assimilation_results(population)
            return population
        

    def elect(self):
        if self.best_score < max(self.population):
            self.best_score = max(self.population)
            self.reporter.report_new_best_scores(self.iteration, self.best_score)
        return self.best_score

    def kill(self):
        while len(self.population) > self.max_population_size:
            del self.population[min(self.population)]

    def report_results(self):
        best_sample = self.population[self.best_score]
        best_params = best_sample[0]
        net_profit = best_sample[1]
        max_drawdown = best_sample[2]

        for count, value in enumerate(best_params):
            if isinstance(value, np.ndarray):
                best_params[count] = list(value)

        del self.population[self.best_score]
        self.best_score = max(self.population)
        
        start_time = dt.datetime.utcfromtimestamp(self.start_timestamp).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        end_time = dt.datetime.utcfromtimestamp(self.end_timestamp).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        report_text = (
            'Period: ' + start_time + ' — ' +
            end_time + '\n' + 'Net profit, %: ' +
            str(net_profit) + '\n' + 'Max drawdown, %: ' +
            str(max_drawdown) + '\n' + ('=' * 50) + '\n'
        )
        report_text += ''.join(
            [
                value + ' = ' + str(best_params[count]) + '\n'
                    for count, value in enumerate(
                        self.strategy.opt_parameters.keys()
                    )
            ]
        )
        report_text += ''.join('=' * 35)
        report_text += '\n\n'

        self.reporter.report_optimization_results(report_text)

    async def execute(self):
        self.reporter.report_start_optimization()

        for i in range(self.number_of_starts):
            print(f"{self.strategy.name} {self.symbol_params.get('symbol')} {self.interval} loop #{i+1}")
            self.create_initial_population()

            for j in range(self.iterations):
                self.iteration = j + 1
                self.select()
                self.cross()
                self.mutate()
                self.expand()
                self.assimilate()
                self.elect()
                self.kill()

            for i in range(self.final_results):
                self.report_results()

        await self.reporter.finish_optimisation()