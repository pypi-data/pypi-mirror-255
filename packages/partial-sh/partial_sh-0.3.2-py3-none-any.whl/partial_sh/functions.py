import logging
import os
import re
from pathlib import Path

from langchain.pydantic_v1 import BaseModel, Field

logger = logging.getLogger(__name__)


def prepare_key(s):
    s = s.lower().replace(" ", "_")
    # Remove special characters except for underscore
    return re.sub(r"[^a-z0-9_]", "", s)


class PythonCode(BaseModel):
    code: str = Field(description="The code generated to transform the data")


class FunctionNameAlreadyExists(Exception):
    pass


class FunctionItem(BaseModel):
    # id: str | UUID = Field(default_factory=uuid4)
    name: str
    code: PythonCode = None
    filename: str = None
    # data_schema: dict[str, str] # TODO: Add the data schema


class FunctionStore:
    path: Path
    functions: dict[str, FunctionItem] = {}

    def __init__(self, path: Path):
        self.path = path

    def refresh(self):
        logger.info(f"Refreshing function store: {self.path}")
        self.functions = {}
        self.load_files()

    def load_files(self):
        """
        Load the files in the function store.
        """
        logger.info(f"Loading files from function store: {self.path}")
        for filename in os.listdir(self.path):
            if filename.endswith(".py"):
                function_name = filename[:-3]
                function_item = FunctionItem(name=function_name, filename=filename)
                self.functions[function_name] = function_item
        return self.functions

    def get_code(self, function_name: str) -> str:
        """
        Get the code for the given function name.
        """
        logger.info(f"Getting code to store for function: {function_name}")
        function_name = prepare_key(function_name)
        function_item = self.functions.get(function_name)
        if not function_item:
            return None
        if function_item.code:
            return function_item.code.code
        code = self.load_code(function_name)
        function_item.code = code
        return code.code

    def load_code(self, function_name: str) -> PythonCode:
        """
        Load the code from the file.
        """
        logger.info(f"Loading code to store for function: {function_name}")
        function_name = prepare_key(function_name)
        function_item = self.functions.get(function_name)
        if not function_item:
            return None
        code_file = self.path / function_item.filename
        with code_file.open("r") as f:
            code = PythonCode(code=f.read())
            return code

    def save_code(self, function_name: str, code: str, replace: bool = False):
        """
        Save the code to the file.

        Returns True if the code was saved successfully.
        """
        logger.info(f"Saving code to store for function: {function_name}")
        function_name = prepare_key(function_name)
        function_item = self.functions.get(function_name)
        if function_item and not replace:
            raise FunctionNameAlreadyExists(
                f"Function already exists with name: {function_name}"
            )
        code_file = self.path / f"{function_name}.py"
        with code_file.open("w") as f:
            f.write(code)
