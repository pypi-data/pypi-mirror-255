import functools
from ..core import NamedMetric
from .compute_bleu import compute_bleu

__docformat__ = "google"


class BleuMetric(NamedMetric):
    """Sentence-level BLEU score"""

    def __init__(self, max_order=4, smooth=False):
        engine = functools.partial(_bleu, max_order=max_order, smooth=smooth)
        super().__init__("bleu", engine)


def _bleu(expected: str, actual: str, max_order=4, smooth=False) -> float:
    """Computes BLEU score."""
    return compute_bleu([[expected.split()]], [actual.split()], max_order=max_order, smooth=smooth)[0]
