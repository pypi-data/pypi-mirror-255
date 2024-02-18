from enum import Enum

import typer
from typing_extensions import Annotated

app = typer.Typer()

__version__ = "0.1.0"


@app.command()
def version():
    print(__version__)


@app.command()
def pipelines():
    print("pipelines")


@app.command()
def store():
    print("store")


@app.command()
def config():
    print("config")


class LlmCodeMode(str, Enum):
    """
    The mode
    """

    auto: str = "auto"
    code: str = "code"
    llm: str = "llm"


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    names: list[str],
    mode: LlmCodeMode = LlmCodeMode.auto,
    examples: Annotated[bool, typer.Option("--examples", help="Show examples")] = False,
):
    """
    This is a CLI tool made with Typer.
    """
    if ctx.invoked_subcommand is not None:
        return

    # if ctx.invoked_subcommand is None:
    # print("Hello World")

    print("Hello World")

    print(names)
    # print(f"Hello {name}")
    if examples:
        print("Examples:")
        print("  partial_sh pipelines")
        print("  partial_sh store")
        print("  partial_sh config")

    print("mode:", mode)


if __name__ == "__main__":
    app()
