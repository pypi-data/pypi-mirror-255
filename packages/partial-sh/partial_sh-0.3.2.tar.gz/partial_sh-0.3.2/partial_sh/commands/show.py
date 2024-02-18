from pathlib import Path

import typer
from typing_extensions import Annotated

from ..store import ShapeStore

app = typer.Typer(no_args_is_help=True)

config_path: Path = Path.home() / ".config" / "partial"
shapes_path = config_path / "shapes"


def display_shape(name, filepath, shape_data):
    print(f"Shape: {name}\nFile: {filepath}\n-------------------")

    # Info
    print(f"ID: {shape_data['id']}")
    print(f"Created at: {shape_data['created_at']}")
    print(f"Updated at: {shape_data['updated_at']}")
    print("")
    # Print instructions
    print("Instructions:")
    for i, instruction in enumerate(shape_data["instructions"], 1):
        print(f"  {i}. {instruction['instruction']} (Mode: {instruction['mode']})")

    # Print codes
    print("\nCode:")
    for name, code in shape_data["code"].items():
        print(f"- {name}:\n\n    {code.replace('\n', '\n    ')}")

    # Other details
    print(f"\nRepeat: {shape_data['repeat']}")


@app.callback(invoke_without_command=True)
def show(
    name_or_id: Annotated[
        str,
        typer.Argument(
            help="Name or ID of the shape to show",
        ),
    ],
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
    Show the shape content
    """
    store = ShapeStore(path=shapes_path)
    store.refresh()

    shape = store.get_by_id(name_or_id) or store.get_by_name(name_or_id)
    if shape is None:
        print(f"Shape not found: {name_or_id}")
        raise typer.Exit(1)

    if json_output:
        print(shape.json(indent=4))
        return

    display_shape(shape.name, store.path / shape.filename, shape.content.dict())
