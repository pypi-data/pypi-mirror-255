from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from langchain.pydantic_v1 import BaseModel
from tabulate import tabulate

app = typer.Typer(no_args_is_help=False)


class RunInfo(BaseModel):
    id: str
    shape_id: str
    start_time: str | None = None
    end_time: str | None = None
    duration_sec: float | None = None
    total_time: str | None = None
    status: str
    input_mode: str
    created_at: str
    updated_at: str


class RunsOutput(BaseModel):
    location: Path
    runs: dict[str, RunInfo] = {}


def parse_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return None


def format_datetime(date_obj):
    if date_obj:
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"


def calculate_duration(start_time, end_time):
    if start_time and end_time:
        delta = end_time - start_time
        return round(delta.total_seconds(), 3)
    return "N/A"


def display_runs(runs_output: RunsOutput):
    runs_path = runs_output.location
    headers = [
        "RUN ID",
        "SHAPE ID",
        "START TIME",
        "END TIME",
        "DURATION (s)",
        "STATUS",
        "INPUT MODE",
        "CREATED AT",
        "UPDATED AT",
    ]
    table = []

    for run_id, run_info in runs_output.runs.items():
        start_time = parse_datetime(run_info.start_time)
        end_time = parse_datetime(run_info.end_time)

        row = [
            run_id,
            run_info.shape_id,
            format_datetime(start_time),
            format_datetime(end_time),
            run_info.duration_sec
            if run_info.duration_sec
            else calculate_duration(start_time, end_time),
            run_info.status,  # Consider translating status codes to messages if needed
            run_info.input_mode,
            format_datetime(parse_datetime(run_info.created_at)),
            format_datetime(parse_datetime(run_info.updated_at)),
        ]
        table.append(row)

    table = sorted(table, key=lambda x: x[7], reverse=True)

    print(f"Location: {runs_path}\n")
    print(tabulate(table, headers=headers, tablefmt="simple"))


def retrieve_runs_data(runs_path: Path):
    runs_output = RunsOutput(location=runs_path)

    for filename in runs_path.iterdir():
        if filename.suffix == ".json":
            run_info = RunInfo.parse_file(filename)
            runs_output.runs[run_info.id] = run_info
    return runs_output


@app.callback(invoke_without_command=True)
def list_runs(
    ctx: typer.Context,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Show the output in JSON format",
        ),
    ] = False,
):
    """
    List the runs in the store.
    """
    config_path = Path(ctx.obj["config_path"])
    runs_path = config_path / "runs"

    runs_output = retrieve_runs_data(runs_path)

    if json_output:
        print(runs_output.json(indent=4))
    else:
        display_runs(runs_output)
