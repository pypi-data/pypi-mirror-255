from .. import NamedMetric
from .util import normalize_string


class PrefixMetric(NamedMetric):
    """
    Metric that checks that the actual response starts with the expected string.

    For example, the expected response could be "Correct", but model answers
    "Correct, because blah blah blah...". To give model full marks for longer and
    verbose answer, use this metric.

    - **ignore_case** (`bool`) - when set to `True` will ignore text case. Deafult is `False`.

    - **ignore_punct** (`bool`) - when set to `True` punctuation symbols will be ignored.
            Default is `False`.

    - **normalize_white_space** (`bool`) - when set to `True`, normalizes white space by
            replacing tabs and newlines with spaces and replacing multiple spaces to one. Also
            strips leading and trailing whitespace.
            Default is `False`.
    """

    def __init__(self, ignore_case=False, ignore_punct=False, normalize_whitespace=False):
        name = "prefix"
        if ignore_case:
            name = name + "-ignore-case"
        if ignore_punct:
            name = name + "-ignore-punct"
        if normalize_whitespace:
            name = name + "-strip"

        self.ignore_case = ignore_case
        self.ignore_punct = ignore_punct
        self.normalize_whitespace = normalize_whitespace

        super().__init__(name, self.__engine)

    def __engine(self, expected: str, actual: str) -> float:
        expected = normalize_string(
            expected,
            to_lower=self.ignore_case,
            strip_punct=self.ignore_punct,
            normalize_whitespace=self.normalize_whitespace,
        )
        actual = normalize_string(
            actual,
            to_lower=self.ignore_case,
            strip_punct=self.ignore_punct,
            normalize_whitespace=self.normalize_whitespace,
        )

        if actual.startswith(expected):
            return 1.0
        return 0.0


class ExactMetric(NamedMetric):
    """
    Metric that checks that the actual response equals the expected string.

    - **ignore_case** (`bool`) - when set to `True` will ignore text case. Deafult is `False`.

    - **ignore_punct** (`bool`) - when set to `True` punctuation symbols will be ignored.
            Default is `False`.

    - **normalize_white_space** (`bool`) - when set to `True`, normalizes white space by
            replacing tabs and newlines with spaces and replacing multiple spaces to one. Also
            strips leading and trailing whitespace.
            Default is `False`.
    """

    def __init__(self, ignore_case=False, ignore_punct=False, normalize_whitespace=False):
        name = "exact"
        if ignore_case:
            name = name + "-ignore-case"
        if ignore_punct:
            name = name + "-ignore-punct"
        if normalize_whitespace:
            name = name + "-strip"

        self.ignore_case = ignore_case
        self.ignore_punct = ignore_punct
        self.normalize_whitespace = normalize_whitespace

        super().__init__(name, self.__engine)

    def __engine(self, expected: str, actual: str) -> float:
        expected = normalize_string(
            expected,
            to_lower=self.ignore_case,
            strip_punct=self.ignore_punct,
            normalize_whitespace=self.normalize_whitespace,
        )
        actual = normalize_string(
            actual,
            to_lower=self.ignore_case,
            strip_punct=self.ignore_punct,
            normalize_whitespace=self.normalize_whitespace,
        )

        if expected == actual:
            return 1.0
        return 0.0
