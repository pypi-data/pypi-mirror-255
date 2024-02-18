from enum import Enum
from pathlib import Path

import typer
from langchain.pydantic_v1 import BaseModel

app = typer.Typer()


class LLMProvider(Enum):
    OPENAI = "openai"


class CodeExecutionProvider(Enum):
    LOCAL = "local"
    E2B = "e2b"


class SetupConfig(BaseModel):
    llm: LLMProvider = LLMProvider.OPENAI
    code_execution: CodeExecutionProvider = CodeExecutionProvider.LOCAL


OPENAI_KEY_LENGTH = 51
OPENAI_KEY_PREFIX = "sk-"
E2B_KEY_PREFIX = "e2b_"


def validate_api_key(key: str, prefix: str, length: int = None) -> bool:
    """Validates the API key format."""
    return key.startswith(prefix) and (length is None or len(key) == length)


def save_to_file(content: str, filepath: Path) -> None:
    """Saves content to a file."""
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Saved: {filepath}")


def setup_llm(config_path: Path) -> LLMProvider:
    """Setups LLM provider."""
    print("1. Setup LLM: OpenAI\n")
    print(
        "Partial use OpenAI API to:\n"
        + "- detect the mode of the instruction (LLM or CODE)\n"
        + "- generate code\n"
        + "- perform LLM transformation\n"
        + "- select fields to use\n"
    )
    print(
        "You can find your API key here:\n" "- https://platform.openai.com/api-keys\n"
    )

    openai_api_key = typer.prompt("Enter your OpenAI API key")

    if not validate_api_key(openai_api_key, OPENAI_KEY_PREFIX, OPENAI_KEY_LENGTH):
        print(
            "Invalid API key, please try again. It should start with sk- and be 51 characters long"
        )
        raise typer.Exit(1)

    save_to_file(openai_api_key, config_path / "openai_api_key")
    return LLMProvider.OPENAI


def setup_code_execution(config_path: Path) -> CodeExecutionProvider:
    """Setups code execution provider."""
    print("\n2. Setup code execution:\n")
    code_execution_res = typer.prompt(
        "Code execution:\n- local\n- e2b\thttps://e2b.dev\nDo you want to setup [local] or e2b"
    )

    if code_execution_res.lower() == CodeExecutionProvider.E2B.value:
        print(
            "E2B is a sandbox to execute code in the cloud.\n"
            + "You can find your API key here:\n"
            + "- https://e2b.dev/account\n"
        )

        e2b_api_key = typer.prompt("Enter your E2B API key")

        if not validate_api_key(e2b_api_key, E2B_KEY_PREFIX):
            print("Invalid API key, please try again. It should start with e2b_")
            raise typer.Exit(1)

        save_to_file(e2b_api_key, config_path / "e2b_api_key")
        return CodeExecutionProvider.E2B

    return CodeExecutionProvider.LOCAL


def setup_location(config_path: Path):
    """Setups the location of the configuration file."""
    config_path_res = typer.prompt(
        "Enter the location where you want to save the configuration file",
        default=str(config_path),
    )
    config_path = Path(config_path_res)
    if not config_path.is_dir():
        print("Invalid location, please try again.")
        raise typer.Exit(1)
    return config_path


@app.callback(invoke_without_command=True)
def setup(ctx: typer.Context):
    """Setups the application with LLM and code execution providers."""
    config_path = Path(ctx.obj["config_path"])

    # config_path = setup_location(config_path)
    llm_provider = setup_llm(config_path)
    code_execution_provider = setup_code_execution(config_path)

    setup_config = SetupConfig(llm=llm_provider, code_execution=code_execution_provider)

    print("\n3. Setup complete\n")

    save_to_file(setup_config.json(indent=4), config_path / "setup.json")
    print("\nPartial ready to use: pt --examples")
