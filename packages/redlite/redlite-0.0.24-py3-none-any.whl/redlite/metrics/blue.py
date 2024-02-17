from ..abc import NamedMetric


class BlueMetric(NamedMetric):
    def __init__(self):
        super().__init__("blue", _compute_blue_score)


def _compute_blue_score(expected: str, actual: str) -> float:  # FIXME
    if expected == actual:
        return 1.0
    return 0.0
