from pendulum import DateTime

from .likeness import LikenessMixin, discount


class RaceDateTime(LikenessMixin):
    _likeness_functions = {
        # date likeness reaches 0 after 1000 days
        "datetime": lambda a, b: discount((abs(a - b).days / 1000) ** 0.5)
    }

    def __init__(self, datetime: DateTime):
        self.datetime = datetime

    def __eq__(self, other: object):
        if not isinstance(other, RaceDateTime):
            return NotImplemented

        return self.datetime == other.datetime

    def __lt__(self, other: "RaceDateTime"):
        return self.datetime < other.datetime

    def __gt__(self, other: "RaceDateTime"):
        return self.datetime > other.datetime

    def format(self, fmt: str) -> str:
        return self.datetime.format(fmt)
