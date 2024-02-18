import logging
import os
from pathlib import Path

import openai
import typer
from langchain_openai import ChatOpenAI
from openai import AuthenticationError

from .chains import detect_mode_chain, gen_code_chain, transform_data_chain
from .instruction import Modes

logger = logging.getLogger(__name__)


def init_openai(config_path: Path):
    # Check if file exists
    if "OPENAI_API_KEY" in os.environ:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    elif os.path.exists(config_path / "openai_api_key"):
        with open(config_path / "openai_api_key", "r") as f:
            openai_api_key = f.read()
    else:
        print("OpenAI API key not found, please run:\npartial setup")
        raise typer.Exit(1)

    # Create LLM instance
    llm = ChatOpenAI(
        model="gpt-4-1106-preview", temperature=0.8, openai_api_key=openai_api_key
    )

    return llm


class ProviderNotSupported(Exception):
    pass


class LLM:
    provider = None
    llm = None

    def __init__(
        self, provider="openai", config_path: Path = Path.home() / ".config" / "partial"
    ):
        self.provider = provider
        self.llm = self.connect(config_path)

    def connect(self, config_path: Path):
        if self.provider == "openai":
            self.llm = init_openai(config_path)
            # self.raise_api_unvalid()  # TODO: Move this to the setup command
        else:
            raise ProviderNotSupported("Provider not supported")
        return self.llm

    def raise_api_unvalid(self) -> bool:
        try:
            openai.models.list()
        except AuthenticationError:
            print("OpenAI API key is not valid")
            print("\nPlease run:\n$ partial setup")
            raise typer.Exit(1)

    def detect_instruction_mode(self, instruction, data):
        detect_mode = detect_mode_chain(self.llm)
        mode_detected = detect_mode.invoke({"instruction": instruction, "data": data})
        mode = (
            Modes.LLM if mode_detected["function"].mode.upper() == "LLM" else Modes.CODE
        )
        return mode

    def transorm_data(
        self, instruction: str, data: str, header: str | None, prev: str | None
    ):
        prompt = transform_data_chain(instruction, data, header, prev)
        chain = prompt | self.llm
        output = chain.invoke({})
        content = output.content
        return content

    def gen_code(self, instruction, data, prev_data):
        chain = gen_code_chain(self.llm)
        res = chain.invoke({"data": data, "instruction": instruction})
        code = res["function"].code
        return code
