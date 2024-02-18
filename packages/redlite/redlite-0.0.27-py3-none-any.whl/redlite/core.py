import dataclasses
import abc
from collections.abc import Callable, Iterable, Sized
from typing import TypedDict, Literal
import logging

__docformat__ = "google"


log = logging.getLogger("redlite")
"""Logger for the redlite package."""

Role = Literal["system", "user", "assistant"]
"""Type for the message role. Can be "system", "user", or "assistant"."""

Message = TypedDict("Message", {"role": Role, "content": str})
"""Type for Message: message is a dictionary contatining "role" and "content" keys."""

Messages = list[Message]
"""Type for Messages: its just a list of Message objects. Represents conversation."""

DatasetItem = TypedDict("DatasetItem", {"id": str, "messages": Messages, "expected": str})
"""Type for dataset item. Every dataset item must have unique id, messages, and the expected completion"""

Split = Literal["test", "train"]
"""Type for the dataset split"""


def system_message(content: str) -> Message:
    """Helper to create a Message with role="system"

    Args:
        content (str): Message content.

    Returns:
        Message: System message.
    """
    return {"role": "system", "content": content}


def user_message(content: str) -> Message:
    """Helper to create a Message with role="user"

    Args:
        content (str): Message content.

    Returns:
        Message: User message.
    """
    return {"role": "user", "content": content}


def assistant_message(content: str) -> Message:
    """Helper to create a Message with role="assistant"

    Args:
        content (str): Message content.

    Returns:
        Message: Assistant message.
    """
    return {"role": "assistant", "content": content}


class NamedDataset(Sized, Iterable[DatasetItem]):
    """Dataset abstraction.

    Each RedLite dataset must have:

    1. name (str): Dataset name
    2. split (str): Split ("test" or "train")
    3. labels (dict): Dictionary of dataset labels
    """

    name: str
    split: Split
    labels: dict[str, str]


class NamedMetric:
    """Metric abstraction.

    Each RedLite metric must have a name (str), and be a callable.
    """

    name: str

    def __init__(self, name: str, engine: Callable[[str, str], float]):
        """Creates RedLite metric from name and callable.

        Args:
            name (str): Metric name.
            engine (Callable[[str, str], float]): Function that computes metric score
                from expected response and actual response strings.

        Returns:
            float: Computed metric score.
        """
        self.name = name
        self._engine = engine

    def __call__(self, expected: str, actual: str) -> float:
        return self._engine(expected, actual)


class NamedModel:
    """Model abstraction.

    Each RedLite model must have a name, and be callable that computes string response from input conversation.
    """

    name: str

    def __init__(self, name: str, engine: Callable[[Messages], str]):
        """Creates a new model from name and callable.

        Args:
            name (str): Name of the model.
            engine (Callable[[Messages], str]): A function that computes model prediction from messages.
        """
        self.name = name
        self._engine = engine

    def __call__(self, conversation: Messages) -> str:
        """Computes model prediction.

        Args:
            conversation (Messages): Input conversation.

        Returns:
            str: Assistant response to the conversation.
        """
        return self._engine(conversation)


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


ScoreSummary = TypedDict("ScoreSummary", {"count": int, "mean": float, "min": float, "max": float})
