from ..abc import NamedMetric
import random


class RandomMetric(NamedMetric):
    def __init__(self):
        super().__init__("random", lambda x, y: random.random())
