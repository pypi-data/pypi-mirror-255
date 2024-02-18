import importlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from ..functions import FunctionStore
from ..input import read_input
from ..llm import LLM, Modes
from ..run import InputMode, Run, save_run
from ..runner import Runner
from ..sandbox import Sandbox
from ..shape import Shape
from ..store import ShapeStore
from .examples import epilog_example, help_examples
from .setup import CodeExecutionProvider, SetupConfig
from .utils import MutuallyExclusiveGroup

APP_NAME = "partial-sh"

app = typer.Typer(no_args_is_help=True)


llm_code_exclusive_group = MutuallyExclusiveGroup()
local_sandbox_exclusive_group = MutuallyExclusiveGroup()


def version_callback(value: bool):
    if value:
        pkg_name = APP_NAME.replace("-", "_")
        pkg_version = importlib.metadata.version(pkg_name)
        print(f"{pkg_name} {pkg_version}")
        raise typer.Exit()


def examples_callback(value: bool):
    if value:
        print(help_examples)
        raise typer.Exit()


def read_config_file(config_file: Path) -> Optional[SetupConfig]:
    setup_config = None

    # check if file exists
    if not config_file.exists() or not config_file.is_file():
        return None

    # check if end with .json
    if config_file.suffix != ".json":
        return None

    with (config_file).open("r") as f:
        setup_config = json.load(f)
        setup_config = SetupConfig(**setup_config)

    return setup_config


def print_info(info: str, *args, **kwargs):
    """
    Print info to stderr, to avoid interfering with the output.
    """
    print(info, *args, **kwargs, file=sys.stderr)


def save_shape(shape: Shape, config_path: Path, quiet: bool = False):
    slug = shape.get_slug()
    filepath = config_path / "shapes" / f"{slug}.json"
    shape.save_to_file(file=filepath)
    if quiet is False:
        print_info("Shape ID:", shape.id.split("-")[0])
        print_info(f"Shape save: {filepath}")


