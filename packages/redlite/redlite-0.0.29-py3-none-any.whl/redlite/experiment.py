import contextlib
import logging
import os
import time
import randomname
from datetime import datetime
from .abc import NamedModel, NamedDataset, NamedMetric, Storage, Experiment, ScoreAccumulator
from ._jsonl_storage import JsonlStorage
from .util import DatasetRunningDigest, format_duration
from ._lock import incr_run_count
from typing import Iterator

__all__ = ["run"]
__docformat__ = "google"

logger = logging.getLogger("redlite")


def run(
    *,
    model: NamedModel,
    dataset: NamedDataset,
    metric: NamedMetric,
    name: str | None = None,
    max_samples=0,
) -> Experiment:
    """Runs experiment, using the given `model`, `dataset`, and `metric`.

    Args:
        model (NamedModel): A model to run.
        dataset (NamedDataset): Dataset.
        metric (NamedMetric): Metric.
        name (str, optional): The name of the run. It will automatically get a
            numeric suffix to ensure global uniqueness.
            If not provided, a unique name will be auto-generated.

    Returns: tuple

    Usage:

    ```python
    TODO
    ```
    """
    started = time.time()

    data_with_digest = DatasetRunningDigest(dataset)
    score_accumulator = ScoreAccumulator()
    with _storage(name) as storage:  # type: Storage
        sample_count = 0
        for item in data_with_digest:
            actual = model(item.messages)
            sample_count += 1
            if max_samples > 0 and sample_count >= max_samples:
                break
            score = metric(item.expected, actual)
            storage.save(item, actual, score)
            score_accumulator(score)

        completed = time.time()

        storage.save_meta(
            name=storage.name,
            dataset=dataset.name,
            data_digest=data_with_digest.hexdigest,
            metric=metric.name,
            model=model.name,
            max_samples=max_samples,
            started=datetime.utcfromtimestamp(started).isoformat() + "Z",
            completed=datetime.utcfromtimestamp(completed).isoformat() + "Z",
            duration=format_duration(completed - started),
            score_summary=score_accumulator.summary.to_json_obj(),
        )

        return Experiment(name=storage.name)


@contextlib.contextmanager
def _storage(name: str | None) -> Iterator[Storage]:
    if name is None:
        name = _generate_name()
    run_count = incr_run_count()
    runname = f"{name}-{run_count}"
    base = os.path.expanduser(f"~/.cache/redlite/{runname}")
    if os.path.isdir(base):
        raise RuntimeError(f"Unexpectedly, directory {base} exists!")
    os.makedirs(base, exist_ok=True)

    logger.info(f"Started run {runname}")
    with JsonlStorage.open(runname, base) as s:
        yield s


def _generate_name():
    return randomname.get_name()
