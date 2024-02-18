from enum import Enum

from langchain.pydantic_v1 import BaseModel, Field


class Modes(Enum):
    LLM = "LLM"
    CODE = "CODE"


class InstructionMetadata(BaseModel):
    instruction: str
    mode: Modes | None = None


class InstructionMode(BaseModel):
    mode: str = Field(description="The mode to use: LLM or CODE")
