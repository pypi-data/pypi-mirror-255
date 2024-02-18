from horsetalk import Horse
from pybet import Market

from analysis.forecasting import FormForecast
from analysis.pricing.strategies import PricingStrategy


class Pricer:
    def __init__(self, strategy: PricingStrategy):
        self.strategy = strategy

    def price(self, form_forecasts: dict[Horse, FormForecast]) -> Market:
        return self.strategy(form_forecasts)
