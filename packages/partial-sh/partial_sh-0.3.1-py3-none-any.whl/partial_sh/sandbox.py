import logging
import os
from pathlib import Path

import typer
from e2b import CodeInterpreter

logger = logging.getLogger(__name__)


def init_interpreter_e2b(config_path: Path):
    if "E2B_API_KEY" in os.environ:
        e2b_api_key = os.getenv("E2B_API_KEY")
    elif os.path.exists(config_path / "e2b_api_key"):
        with open(config_path / "e2b_api_key", "r") as f:
            e2b_api_key = f.read()
    else:
        print("E2B API key not found, please run:\npartial setup")
        raise typer.Exit(1)

    # Create interpreter instance
    interpreter = CodeInterpreter(api_key=e2b_api_key)
    return interpreter


class ProviderNotSupported(Exception):
    pass


class Sandbox:
    """
    Sandbox to run code in a safe environment.

    Cloud sandbox available:
    - e2b
    """

    provider = None
    interpreter = None

    def __init__(
        self, provider="e2b", config_path: Path = Path.home() / ".config" / "partial"
    ):
        self.provider = provider
        self.interpreter = self.connnect(config_path=config_path)

    def connnect(self, config_path: Path):
        if self.provider == "e2b":
            logger.info("Connecting to e2b")
            self.interpreter = init_interpreter_e2b(config_path)
            logger.info("Connected to e2b")
        else:
            raise ProviderNotSupported("Provider not supported")

        return self.interpreter

    def run(self, code):
        stdout, stderr, artifacts = self.interpreter.run_python(code)
        if stderr:
            logger.error(stderr)
            raise Exception(stderr)
        return stdout

    def close(self):
        logger.info("Closing sandbox")
        self.interpreter.close()
        logger.info("Sandbox closed")
