from .._util import redlite_data_dir, read_runs, read_data
from .._core import MissingDependencyError
import collections
import os


try:
    from zeno_client import ZenoClient, ZenoMetric
    import pandas as pd
except ImportError as err:
    raise MissingDependencyError("Please install zeno_client library") from err


Task = collections.namedtuple("Task", ["dataset", "data_digest", "metric"])


def read_tasks(root: str):
    """Reads all runs and builds task-level aggregation."""
    by_task = collections.defaultdict(list)

    def run_task(run):
        return Task(run["dataset"], run["data_digest"], run["metric"])

    for run in read_runs(root):
        by_task[run_task(run)].append(run)

    for task, runs in by_task.items():
        # group by model here
        by_model = collections.defaultdict(list)
        for run in runs:
            by_model[run["model"]].append(run)

        # take only the last model's run into account
        latest_runs = []
        for model_runs in by_model.values():
            model_runs = sorted(model_runs, key=lambda x: x["completed"])
            latest_runs.append(model_runs[-1])

        yield task, latest_runs


def upload(api_key: str | None = None) -> None:
    """Uploads all runs to Zeno."""
    base_dir = redlite_data_dir()
    tasks = dict(read_tasks(base_dir))
    if len(tasks) == 0:
        print("No tasks found. Please run some benchmarks, then upload")

    if api_key is None:
        api_key = os.environ.get("ZENO_API_KEY")
    if api_key is None:
        raise RuntimeError("ZENO_API_KEY not found")

    # Initialize a client with our API key.
    client = ZenoClient(api_key=api_key)

    for task, runs in tasks.items():
        print(f"Uploading task {task}")

        run_name = runs[0]["name"]  # all runs contain the same data,
        # does not matter which one we send out
        df = pd.DataFrame(read_data(base_dir, run_name)).drop("score", axis=1).drop("actual", axis=1)

        project_name = f"RedLight: {task.dataset}-{task.data_digest[:6]}-{task.metric}".replace("/", "__")
        project = client.create_project(
            name=project_name,
            view="chatbot",
            metrics=[
                ZenoMetric(name="score", type="mean", columns=["score"]),
            ],
        )

        project.upload_dataset(df, id_column="id", data_column="messages", label_column="expected")

        for run in runs:
            print(f"\tUploading model: {run['model']}")
            df_sys = pd.DataFrame(read_data(base_dir, run["name"])).drop("messages", axis=1).drop("expected", axis=1)
            project.upload_system(df_sys, name=run["model"].replace("/", "__"), id_column="id", output_column="actual")

    print(f"\nUploaded {len(tasks)} tasks to Zeno. Go to https://hub.zenoml.com/ to view your data")
