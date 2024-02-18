import json
import sys
from pathlib import Path


def parse_incremental(data):
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(data):
        try:
            obj, pos = decoder.raw_decode(data, pos)
            yield obj
        except json.JSONDecodeError:
            pos += 1


def read_input(file: Path = None):
    """
    Read data from stdin or from a file.
    """
    if file:
        with open(file, "r") as f:
            return parse_incremental(f.read())
    else:
        return parse_incremental(sys.stdin.read())
