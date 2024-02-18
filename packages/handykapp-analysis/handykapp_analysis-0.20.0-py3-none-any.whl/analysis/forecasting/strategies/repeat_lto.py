from scipy.stats import norm, rv_continuous

from analysis.forecasting.strategies import FormForecastStrategy


class RepeatLto(FormForecastStrategy):
    def _probability_distribution(self) -> rv_continuous:
        return norm(loc=float(self._past_ratings[-1]), scale=0.33)
