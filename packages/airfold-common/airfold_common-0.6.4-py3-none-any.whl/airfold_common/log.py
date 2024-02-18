import logging

from rich.console import Console
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="ERROR",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=Console(stderr=True))],
)

log: logging.Logger = logging.getLogger("rich")


def set_verbosity(verbosity: int) -> None:
    lvl = logging.WARNING
    if verbosity == 1:
        lvl = logging.INFO
    elif verbosity > 1:
        lvl = logging.DEBUG
    log.setLevel(lvl)
