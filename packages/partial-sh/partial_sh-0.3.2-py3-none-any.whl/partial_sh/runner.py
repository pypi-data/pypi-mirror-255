import json
import logging
import sys

from .process import process_line
from .run import RunStatus

logger = logging.getLogger(__name__)


def print_data_output(output: str | dict):
    if isinstance(output, dict):
        logger.info("Output is a dict")
        output = json.dumps(output)
    else:
        logger.info("Output is a string")

    print(output, file=sys.stdout, flush=True)


def print_info(info: str, *args, **kwargs):
    """
    Print info to stderr, to avoid interfering with the output.
    """
    print(info, *args, **kwargs, file=sys.stderr)


def write_to_file(output: str, file_path: str):
    with open(file_path, "a") as f:
        f.write(json.dumps(output))
        f.write("\n")


class Runner:
    llm = None
    sandbox = None
    store = None
    quiet = False
    output_file = None

    def __init__(self, llm, sandbox, store, quiet=False, output_file=None):
        self.llm = llm
        self.sandbox = sandbox
        self.store = store
        self.quiet = quiet
        self.output_file = output_file

    def terminate(self):
        if self.sandbox:
            self.sandbox.close()

    def process(
        self,
        lines,
        run,
    ):
        logger.info("Process data")
        run.start()
        shape = run.shape

        if self.output_file is not None:
            print_info(f"Writing to file: {self.output_file}")

        output = None
        for idx, line in enumerate(lines):
            logger.info("Processing line: %s", idx)
            for ri in range(shape.repeat):
                logger.info("Repeat Iteration: %s", ri)
                if self.quiet is False and sys.stdout.isatty() is False:
                    print_info(f"Processing line: {idx} Repeat Iteration: {ri}")
                output = process_line(
                    llm=self.llm,
                    sandbox=self.sandbox,
                    line=line,
                    shape=shape,
                    store=self.store,
                    run=run,
                )
                if self.output_file is None:
                    print_data_output(output)
                else:
                    # Write to file
                    write_to_file(output, self.output_file)

        # Handle if the run fails, in the case the output data is None
        if output is None:
            run.end(status=RunStatus.FAILED)
        else:
            run.end(status=RunStatus.SUCCESS)

        logger.info("Data processed")
        return run
