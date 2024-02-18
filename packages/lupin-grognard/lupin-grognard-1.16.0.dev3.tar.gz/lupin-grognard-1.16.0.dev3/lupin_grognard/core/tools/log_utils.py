import logging
import sys


def die(msg: str) -> None:
    logging.error(msg)
    sys.exit(1)


def warn(msg: str) -> None:
    logging.warning(msg)


def info(msg: str) -> None:
    logging.info(msg)
