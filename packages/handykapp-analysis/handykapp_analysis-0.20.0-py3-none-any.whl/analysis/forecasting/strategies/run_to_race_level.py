from scipy.stats import norm

from analysis.forecasting.strategies import FormForecastStrategy

_flat_race_level_pars = {
    "Group 1": 140,
    "Group 2": 130,
    "Group 3": 120,
    "Listed": 110,
    "Class 2": 100,
    "Class 3": 90,
    "Class 4": 80,
    "Class 5": 70,
    "Class 6": 60,
    "Class 7": 50,
}


class RunToRaceLevel(FormForecastStrategy):
    def _probability_distribution(self):
        race_level = self.conditions.race_level

        max_level = _flat_race_level_pars[
            str(race_level.grade) or str(race_level.class_)
        ]
        min_level = max_level - 70
        ave_level = max_level - 35

        return norm(loc=ave_level, scale=(max_level - min_level) / 6)
