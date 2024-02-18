from .. import NamedMetric
import re


_PUNCT = ".,:;()[]{}!?<>$%"
_RE_PUNCT = re.compile("[" + re.escape(_PUNCT) + "]")


def match(expected: str, actual: str, ignore_case=True, ignore_punct=False, strip=False) -> float:
    """
    Computes score by comparing expected string to the prefix of the actual string.
    """
    if ignore_case:
        expected = expected.lower()
        actual = actual.lower()

    if ignore_punct:
        expected = re.sub(_RE_PUNCT, "", expected)
        actual = re.sub(_RE_PUNCT, "", actual)

    if strip:
        expected = expected.strip()
        actual = actual.strip()

    if actual.startswith(expected):
        return 1.0

    return 0.0


class PrefixMetric(NamedMetric):
    """Metric that checks that the actual resonse starts with the expected string.

    For example, the expected response could be "Correct", but model answers
    "Correct, because blah blah blah...". To give model full marks for longer and
    verbose answer, use this metric.

    - **ignore_case** (`bool`) - when set to `True` will ignore text case. Deafult is `False`.
    - **ignore_punct** (`bool`) - when set to `True` punctuation symbols and various parenthesis
            will be ignored. Default is `False`.

    - **strip** (`bool`) - when set to `True`, strips leading and trailing white space.
            Default is `False`.
    """

    def __init__(self, ignore_case=False, ignore_punct=False, strip=False):
        name = "prefix"
        if ignore_case:
            name = name + "-ignore-case"
        if ignore_punct:
            name = name + "-ignore-punct"
        if strip:
            name = name + "-strip"

        self.ignore_case = ignore_case
        self.ignore_punct = ignore_punct

        super().__init__(name, self.__match)

    def __match(self, expected: str, actual: str) -> float:
        return match(
            expected,
            actual,
            ignore_case=self.ignore_case,
            ignore_punct=self.ignore_punct,
        )
