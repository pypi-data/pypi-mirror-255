import copy
import json
import logging

from .functions import FunctionStore
from .instruction import Modes
from .llm import LLM
from .run import LogItemCode, LogItemLlm
from .sandbox import Sandbox
from .shape import Shape

logger = logging.getLogger(__name__)


class ErrorCodeExecution(Exception):
    pass


def execute_llm(llm: LLM, instruction: str, data: str, prev_data: str):
    prev_data = prev_data or data
    # TODO: Fix when data is not a dict
    prev_keys = ",".join(prev_data.keys())
    json_data = json.dumps(data)
    output = llm.transorm_data(
        instruction=instruction,
        data=json_data,
        header=None,
        prev=prev_keys,
    )
    logging.info(f"OUTPUT: {output}")
    if "{" in output:
        output = output[output.index("{") :]
    else:
        output = json.dumps({"output": output})
    return output


def generate_code(
    llm: LLM,
    shape: Shape,
    instruction: str,
    data: str,
    prev_data: str,
    regenerate: bool,
    store: FunctionStore,
):
    # 1. Check if the code needs to be regenerated
    # 0. Generate the code
    # 1. Cache the code
    # 2. Check if the code is cached
    # 0. Generate the code
    # 1. Cache the code
    # 3. return code

    if regenerate:
        logger.info("Regenerate code")
        # 0. Generate the code
        code = llm.gen_code(instruction, data, prev_data)
        shape.save_code(instruction, code)
        # 1. Cache the code
        store.save_code(instruction, code, replace=True)
    else:
        logger.info("Check if code is cached")
        # 2. Check if the code is cached in the shape
        code_from_shape = shape.lookup_code(instruction)
        # 3. Check if the code is cached in the store
        code = code_from_shape or store.get_code(instruction)
        if not code:
            logger.info("Code not cached")
            # 0. Generate the code
            code = llm.gen_code(instruction, data, prev_data)
            # 1. Cache the code
            shape.save_code(instruction, code)
            store.save_code(instruction, code, replace=True)
        elif code_from_shape is None:
            logger.info("Code cached in store only")
            # 0. Cache the code in the shape
            shape.save_code(instruction, code)
            logger.info("Code cached in shape")
        else:
            logger.info("Code cached in shape and store")

    # TODO: Check if code match the data model
    logger.info("Code:\n%s", code)

    return code


def execute_in_sandbox(
    sandbox: Sandbox,
    code: str,
    data: dict,
):
    logger.info("Execute code in sandbox")
    code_with_data = f"import json\ndata={data}\n" + code + "\nprint(json.dumps(data))"
    content = sandbox.run(code_with_data)
    return json.loads(content)


def execute_locally(
    code: str,
    data: dict,
):
    logger.info("Execute code locally")
    # Make a copy of the data to avoid modifying the original data
    data_copy = copy.deepcopy(data)
    vars = {"data": data_copy}
    # Local execution here, modify the data inplace
    try:
        exec(code, vars)
    except Exception as e:
        raise ErrorCodeExecution(f"Error executing code: {e}")

    return json.dumps(vars["data"])


def execute_code(
    sandbox: Sandbox,
    code: str,
    data: str | dict,
):
    """
    Execute the code either in the sandbox or on the local machine.

    Regenerate the code if needed instead of using the cached code.
    """

    # Execute the code
    # a. Check if sandbox is available
    # 0. Execute the code in the sandbox
    # b. Execute the code locally

    # peprare data for the code execution
    data_dict = json.loads(data) if isinstance(data, str) else data

    # check if sandbox is available
    if sandbox is not None:
        logger.info("Sandbox available")
        # execute in sandbox
        output = execute_in_sandbox(
            sandbox=sandbox,
            code=code,
            data=data_dict,
        )
    else:
        logger.info("Sandbox not available")
        # execute locally
        try:
            output = execute_locally(
                code=code,
                data=data_dict,
            )
        except ErrorCodeExecution as e:
            # logger.error("Error executing code: %s", e)
            raise e
    return output


MAX_GENERATION_RETRIES = 3


def process_instruction_llm(llm, instruction, input, prev_data, run):
    output = execute_llm(
        llm=llm,
        instruction=instruction.instruction,
        data=input,
        prev_data=prev_data,
    )
    # Convert to dict if output is a string
    output = json.loads(output) if isinstance(output, str) else output
    run.log(
        LogItemLlm(
            mode="llm",
            instruction=instruction.instruction,
            input=input,
            output=output,
        )
    )
    return output


def process_instruction_code(
    llm, sandbox, shape, instruction, input, prev_data, store, run
):
    for retry_count in range(MAX_GENERATION_RETRIES + 1):
        code = generate_code(
            llm=llm,
            shape=shape,
            instruction=instruction.instruction,
            data=input,
            prev_data=prev_data,
            regenerate=shape.regenerate,
            store=store,
        )
        try:
            # Data is modified inplace
            output = execute_code(
                sandbox=sandbox,
                code=code,
                data=input,
            )
            # Convert to dict if output is a string
            output = json.loads(output) if isinstance(output, str) else output
            run.log(
                LogItemCode(
                    mode="code",
                    instruction=instruction.instruction,
                    input=input,
                    output=output,
                    code=code,
                )
            )
            return output
        except ErrorCodeExecution as e:
            if retry_count >= MAX_GENERATION_RETRIES:
                logger.error(
                    "Max retries reached. Instruction: %s", instruction.instruction
                )
                return None
            logger.error(
                "Execution error: %s. Retrying... (Attempt %s of %s)",
                e,
                retry_count + 1,
                MAX_GENERATION_RETRIES,
            )
            shape.regenerate = True
    return None


def process_line(llm, sandbox, line, shape, store, run):
    prev_data = None
    input = line

    for instruction in shape.instructions:
        mode = instruction.mode or llm.detect_instruction_mode(
            instruction=instruction.instruction,
            data=input,
        )
        instruction.mode = mode

        logging.info(
            f"Processing instruction. Input: {input}, Instruction: {instruction.instruction}, Mode: {mode.value}"
        )

        output = None
        if mode == Modes.LLM:
            output = process_instruction_llm(llm, instruction, input, prev_data, run)
        else:
            output = process_instruction_code(
                llm, sandbox, shape, instruction, input, prev_data, store, run
            )

        shape.regenerate = False

        if output is None:
            logging.error("Failed to process instruction: %s", instruction.instruction)
            continue

        logging.info(f"Instruction output: {output}")

        prev_data = output
        input = output

    return output
