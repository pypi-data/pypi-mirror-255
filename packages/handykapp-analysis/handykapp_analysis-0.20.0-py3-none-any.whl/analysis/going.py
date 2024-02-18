from horsetalk import Going as HorsetalkGoing

from .likeness import LikenessMixin, discount

LIKENESS_DIFFERENCE_PER_POINT = 0.125


class Going(LikenessMixin, HorsetalkGoing):
    """
    A class to represent a going, wrapping the horsetalk class of the same name.
    """

    _likeness_functions = {
        "value": lambda a, b: discount(abs(a - b) * LIKENESS_DIFFERENCE_PER_POINT)
    }