@app.callback(invoke_without_command=True, epilog=epilog_example)
def main(
    ctx: typer.Context,
    instruction: Annotated[
        list[str],
        typer.Option(
            "--instruction",
            "-i",
            help="Instructions to follow",
            rich_help_panel="Execution",
        ),
    ] = None,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            rich_help_panel="Info",
        ),
    ] = None,
    examples: Annotated[
        Optional[bool],
        typer.Option(
            "--examples",
            callback=examples_callback,
            is_eager=True,
            rich_help_panel="Info",
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug", "-d", help="Show debug information", rich_help_panel="Execution"
        ),
    ] = False,
    regenerate: Annotated[
        bool,
        typer.Option(
            "--regenerate",
            "-R",
            help="Regenerate the code",
            rich_help_panel="Execution",
        ),
    ] = False,
    llm_mode: Annotated[
        Optional[bool],
        typer.Option(
            "--llm",
            "-l",
            help="Use LLM to execute the transformation",
            callback=llm_code_exclusive_group,
            rich_help_panel="Execution",
        ),
    ] = None,
    code_mode: Annotated[
        Optional[bool],
        typer.Option(
            "--code",
            "-c",
            help="Generate code to execute the transformation",
            callback=llm_code_exclusive_group,
            rich_help_panel="Execution",
        ),
    ] = None,
    local_mode: Annotated[
        Optional[bool],
        typer.Option(
            "--local",
            "-L",
            help="Use local code execution",
            callback=local_sandbox_exclusive_group,
            rich_help_panel="Execution",
        ),
    ] = None,
    sandbox_mode: Annotated[
        Optional[bool],
        typer.Option(
            "--sandbox",
            "-S",
            help="Use sandbox code execution",
            callback=local_sandbox_exclusive_group,
            rich_help_panel="Execution",
        ),
    ] = None,
    repeat: Annotated[
        int,
        typer.Option(
            "--repeat",
            "-r",
            help="Repeat the instruction multiple time",
            min=1,
            max=10,
            rich_help_panel="Execution",
        ),
    ] = 1,
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--file",
            "-f",
            help="Read the input data from a file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            rich_help_panel="Execution",
        ),
    ] = None,
    shape_arg: Annotated[
        Optional[str],
        typer.Option(
            "--shape",
            "-p",
            help="Id, Name or File of the shape",
            rich_help_panel="Execution",
        ),
    ] = None,
    config_file: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            help="Path to the json config file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            rich_help_panel="Execution",
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Only display the output data",
            rich_help_panel="Execution",
        ),
    ] = False,
    save: Annotated[
        bool,
        typer.Option(
            "--save",
            "-s",
            help="Save the shape",
            rich_help_panel="Execution",
        ),
    ] = False,
    name: Annotated[
        Optional[str],
        typer.Option(
            "--name",
            "-n",
            help="Name of the shape",
            rich_help_panel="Execution",
        ),
    ] = None,
):
    """
    Transform JSON data with LLM
    """
    # Config path
    config_path = os.getenv("PARTIAL_CONFIG_PATH", None)
    if config_path is None:
        config_path: Path = Path.home() / ".config" / "partial"
    else:
        config_path: Path = Path(config_path)

    # Create storage folders
    config_path.mkdir(parents=True, exist_ok=True)
    function_store_path = config_path / "codes"
    function_store_path.mkdir(parents=True, exist_ok=True)
    shape_store_path = config_path / "shapes"
    shape_store_path.mkdir(parents=True, exist_ok=True)

    if config_file is None:
        config_file = config_path / "setup.json"

    setup_config = read_config_file(config_file)

    if setup_config is None:
        config_file = None
        setup_config = SetupConfig()

    # Pass values to the context
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["config_path"] = config_path

    if ctx.invoked_subcommand is not None:
        return

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if sys.stdout.isatty() is False:
        quiet = True

    if quiet is False:
        # Display config
        print_info("LLM:", setup_config.llm.value)

    local_mode = local_mode or False
    sandbox_mode = sandbox_mode or False

    if (
        sandbox_mode is True or setup_config.code_execution == CodeExecutionProvider.E2B
    ) and local_mode is False:
        sandbox_mode = True
    elif (
        local_mode is True or setup_config.code_execution == CodeExecutionProvider.LOCAL
    ) and sandbox_mode is False:
        sandbox_mode = False
    else:
        sandbox_mode = False

    if quiet is False:
        # Display only the current parameters that will be use for this run
        if sandbox_mode is True:
            print_info("Code execution: e2b (remote sandbox)")
        else:
            print_info("Code execution: local")

    llm_instance = LLM(provider="openai", config_path=config_path)

    sandbox = Sandbox(provider="e2b", config_path=config_path) if sandbox_mode else None

    function_store = FunctionStore(path=config_path / "codes")
    function_store.refresh()

    runner = Runner(
        llm=llm_instance,
        sandbox=sandbox,
        store=function_store,
        quiet=quiet,
    )

    lines = read_input(file=file) if file else read_input()

    shape = Shape()

    # Check if shape arg is a file
    shape_store = ShapeStore(path=config_path / "shapes")
    if shape_arg:
        shape_file = shape_store.find_shape_file(shape_arg)

        if not shape_file:
            typer.echo(f"Shape not found: {shape_arg}", err=True)
            raise typer.Exit(1)

        shape = shape.load_from_file(shape_file)
    else:
        if llm_mode:
            mode = Modes.LLM
        elif code_mode:
            mode = Modes.CODE
        else:
            mode = None

        shape = shape.new(
            name=name,
            instructions=instruction,
            repeat=repeat,
            regenerate=regenerate,
            mode=mode,
        )

    if shape.name is None:
        shape.name = shape.get_prep_name()

    if quiet is False:
        print_info("--- start")

    run = Run(
        shape=shape,
        input_mode=InputMode.FILE_ if file else InputMode.STDIN_,
    )

    run_res = runner.process(
        lines=lines,
        # shape=shape,
        run=run,
    )

    runner.terminate()

    if quiet is False:
        print_info("--- end")
    # Save shape
    if save:
        save_run(run_res, config_path, quiet=quiet)
        save_shape(shape, config_path, quiet=quiet)
