import os
import json
import contextlib
from collections.abc import Iterator
from .abc import Storage, DatasetItem, KeyedValues


class JsonlStorage(Storage):
    def __init__(self, name: str, folder: str, fd):
        super().__init__(name)
        self.folder = folder
        self.fd = fd

    def save_meta(self, **kaw: KeyedValues) -> KeyedValues:
        with open(f"{self.folder}/meta.json", "w", encoding="utf-8") as f:
            json.dump(kaw, f, ensure_ascii=False, indent=2)
        return kaw

    def save(self, item: DatasetItem, actual: str, score: float) -> None:
        self.fd.write(
            json.dumps(
                {
                    "item": item.to_json_obj(),
                    "actual": actual,
                    "score": score,
                },
                ensure_ascii=False,
            )
        )
        self.fd.write("\n")

    @classmethod
    @contextlib.contextmanager
    def open(cls, name: str, folder: str) -> Iterator[Storage]:
        os.makedirs(folder)
        with open(f"{folder}/data.jsonl", "w", encoding="utf-8") as f:
            yield cls(name, folder, f)
