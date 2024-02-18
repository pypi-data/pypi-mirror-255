import json
from typing import Literal
from collections.abc import Iterator
from .._core import NamedDataset, DatasetItem


class JSONDataset(NamedDataset):
    """
    Dataset from a local JSONL file.

    Each line of the dataset file must be a `DatasetItem` serialized to JSON representation.
    File must use UTF-8 encoding. There should be no BOM-markers (some Microsoft tools produce those).

    - **path** (`str`): Location of JSONL file.
    - **name** (`str`): Dataset name.
    - **split** (`str`): Dataset split.
    - **labels** (`dict[str, str]`): Labels.
    """

    def __init__(self, *, path: str, name: str, split: Literal["test", "train"], labels: dict[str, str] | None = None):
        self.name = name
        self.split = split
        self.labels = labels if labels is not None else {}
        self._path = path

        self._data: list[DatasetItem] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                self._data.append(json.loads(line))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[DatasetItem]:
        yield from self._data
