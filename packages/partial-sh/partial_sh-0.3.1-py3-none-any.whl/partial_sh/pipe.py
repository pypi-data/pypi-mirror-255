#!/usr/bin/env python3
import argparse
import json
import logging
import os
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Union

from e2b import CodeInterpreter
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI


def get_version():
    import importlib

    pkg_name = "partial-sh"
    pkg_version = importlib.metadata.version("partial_sh")

    return f"{pkg_name} {pkg_version}"


# Get the environment variable, with a fallback default value
partial_config_path = os.getenv("PARTIAL_CONFIG_PATH", "~/.config/partial/")

# Expand the user's home directory (`~`) to an absolute path
config_path = Path(os.path.expanduser(partial_config_path))

# Create folder if it does not exist
if not os.path.exists(config_path):
    os.makedirs(config_path)

code_base_path = config_path / Path("./codes")
pipeline_base_path = config_path / Path("./pipelines")


class Modes(Enum):
    LLM = "LLM"
    CODE = "CODE"


state = {
    "llm": None,
    "sandbox": None,
}


class InstructionMetadata(BaseModel):
    instruction: str
    mode: Union[Modes, None] = None


class PipelineConfig(BaseModel):
    instructions: list[InstructionMetadata]
    codes: dict[str, str]
    repeat: int = 1


class ImplementationMode(BaseModel):
    mode: str = Field(description="The mode to use: LLM or CODE")


def detect_mode_chain(state) -> ChatPromptTemplate:
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
        ImplementationMode,
        state["llm"],
        prompt,
        verbose=False,
    )
    return chain


class PythonCode(BaseModel):
    code: str = Field(description="The code generated to transform the data")


def gen_code_chain(state) -> ChatPromptTemplate:
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
        state["llm"],
        prompt,
        verbose=False,
    )
    return chain


def gen_code(chain, instruction: str, data: str):
    res = chain.invoke({"data": data, "instruction": instruction})
    code = res["function"].code
    return code


