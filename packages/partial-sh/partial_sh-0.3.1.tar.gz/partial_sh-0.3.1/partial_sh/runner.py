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


class Runner:
    llm = None
    sandbox = None
    store = None
    quiet = False

    def __init__(self, llm, sandbox, store, quiet=False):
        self.llm = llm
        self.sandbox = sandbox
        self.store = store
        self.quiet = quiet

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
                print_data_output(output)

        # Handle if the run fails, in the case the output data is None
        if output is None:
            run.end(status=RunStatus.FAILED)
        else:
            run.end(status=RunStatus.SUCCESS)

        logger.info("Data processed")
        return run
