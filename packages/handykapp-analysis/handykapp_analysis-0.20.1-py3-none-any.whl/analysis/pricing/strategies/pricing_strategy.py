from horsetalk import Horse
from pybet import Market

from analysis.forecasting import FormForecast


class PricingStrategy:
    def __call__(self, form_forecasts: dict[Horse, FormForecast]) -> Market:
        raise NotImplementedError
