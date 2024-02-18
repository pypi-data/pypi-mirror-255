import dataclasses
import abc
from collections.abc import Callable, Iterable
from typing import Any
from enum import Enum


class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclasses.dataclass(frozen=True)
class Message:
    role: Role
    """Role of the message author."""

    content: str
    """Message text."""

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role=Role.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role=Role.ASSISTANT, content=content)

    def to_json_obj(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
        }

    @classmethod
    def from_json_obj(cls, obj: dict[str, Any]) -> "Message":
        return cls(role=obj["role"], content=obj["content"])


@dataclasses.dataclass
class DatasetItem:
    id: str
    messages: list[Message]
    expected: str

    def to_json_obj(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "messages": [m.to_json_obj() for m in self.messages],
            "expected": self.expected,
        }

    @classmethod
    def from_json_obj(cls, obj: dict[str, Any]) -> "DatasetItem":
        messages = [Message.from_json_obj(x) for x in obj["messages"]]
        return cls(id=obj["id"], messages=messages, expected=obj["expected"])


class NamedDataset(Iterable[DatasetItem]):
    name: str


class NamedMetric:
    name: str

    def __init__(self, name: str, engine: Callable[[str, str], float]):
        self.name = name
        self.engine = engine

    def __call__(self, expected: str, actual: str) -> float:
        return self.engine(expected, actual)


class NamedModel:
    name: str

    def __init__(self, name: str, engine: Callable[[list[Message]], str]):
        self.name = name
        self.engine = engine

    def __call__(self, messages: list[Message]) -> str:
        return self.engine(messages)


class Storage(abc.ABC):
    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def save(self, item: DatasetItem, response: str, score: float):
        pass

    @abc.abstractmethod
    def save_meta(self, **kw):
        pass


@dataclasses.dataclass
class Experiment:
    """Represents experiment run"""

    name: str


class MissingDependencyError(RuntimeError):
    """Raised when a missing optional dependency is detected"""


KeyedValues = dict[str, Any]


@dataclasses.dataclass(frozen=True)
class ScoreSummary:
    count: int
    mean: float
    min: float
    max: float

    def to_json_obj(self) -> KeyedValues:
        return {
            "count": self.count,
            "mean": self.mean,
            "min": self.min,
            "max": self.max,
        }

    @classmethod
    def from_json_obj(cls, obj: KeyedValues) -> "ScoreSummary":
        return cls(**obj)


class ScoreAccumulator:
    def __init__(self):
        self._min = 100000  # FIXME?
        self._max = 0.0
        self._acc = 0.0
        self._count = 0

    def __call__(self, score: float) -> None:
        self._acc += score
        self._min = min(self._min, score)
        self._max = max(self._max, score)
        self._count += 1

    @property
    def summary(self):
        mean = 0.0 if self._count == 0 else self._acc / self._count
        return ScoreSummary(
            count=self._count,
            mean=mean,
            min=self._min,
            max=self._max,
        )
