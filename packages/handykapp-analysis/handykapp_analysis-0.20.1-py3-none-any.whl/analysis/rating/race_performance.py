from horsetalk import RacePerformance as HorsetalkRacePerformance

from .form_rating import FormRating
from .performance_context import PerformanceContext
from .time_rating import TimeRating


class RacePerformance(HorsetalkRacePerformance):
    def __init__(
        self,
        *args,
        form_rating: FormRating | None = None,
        time_rating: TimeRating | None = None,
        context: PerformanceContext | None = None,
        **kwargs,
    ):
        self.form_rating = form_rating
        self.time_rating = time_rating
        self.context = context
        super().__init__(*args, **kwargs)
