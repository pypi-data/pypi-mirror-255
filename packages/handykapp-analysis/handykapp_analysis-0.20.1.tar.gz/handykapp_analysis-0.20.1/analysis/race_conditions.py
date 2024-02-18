from horsetalk import RaceConditions as HorsetalkRaceConditions

from .likeness import LikenessMixin, ignore, likeness
from .race_datetime import RaceDateTime


class RaceConditions(LikenessMixin, HorsetalkRaceConditions):
    _likeness_functions = {
        "datetime": likeness,
        "racecourse": likeness,
        "distance": likeness,
        "going": likeness,
        "race_designation": ignore,
        # lambda a, b: 1 if a == b else 0.83,
        "race_level": ignore,
        # lambda a, b: int(a == b)
        # or discount(abs(a.class_.value - b.class_.value) * 0.05),
    }

    def __init__(self, *args, **kwargs):
        kwargs["datetime"] = RaceDateTime(kwargs["datetime"])
        super().__init__(*args, **kwargs)
