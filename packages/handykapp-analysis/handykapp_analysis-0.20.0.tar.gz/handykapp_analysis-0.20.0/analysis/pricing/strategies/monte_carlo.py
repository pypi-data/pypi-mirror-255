from collections import Counter
from decimal import Decimal

from horsetalk import Horse
from pybet import Market, Odds

from analysis.forecasting import FormForecast
from analysis.pricing.strategies import PricingStrategy


class MonteCarlo(PricingStrategy):
    def __init__(self, *args, **kwargs):
        self.trials = kwargs.get("trials", 10000)
        super().__init__()

    def __call__(self, form_forecasts: dict[Horse, FormForecast]) -> Market:
        counts = Counter(
            max(
                form_forecasts.keys(),
                key=lambda x: form_forecasts[x].probability_distribution.rvs(),
            )
            for _ in range(self.trials)
        )

        return Market(
            {
                horse: Odds.probability(Decimal(counts[horse] / self.trials))
                for horse in form_forecasts
            }
        )
