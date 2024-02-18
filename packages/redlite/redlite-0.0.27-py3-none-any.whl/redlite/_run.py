import contextlib
import os
import time
from tqdm import tqdm
import duoname
from datetime import datetime
from ._core import (
    NamedModel,
    NamedDataset,
    NamedMetric,
    Storage,
    Run,
)
from ._jsonl_storage import JsonlStorage
from ._util import DatasetRunningDigest, redlite_data_dir, format_score_summary, ScoreAccumulator
from ._lock import incr_run_count
from typing import Iterator
from ._core import log


__all__ = ["run"]


def run(
    *,
    model: NamedModel,
    dataset: NamedDataset,
    metric: NamedMetric,
    name: str | None = None,
    max_samples=0,
) -> Run:
    """Runs experiment, using the given `model`, `dataset`, and `metric`.

    - **model** (`NamedModel`): Model.
    - **dataset** (`NamedDataset`): Dataset.
    - **metric** (`NamedMetric`): Metric.
    - **name** (`str`, optional): The name of the run. It will automatically get a
            numeric suffix to ensure global uniqueness.
            If not provided, a unique name will be auto-generated.
    - **max_samples** (`int`, optional): Allows one to limit the number of samples
            in the run. Value of zero (the default) means "run the whole dataset".

    Returns the name of the actual (generated) run name.

    Sample usage:
    ```python
    model = MyModel(...)
    dataset = MyDataset(...)
    metric = MyMetric(...)

    run(model=model, dataset=dataset, metric=metric)
    ```
    """
    started = time.time()

    data_with_digest = DatasetRunningDigest(dataset, max_samples=max_samples)
    score_accumulator = ScoreAccumulator()

    if name is None:
        name = _generate_name()
    run_count = incr_run_count()
    runname = f"{name}-{run_count}"

    print(f"RedLite run {runname}:")
    print(f"\tmodel  : {model.name}")
    print(f"\tdataset: {dataset.name}")
    print(f"\tmetric : {metric.name}")

    with _storage(runname) as storage:  # type: Storage
        for item in tqdm(data_with_digest):
            actual = model(item["messages"])
            score = metric(item["expected"], actual)
            storage.save(item, actual, score)
            score_accumulator(score)

        completed = time.time()

        run: Run = dict(
            run=storage.name,
            dataset=dataset.name,
            split=dataset.split,
            dataset_labels=dataset.labels,
            data_digest=data_with_digest.hexdigest,
            metric=metric.name,
            model=model.name,
            max_samples=max_samples,
            started=datetime.utcfromtimestamp(started).isoformat() + "Z",
            completed=datetime.utcfromtimestamp(completed).isoformat() + "Z",
            duration=completed - started,
            score_summary=score_accumulator.summary,
        )

        storage.save_meta(**run)

        print()
        print(f"\tData digest: {run['data_digest']}")
        print(f"\tScore summary: {format_score_summary(run['score_summary'])}")
        print("Smile! All done!")
        return run


@contextlib.contextmanager
def _storage(runname: str) -> Iterator[Storage]:
    base = os.path.join(redlite_data_dir(), runname)
    if os.path.isdir(base):
        raise RuntimeError(f"Unexpectedly, directory {base} exists!")
    os.makedirs(base, exist_ok=True)

    log.info(f"Started run {runname}")
    with JsonlStorage.open(runname, base) as s:
        yield s


def _generate_name():
    return duoname.duoname()