def transform_chain(
    instruction: str, data: str, header: Union[str, None], prev: str
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


def execute_step(
    state, instruction: str, data: str, header: str | None, prev: str | None
) -> str:
    prompt = transform_chain(instruction, data, header, prev)
    chain = prompt | state["llm"]
    output = chain.invoke({})
    content = output.content
    return content


def lowercase_and_replace(s):
    s = s.lower().replace(" ", "_")
    # Remove special characters except for underscore
    return re.sub(r"[^a-z0-9_]", "", s)


class ShowExamplesAction(argparse.Action):
    def __init__(self, option_strings, dest, examples=None, **kwargs):
        self.examples = examples
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(self.examples)
        parser.exit()


help_examples = """
+---------------+
| Pipe as input |
+---------------+

$ echo '{"name":"Jay Neal", "address": "42 Main St 94111"}' | pt -i "Split firstname and lastname" -i "remove the address"

{"first_name": "Jay", "last_name": "Neal"}

+-----------------------------+
| Multi lines with JSON Lines |
+-----------------------------+

$ cat << EOF > data.jsonl
{"name":"John Doe","date_of_birth":"1980-01-01", "address": "123 Main St"}
{"name":"Jane Smith","date_of_birth":"1990-02-15", "address": "456 Main St"}
{"name":"Jay Neal","date_of_birth":"1993-07-27", "address": "42 Main St 94111"}
{"name":"Lisa Ray","date_of_birth":"1985-03-03", "address": "789 Elm St"}
EOF

$ cat data.jsonl | pt -i "Split firstname and lastname" -i "remove the address"

{"date_of_birth": "1980-01-01", "first_name": "John", "last_name": "Doe"}
{"date_of_birth": "1990-02-15", "first_name": "Jane", "last_name": "Smith"}
{"date_of_birth": "1993-07-27", "first_name": "Jay", "last_name": "Neal"}
{"date_of_birth": "1985-03-03", "first_name": "Lisa", "last_name": "Ray"}

+---------------+
| File as input |
+---------------+

$ cat << EOF > invoice.json
{"products":[
  {"name":"Laptop","price":1000},
  {"name":"Smartphone","price":600},
  {"name":"Headphones","price":70}
]}
EOF

$ pt --file invoice.json \\
-i 'give me the invoice total price' \\
-i 'give me the field invoice_total only'

{"invoice_total": 1670}

"""


def get_args():
    examples = """
Example:

    $ echo '{"name":"Jay Neal", "address": "42 Main St 94111"}' | pt -i "Split firstname and lastname" -i "remove the address"

    {"first_name": "Jay", "last_name": "Neal"}

    """
    parser = argparse.ArgumentParser(
        description="Transform JSON data with LLM",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparser = parser.add_subparsers(dest="command", help="Available commands")

    subparser.add_parser("setup", help="Setup partial")
    subparser.add_parser("config", help="Display the configuration location")
    subparser.add_parser("store", help="Display the functions in the store")

    # Pipelines
    pipelines_parser = subparser.add_parser(
        "pipelines", help="Display the available pipelines"
    )
    pipelines_subparser = pipelines_parser.add_subparsers(
        dest="pipelines_command", help="Available commands"
    )
    pipelines_subparser.add_parser("ls", help="Display the available pipelines")
    pipelines_rm_parser = pipelines_subparser.add_parser("rm", help="Remove a pipeline")
    pipelines_rm_parser.add_argument("pipeline", help="The pipeline to remove")
    pipeline_show_parser = pipelines_subparser.add_parser(
        "show", help="Display the pipeline"
    )
    pipeline_show_parser.add_argument("pipeline", help="The pipeline to display")

    llm_code_group = parser.add_mutually_exclusive_group()
    local_sandbox_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "--examples",
        required=False,
        action=ShowExamplesAction,
        examples=help_examples,
        help="Show examples",
    )

    parser.add_argument(
        "--instruction",
        "-i",
        required=False,
        action="append",
        help="Instruction for the LLM, multiple instructions can be provided",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Debug mode, write to debug file",
    )
    llm_code_group.add_argument(
        "--code",
        "-c",
        action="store_true",
        help="Generate code to execute the transformation",
    )
    llm_code_group.add_argument(
        "--llm",
        "-l",
        action="store_true",
        help="Use LLM to execute the transformation",
    )
    parser.add_argument(
        "--pipeline",
        "-p",
        help="Use a pipeline over the data",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Read the input data from a file",
    )
    parser.add_argument(
        "--repeat",
        "-r",
        type=int,
        choices=range(1, 10),
        default=1,
        help="Repeat the instruction multiple time",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version(),
    )
    local_sandbox_group.add_argument(
        "--local",
        "-L",
        action="store_true",
        help="Use local code execution",
    )
    local_sandbox_group.add_argument(
        "--sandbox",
        "-S",
        action="store_true",
        help="Use sandbox code execution",
    )
    parser.add_argument(
        "--regenerate",
        "-R",
        action="store_true",
        help="Do not use cache, generate code each time",
    )
    return parser, parser.parse_args()


def write_code_file(code, instruction):
    code_filename = lowercase_and_replace(instruction) + ".py"

    # Create folder if it does not exist
    if not os.path.exists(code_base_path):
        os.makedirs(code_base_path)

    with open(code_base_path / code_filename, "w") as f:
        f.write(code)


def is_code_file_exists(instruction):
    code_filename = lowercase_and_replace(instruction) + ".py"
    return os.path.exists(code_base_path / code_filename)


def read_code_file(instruction):
    code_filename = lowercase_and_replace(instruction) + ".py"
    with open(code_base_path / code_filename, "r") as f:
        code = f.read()
    return code


def show_store():
    print("Codes:", code_base_path)
    for filename in os.listdir(code_base_path):
        if filename.endswith(".py"):
            print("- ", filename[:-3])
    print("")
    print("Pipelines:", pipeline_base_path)
    for filename in os.listdir(pipeline_base_path):
        if filename.endswith(".json"):
            print("- ", filename[:-5])


def list_pipelines():
    print("Pipelines:", pipeline_base_path)
    for filename in os.listdir(pipeline_base_path):
        if filename.endswith(".json"):
            print("- ", filename[:-5])


def show_config():
    print("Location:", config_path / "setup.json")

    # Read setup file
    if os.path.exists(config_path / "setup.json"):
        with open(config_path / "setup.json", "r") as f:
            config = json.loads(f.read())
    else:
        print("Config file not found")
        print("Execute comamnd#: partial setup")
        sys.exit(1)

    print("Setup:")
    print("- llm:", config["llm"])
    print("- code_execution:", config["code_execution"])

    print("")
    print("Environment variables:")
    print(
        "- PARTIAL_CONFIG_PATH",
        "\tis set\t" if os.getenv("PARTIAL_CONFIG_PATH") else "\tnot set\t",
        "\tcurrent:",
        config_path,
    )

    openai_api_key = os.getenv("OPENAI_API_KEY", None)
    print(
        "- OPENAI_API_KEY",
        "\tis set\t" if openai_api_key else "\tnot set\t",
        "\tcurrent:",
        # show only the first 3 characters and last 4 characters, hide the middle part
        openai_api_key[:3] + "..." + openai_api_key[-4:] if openai_api_key else "",
    )

    e2b_api_key = os.getenv("E2B_API_KEY", None)
    print(
        "- E2B_API_KEY",
        "\t\tis set\t" if e2b_api_key else "\t\tnot set\t",
        "\tcurrent:",
        # show only the first 3 characters and last 4 characters, hide the middle part
        e2b_api_key[:3] + "..." + e2b_api_key[-4:] if e2b_api_key else "",
    )

    # Read file content
    print("Credentials files:")
    if os.path.exists(config_path / "openai_api_key"):
        with open(config_path / "openai_api_key", "r") as f:
            openai_api_key = f.read()
    else:
        openai_api_key = None

    print(
        "- openai_api_key",
        "\tis set\t" if openai_api_key else "\tnot set\t",
        "\tcurrent:",
        # show only the first 3 characters and last 4 characters, hide the middle part
        openai_api_key[:3] + "..." + openai_api_key[-4:] if openai_api_key else "\t",
        "\tfile:",
        config_path / "openai_api_key",
    )

    if os.path.exists(config_path / "e2b_api_key"):
        with open(config_path / "e2b_api_key", "r") as f:
            e2b_api_key = f.read()
    else:
        e2b_api_key = None

    print(
        "- e2b_api_key",
        "\t\tis set\t" if e2b_api_key else "\t\tnot set\t",
        "\tcurrent:",
        # show only the first 3 characters and last 4 characters, hide the middle part
        e2b_api_key[:3] + "..." + e2b_api_key[-4:] if e2b_api_key else "\t",
        "\tfile:",
        config_path / "e2b_api_key",
    )


def create_pipeline(instructions: list[InstructionMetadata], codes: dict = {}):
    if not os.path.exists(pipeline_base_path):
        os.makedirs(pipeline_base_path)

    filename = instructions[0].instruction
    pipeline_filename = lowercase_and_replace(filename) + ".json"

    pipeline = PipelineConfig(instructions=instructions, codes=codes)

    with open(pipeline_base_path / pipeline_filename, "w") as f:
        f.write(pipeline.json(indent=4))


def write_to_code_store(store, code, instruction):
    code_name = lowercase_and_replace(instruction)
    store[code_name] = code
    return store


def get_code_store(store, instruction):
    code_name = lowercase_and_replace(instruction)
    return store.get(code_name)


def parse_incremental(data):
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(data):
        try:
            obj, pos = decoder.raw_decode(data, pos)
            yield obj
        except json.JSONDecodeError:
            pos += 1


def validate_args(args):
    valid_args = args.instruction or args.pipeline
    if not valid_args:
        return False
    return True


def read_input(args):
    """
    Read input data based on the arguments.
    """

    if args.file:
        with open(args.file, "r") as f:
            return parse_incremental(f.read())
    else:
        return parse_incremental(sys.stdin.read())


def init_pipeline(args):
    code_store = {}
    if args.llm:
        mode = Modes.LLM
    elif args.code:
        mode = Modes.CODE
    else:
        mode = None
    instructions = [
        InstructionMetadata(instruction=i, mode=mode) for i in args.instruction
    ]
    repeat = args.repeat

    return PipelineConfig(codes=code_store, instructions=instructions, repeat=repeat)


def load_pipeline(pipeline):
    if pipeline.endswith(".json"):
        pipeline_file = pipeline
    else:
        pipeline_file = pipeline_base_path / (pipeline + ".json")
    if not os.path.exists(pipeline_file):
        print("Pipeline file not found:", pipeline_file)
        sys.exit(1)
    pipeline = PipelineConfig.parse_file(pipeline_file)
    return pipeline


def detect_instruction_mode(state, instruction, data):
    detect_mode = detect_mode_chain(state)
    mode_detected = detect_mode.invoke({"instruction": instruction, "data": data})
    mode = Modes.LLM if mode_detected["function"].mode.upper() == "LLM" else Modes.CODE
    return mode


def execute_llm(state, prev_data, line, instruction):
    prev_data = prev_data or line
    prev_keys = ",".join(prev_data.keys())
    line = json.dumps(line)
    output = execute_step(
        state=state, instruction=instruction, data=line, header=None, prev=prev_keys
    )
    logging.debug(f"OUTPUT LLM: {output}")

    if "{" in output:
        output = output[output.index("{") :]
    else:
        output = json.dumps({"output": output})
    return output


def execute_code(state, pipeline, line, instruction, regenerate=False):
    # lookup for the code in the store or generate it
    if (
        get_code_store(pipeline.codes, instruction) is None
        and not is_code_file_exists(instruction)
    ) or regenerate:
        logging.debug("Generating code")
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            sys.stderr.write(
                "Code generation in progress...\n",
            )
        chain = gen_code_chain(state)
        code = gen_code(chain, instruction, line)

        if logging.getLogger().isEnabledFor(logging.DEBUG) and sys.stdout.isatty():
            sys.stderr.write(
                f"Generated code:\n{code}\n---\n",
            )
            ask = input("\nExecute code? [Y/n]: ")

            if ask.lower() == "n" or ask.lower() == "no":
                sys.exit(1)
            sys.stderr.write("---\n")

        write_code_file(code, instruction)
        write_to_code_store(pipeline.codes, code, instruction)
        logging.debug("Code generated and saved")

    code = get_code_store(pipeline.codes, instruction) or read_code_file(instruction)
    logging.debug(f"CODE: {code}")

    # save the code in the store
    pipeline.codes[lowercase_and_replace(instruction)] = code

    # peprare data for the code execution
    line_data = json.loads(line) if isinstance(line, str) else line
    vars = {"data": line_data}

    # execute the code
    try:
        logging.debug(
            f"Executing code: {code}",
        )
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            sys.stderr.write(
                f"Executing code:\n{code}\n---\n",
            )
        sandbox = state["sandbox"]
        if sandbox:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                sys.stderr.write("Running code in sandbox\n")
            code = (
                f"import json\ndata={vars['data']}\n"
                + code
                + "\nprint(json.dumps(data))"
            )
            stdout, stderr, artifacts = sandbox.run_python(code)
            if stderr:
                print(f"Error while executing the code: {stderr}")
                sys.exit(1)
            vars["data"] = json.loads(stdout)
        else:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                sys.stderr.write("Running code locally\n")
            exec(code, vars)
    except Exception as e:
        print("Error while executing the code")
        print(e)
        logging.exception(
            "Error while executing the code:\n"
            + "INSTRUCTION: "
            + instruction
            + "\n"
            + "DATA: "
            + str(line_data)
            + "\n"
            + "CODE:\n"
            + code
            + "\n\n"
        )

        sys.stderr.write(
            "Error while executing the code:\n"
            + "INSTRUCTION: "
            + instruction
            + "\n"
            + "DATA: "
            + str(line_data)
            + "\n"
            + "CODE:\n"
            + code
            + "\n\n"
        )
        sys.exit(1)
    output_dict = vars["data"]
    output = json.dumps(output_dict)
    return output


def print_output(output):
    # Check if last char is a new line
    if output[-1] == "\n":
        sys.stdout.write(output)
    else:
        sys.stdout.write(output + "\n")


def process_line(state, line, pipeline):
    prev_data = None

    for instruciton in pipeline.instructions:
        mode = instruciton.mode or detect_instruction_mode(
            state, instruciton.instruction, line
        )
        instruciton.mode = mode

        logging.debug(
            f"INPUT: {line} INSTRUCTION: {instruciton.instruction} MODE: {mode.value}"
        )

        if mode == Modes.LLM:
            output = execute_llm(state, prev_data, line, instruciton.instruction)
        else:
            regenerate = state["regenerate"]
            output = execute_code(
                state, pipeline, line, instruciton.instruction, regenerate=regenerate
            )
            state["regenerate"] = False

        logging.debug(f"OUTPUT: {output}")
        # Pass the output to the next step
        line = output
        # Help the next step by passing the previous data
        prev_data = json.loads(output)

    return output


def process_data(state, lines, pipeline):
    for line in lines:
        for ri in range(pipeline.repeat):
            logging.debug(f"REPEAT ITERATION: {ri}")
            output = process_line(state, line, pipeline)
            print_output(output)


def resolve_pipeline(pipeline):
    if pipeline.endswith(".json"):
        pipeline_file = pipeline
    else:
        pipeline_file = pipeline_base_path / (pipeline + ".json")
    if not os.path.exists(pipeline_file):
        print("Pipeline file not found:", pipeline_file)
        sys.exit(1)
    return pipeline_file


def remove_pipeline(pipeline):
    print("Remove pipeline:", pipeline)
    pipeline_file = resolve_pipeline(pipeline)
    os.remove(pipeline_file)
    print("Pipeline removed")


def show_pipeline(pipeline):
    pipeline_file = resolve_pipeline(pipeline)
    with open(pipeline_file, "r") as f:
        pipeline_data = json.loads(f.read())
        display_pipeline(pipeline, pipeline_file, pipeline_data)


def display_pipeline(name, filepath, pipeline_data):
    print(f"Pipeline: {name}\nFile: {filepath}\n-------------------")

    # Print instructions
    print("Instructions:")
    for i, instruction in enumerate(pipeline_data["instructions"], 1):
        print(f"  {i}. {instruction['instruction']} (Mode: {instruction['mode']})")

    # Print codes
    print("\nCodes:")
    for name, code in pipeline_data["codes"].items():
        print(f"- {name}:\n\n    {code.replace('\n', '\n    ')}")

    # Other details
    print(f"\nRepeat: {pipeline_data['repeat']}")


def pipeline_command(args):
    if args.pipelines_command == "rm":
        remove_pipeline(args.pipeline)
    elif args.pipelines_command == "ls":
        list_pipelines()
    elif args.pipelines_command == "show":
        show_pipeline(args.pipeline)
    else:
        list_pipelines()


def setup():
    setup = {}

    print("1. Setup LLM: OpenAI\n")
    # Ask for OpenAI API key

    # Mention that partial use openai api
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

    try:
        api_key = input("Enter your OpenAI API key: ")
    except KeyboardInterrupt:
        print("\nSetup aborted")
        sys.exit(1)

    # it should start with sk- and be 51 characters long
    if not api_key.startswith("sk-") or len(api_key) != 51:
        print(
            "Invalid API key, please try again. It should start with sk- and be 51 characters long"
        )
        sys.exit(1)

    with open(config_path / "openai_api_key", "w") as f:
        f.write(api_key)
        print("API key saved:", config_path / "openai_api_key")

    setup["llm"] = "openai"

    # E2B
    # Ask if the user want to setup E2B, for safe code execution in the cloud
    # Mention that E2B is a sandbox to execute code in the cloud

    print("\n2. Setup code execution:\n")
    # Either local or cloud E2B
    try:
        setup_e2b = input(
            "Code execution:\n- local\n- e2b\thttps://e2b.dev\nDo you want to setup [local] or e2b? "
        )
    except KeyboardInterrupt:
        pass
    if setup_e2b is None or setup_e2b == "":
        setup_e2b = "local"

    if setup_e2b.lower() == "e2b":
        # Ask for API key
        try:
            e2b_api_key = input("Enter your e2b API key: ")
        except KeyboardInterrupt:
            print("\nSetup aborted")
            sys.exit(1)

        # it should start with e2b_
        if not e2b_api_key.startswith("e2b_"):
            print("Invalid API key, please try again. It should start with e2b_")
            sys.exit(1)

        # Save the API key
        with open(config_path / "e2b_api_key", "w") as f:
            f.write(e2b_api_key)
            print("API key saved:", config_path / "e2b_api_key")

    setup["code_execution"] = setup_e2b.lower()

    # Save the setup
    with open(config_path / "setup.json", "w") as f:
        f.write(json.dumps(setup, indent=4))
        print("Setup saved:", config_path / "setup.json")

    print("Setup done")


def main():
    try:
        parser, args = get_args()

        if args.command == "setup":
            setup()
            return
        elif args.command == "store":
            show_store()
            return
        elif args.command == "pipelines":
            pipeline_command(args)
            return
        elif args.command == "config":
            show_config()
            return

        if not validate_args(args):
            parser.print_help()
            return

        # Read configuration
        if os.path.exists(config_path / "setup.json"):
            with open(config_path / "setup.json", "r") as f:
                config = json.loads(f.read())

        # Load the API key or get it from the environment variable

        # Check if file exists
        if "OPENAI_API_KEY" in os.environ:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        elif os.path.exists(config_path / "openai_api_key"):
            with open(config_path / "openai_api_key", "r") as f:
                openai_api_key = f.read()
        else:
            print("OpenAI API key not found, please run:\npartial setup")
            sys.exit(1)

        llm = ChatOpenAI(
            model="gpt-4-1106-preview", temperature=0.8, openai_api_key=openai_api_key
        )

        # sandbox
        if (
            (args.sandbox or config["code_execution"] == "e2b")
            and "E2B_API_KEY" in os.environ
            and args.local is False
        ):
            sandbox = CodeInterpreter()
        elif (
            (args.sandbox or config["code_execution"] == "e2b")
            and os.path.exists(config_path / "e2b_api_key")
            and args.local is False
        ):
            e2b_api_key = open(config_path / "e2b_api_key", "r").read()
            sandbox = CodeInterpreter(api_key=e2b_api_key)
        elif args.local:
            sandbox = None
        else:
            sandbox = None

        state["regenerate"] = args.regenerate

        code_execution = "sandbox" if sandbox else "local"
        state["llm"] = llm
        state["sandbox"] = sandbox
        sys.stderr.write(f"Using LLM: {config['llm']}\n")
        sys.stderr.write(f"Using code execution: {code_execution}\n")

        if args.debug:
            logging.basicConfig(
                filename=config_path / "debug.log",
                format="%(asctime)s - %(levelname)s - %(message)s",
                level=logging.DEBUG,
            )
        else:
            logging.basicConfig(
                filename=config_path / "debug.log",
                format="%(asctime)s - %(levelname)s - %(message)s",
                level=logging.INFO,
            )

        logging.debug("debug mode enabled")

        input_data = read_input(args)

        if args.pipeline:
            pipeline = load_pipeline(args.pipeline)
        else:
            pipeline = init_pipeline(args)

        process_data(state, input_data, pipeline)

        create_pipeline(pipeline.instructions, pipeline.codes)

    except KeyboardInterrupt:
        print("\nAborted")
        sys.exit(1)

    finally:
        logging.debug("Shutting down")
        if state["sandbox"]:
            state["sandbox"].close()


if __name__ == "__main__":
    main()
