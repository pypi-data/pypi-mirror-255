import json
import os
from pathlib import Path
from typing import Annotated, Dict, Optional

import typer
from langchain.pydantic_v1 import BaseModel

app = typer.Typer()


class SetupConfig(BaseModel):
    llm: Optional[str]
    code_execution: Optional[str]
    file_path: Optional[Path]


class EnvVar(BaseModel):
    is_set: bool
    value: Optional[str]
    masked_value: Optional[str]


class CredentialFile(BaseModel):
    is_set: bool
    file_path: Optional[Path]
    masked_value: Optional[str]


class CompleteConfig(BaseModel):
    setup: SetupConfig
    env_vars: Dict[str, EnvVar]
    credentials: Dict[str, CredentialFile]


def read_file_content(file_path: Path) -> Optional[str]:
    if file_path.exists():
        with file_path.open("r") as f:
            return f.read().strip()
    return None


def mask_value(value: str) -> str:
    return f"{value[:3]}...{value[-4:]}" if value else ""


def retrieve_config_data(config_path: Path) -> CompleteConfig:
    # Read setup file
    setup_file_path = config_path / "setup.json"
    setup_config = SetupConfig()
    if setup_file_path.is_file():
        with setup_file_path.open("r") as f:
            setup_config = SetupConfig(file_path=setup_file_path, **json.load(f))

    # Read environment variables
    partial_config_path = os.getenv("PARTIAL_CONFIG_PATH")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    e2b_api_key = os.getenv("E2B_API_KEY")

    env_vars = {
        "PARTIAL_CONFIG_PATH": EnvVar(
            is_set=bool(partial_config_path),
            value=partial_config_path,
            masked_value=None,
        ),
        "OPENAI_API_KEY": EnvVar(
            is_set=bool(openai_api_key),
            value=openai_api_key,
            masked_value=mask_value(openai_api_key),
        ),
        "E2B_API_KEY": EnvVar(
            is_set=bool(e2b_api_key),
            value=e2b_api_key,
            masked_value=mask_value(e2b_api_key),
        ),
    }

    # Read credential files
    openai_api_key_content = read_file_content(config_path / "openai_api_key")
    e2b_api_key_content = read_file_content(config_path / "e2b_api_key")

    credentials = {
        "openai_api_key": CredentialFile(
            is_set=bool(openai_api_key_content),
            file_path=config_path / "openai_api_key",
            masked_value=mask_value(openai_api_key_content),
        ),
        "e2b_api_key": CredentialFile(
            is_set=bool(e2b_api_key_content),
            file_path=config_path / "e2b_api_key",
            masked_value=mask_value(e2b_api_key_content),
        ),
    }

    complete_config = CompleteConfig(
        setup=setup_config, env_vars=env_vars, credentials=credentials
    )

    return complete_config


def display_config(complete_config: CompleteConfig):
    setup_config = complete_config.setup
    env_vars = complete_config.env_vars
    credentials = complete_config.credentials

    if setup_config.file_path is None:
        print("+--------------------------------------------------------+")
        print("| Config file not found, execute command: partial setup  |")
        print("+--------------------------------------------------------+")

    print("Location:", setup_config.file_path or "Not set")
    print("Setup:")
    print(f"- llm: {setup_config.llm or 'Not set'}")
    print(f"- code_execution: {setup_config.code_execution or 'Not set'}")

    print("\nEnvironment variables:")
    for name, var in env_vars.items():
        status = "is set" if var.is_set else "not set"
        current = (
            f"current: {var.masked_value or var.value}" if var.is_set else "current:"
        )
        print(f"- {name:<20} {status:<20} {current}")

    print("\nCredentials files:")
    for name, cred in credentials.items():
        status = "is set" if cred.is_set else "not set"
        current = f"current: {cred.masked_value}" if cred.is_set else "current:"
        file_info = f"file: {cred.file_path}" if cred.file_path else ""
        print(f"- {name:<20} {status:<20} {current:<30} {file_info}")


@app.callback(invoke_without_command=True)
def config(
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
    config_path = ctx.obj["config_path"]
    complete_config = retrieve_config_data(config_path)

    if json_output:
        print(complete_config.json(indent=4))
    else:
        display_config(complete_config)
