from scipy.stats import triang

from analysis.forecasting.strategies import FormForecastStrategy


class MinModeMaxTriangular(FormForecastStrategy):
    def _probability_distribution(self):
        r = self._past_ratings
        min_r = min(r)
        max_r = max(r)
        mode_r = sum(r) / len(r)

        loc = min_r
        scale = max_r - min_r
        c = (mode_r - min_r) / scale

        return triang(c, loc, scale)
