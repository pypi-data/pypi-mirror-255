# import typer
# from typing import Optional
# from typing_extensions import Annotated
# from rich import print

# def main(name: Annotated[Optional[str], typer.Argument("Name of the person")] = None):
#     if name:
#         print("Hello", name)
#     else:
#         print("Hello World")

# if __name__ == "__main__":
#     typer.run(main)

from typing import Optional

import typer
from typing_extensions import Annotated


def main(name: Annotated[Optional[str], typer.Argument()] = None):
    if name is None:
        print("Hello World!")
    else:
        print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
