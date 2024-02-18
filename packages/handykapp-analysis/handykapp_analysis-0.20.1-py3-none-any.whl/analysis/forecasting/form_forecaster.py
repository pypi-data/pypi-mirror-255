from horsetalk import Horse

from analysis import RaceCareer, RaceConditions
from analysis.forecasting import FormForecast
from analysis.forecasting.strategies import FormForecastStrategy


class FormForecaster:
    def __init__(self, strategy: FormForecastStrategy, **kwargs):
        self.strategy = strategy.using(**kwargs) if kwargs else strategy

    def forecast(
        self,
        horse: Horse,
        career: RaceCareer,
        conditions: RaceConditions,
    ) -> FormForecast:
        return self.strategy(horse, career, conditions)
