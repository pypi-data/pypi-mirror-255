from horsetalk import Horse
from pybet import Market, Odds

from analysis.forecasting import FormForecast
from analysis.pricing.strategies import PricingStrategy


class Alpha(PricingStrategy):
    def __init__(self, *args, **kwargs):
        self.alpha = kwargs.get("alpha", 0.16)
        self.percentile = kwargs.get("percentile", 0.5)
        super().__init__()

    def __call__(self, form_forecasts: dict[Horse, FormForecast]) -> Market:
        weightings = [
            self.alpha ** v.probability_distribution.ppf(self.percentile)
            for v in form_forecasts.values()
        ]
        total = sum(weightings)

        return {
            horse: Odds.probability(weighting / total)
            for horse, weighting in zip(form_forecasts.keys(), weightings)
        }
