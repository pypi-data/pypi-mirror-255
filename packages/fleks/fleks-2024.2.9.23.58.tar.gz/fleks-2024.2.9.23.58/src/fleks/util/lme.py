""" fleks.util.lme
"""

import logging

from rich.style import Style
from rich.theme import Theme
from rich.console import Console
from rich.logging import RichHandler
from rich.default_styles import DEFAULT_STYLES

from fleks import constants

THEME = Theme(
    {
        **DEFAULT_STYLES,
        **{
            "logging.keyword": Style(bold=True, color="yellow"),
            # "logging.level.notset": Style(dim=True),
            "logging.level.debug": Style(color="green"),
            "logging.level.info": Style(
                dim=True,
                # color="blue",
            ),
            "logging.level.warning": Style(color="yellow"),
            "logging.level.error": Style(color="red", dim=True, bold=True),
            "logging.level.critical": Style(
                color="red",
                bold=True,
                # reverse=True
            ),
            "log.level": Style.null(),
            "log.time": Style(color="cyan", dim=True),
            "log.message": Style.null(),
            "log.path": Style(dim=True),
        },
    }
)
CONSOLE = Console(theme=THEME, stderr=True)


def set_global_level(level):
    """
    https://stackoverflow.com/questions/19617355/dynamically-changing-log-level-without-restarting-the-application
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
        # if isinstance(handler, type(logging.StreamHandler())):
        #     handler.setLevel(logging.DEBUG)
        #     logger.debug('Debug logging enabled')


def get_logger(name, console=CONSOLE):
    """utility function for returning a logger
    with standard formatting patterns, etc
    """
    log_handler = RichHandler(
        rich_tracebacks=True,
        console=console,
        show_time=False,
    )

    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[log_handler],
    )
    FormatterClass = logging.Formatter
    formatter = FormatterClass(
        fmt=" ".join(["%(name)s", "%(message)s"]),
        # datefmt="%Y-%m-%d %H:%M:%S",
        datefmt="",
    )
    log_handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    # FIXME: get this from some kind of global config
    # logger.setLevel("DEBUG")
    logger.setLevel(constants.LOG_LEVEL.upper())

    return logger
