import json
from typing import Optional

import typer
from rich import print, print_json
from rich.console import Console
from typing_extensions import Annotated

__version__ = "0.1.0"

app = typer.Typer()

err_console = Console(stderr=True)

data = {
    "name": "John",
    "lastname": "Doe",
    "uppercase": False,
    "age": 42,
}


def version_callback(value: bool):
    if value:
        print(f"{__version__}")
        raise typer.Exit()


@app.command()
def main(is_awesome: bool = False):
    if is_awesome:
        print("This is awesome!")
        print(data)
        print_json(json.dumps(data))
        raise typer.Exit(1)
    else:
        print("Hello World")
        raise typer.Abort()


@app.command()
def hello(name: str, lastname: str = "", uppercase: bool = False):
    """
    Say hello to NAME, optionally with a --lastname.
    Turn it uppercase with --uppercase.
    """
    if uppercase:
        name = name.upper()
        lastname = lastname.upper()
    print("Hello", name, lastname)

    err_console.print("This is an error")


@app.command()
def goodbye():
    print("Goodbye")


@app.command()
def args(
    name: Annotated[str, typer.Argument(help="Name of the user")],
    age: Annotated[
        int,
        typer.Option("--age", "-a", help="Age of the user", prompt="Give me your age"),
    ],
    instruction: Annotated[
        list[str], typer.Option("--instruction", "-i", help="Instructions to follow")
    ],
    lastname: Annotated[
        Optional[str], typer.Argument(help="Lastname of the user")
    ] = None,
    uppercase: Annotated[bool, typer.Option(help="Uppercase the name")] = False,
    version: Annotated[
        bool, typer.Option("--version", "-v", callback=version_callback, is_eager=True)
    ] = None,
):
    if name:
        if uppercase:
            name = name.upper()
            lastname = lastname.upper() if lastname else None
        print("Hello", name, lastname or "")
    else:
        print("Hello World")

    print("Age:", age)
    print("Instruction:", instruction)


if __name__ == "__main__":
    app()
