import random
from decimal import Decimal
from itertools import starmap
from typing import Callable

from pybet import Odds  # type: ignore


class MonteCarloSimulator:
    def __init__(self, selection_function: Callable, runner_data: list[list]):
        self.selection_function = selection_function
        self.runner_data = runner_data
        n = len(runner_data)
        self.result_grid = [{(k + 1): 0 for k in range(n)} for _ in range(n)]
        self._n = n
        self._validate_runner_data()

    def run(self, times: int = 1000):
        for _ in range(times):
            result = list(starmap(self.selection_function, self.runner_data))
            randomiser = [random.random() for _ in self.runner_data]
            # add a small random factor to separate equal values
            result = [r + randomiser[i] for i, r in enumerate(result)]
            ordering = [sorted(result, reverse=True).index(r) for r in result]
            for i, o in enumerate(ordering):
                self.result_grid[i][o + 1] += 1
        return [
            {k: Odds.probability(Decimal(str(v / times))) for k, v in row.items()}
            for row in self.result_grid
        ]

    def _validate_runner_data(self):
        for datum in self.runner_data:
            self.selection_function(*datum)
