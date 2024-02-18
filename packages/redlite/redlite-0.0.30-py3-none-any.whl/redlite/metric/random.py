from ..core import NamedMetric
import random

__docformat__ = "google"


class RandomMetric(NamedMetric):
    def __init__(self):
        super().__init__("random", lambda x, y: random.random())
