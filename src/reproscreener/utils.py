import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console(
    quiet=False,
)


FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING",  # "NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

log = logging.getLogger("rich")
