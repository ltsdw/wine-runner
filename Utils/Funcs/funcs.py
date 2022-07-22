from typing import NoReturn
from sys import stderr


def die(msg: str) -> NoReturn:
    """
    Prints a message and exits.

    :msg: the message to be displayed.
    :return:
    """

    stderr.write(msg + "\n")
    stderr.flush()

    exit(-1)

