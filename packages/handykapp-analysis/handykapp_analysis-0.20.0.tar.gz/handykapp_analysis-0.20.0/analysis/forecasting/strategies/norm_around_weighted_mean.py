from scipy.stats import norm

from analysis.forecasting.strategies import FormForecastStrategy


class NormAroundWeightedMean(FormForecastStrategy):
    def _probability_distribution(self):
        w = self._weightings
        r = self._past_ratings

        wr = [x[0] * float(x[1]) for x in zip(w, r)]
        mean = float(sum(wr) / sum(w))

        return norm(loc=mean)
