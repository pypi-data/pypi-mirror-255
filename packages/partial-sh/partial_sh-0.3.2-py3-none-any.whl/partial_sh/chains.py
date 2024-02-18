from langchain.chains.openai_functions import create_structured_output_chain
from langchain.prompts import ChatPromptTemplate

from .functions import PythonCode
from .instruction import InstructionMode


def detect_mode_chain(llm) -> ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a system to transform data, you have the choice between two mode: LLM mode or Code mode.
            Some instructions can be hard to implement it as code, so in the case it does not suits for code mode, you can use LLM mode.
            The LLM mode is more approriate for instructions that are not deterministic. Chose the correct mode for the instruction.
                """,
            ),
            ("human", "INSTRUCTION: {instruction}"),
            ("human", "DATA: {data}"),
            ("human", "Chose the MODE:"),
        ]
    )
    chain = create_structured_output_chain(
        InstructionMode,
        llm,
        prompt,
        verbose=False,
    )
    return chain


def transform_data_chain(
    instruction: str, data: str, header: str | None, prev: str
) -> ChatPromptTemplate:
    messages = [
        (
            "system",
            "Act as a system to transform data, always print the full data, only output the data. No comment or exaplanation. Just the data transformed. Respect the order, do not print again the header",
        ),
        (
            "system",
            "If the data is the header just print the header with the instruction applied. Just output the header no prefix or suffix text",
        ),
        (
            "system",
            "Be consistent with data format and field name that you already generated, in the previous steps. But you have to answer the instruction for the current step. Only be based on the previous data to enforce the format not the content.",
        ),
        ("ai", "PREVIOUS DATA KEYS: {prev}"),
        ("human", "DATA: {data}"),
        ("human", "INSTRUCTION: {instruction}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    if header is not None:
        messages.extend(("human", "HEADER: {header}"))
        prompt = prompt.partial(
            data=data, instruction=instruction, header=header, prev=prev
        )
    else:
        prompt = prompt.partial(data=data, instruction=instruction, prev=prev)
    return prompt


def gen_code_chain(llm) -> ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a system to transform data and you have to write the code for it",
            ),
            (
                "system",
                "You have access to the following data: data is a dictionary with the data to transform",
            ),
            (
                "system",
                "Put all the import of the libraries you need inside the function",
            ),
            (
                "system",
                "Dont't write the code inside backticks",
            ),
            (
                "system",
                "Write the code to transform the data based on the instruction, generate just the code to transform the data inplace.",
            ),
            (
                "system",
                """Output only the code like that:
                CODE TO RETURN EXAMPLE:
                name_parts = data['name'].split()
                data['first_name'] = name_parts[0]
                data['last_name'] = name_parts[1]
                del data['name']
                """,
            ),
            (
                "system",
                "The created data should always be returned in the variable data, create new fields or modify existing fields if required.",
            ),
            ("human", "DATA: {data}"),
            ("human", "INSTRUCTION: {instruction}"),
        ]
    )

    chain = create_structured_output_chain(
        PythonCode,
        llm,
        prompt,
        verbose=False,
    )
    return chain
