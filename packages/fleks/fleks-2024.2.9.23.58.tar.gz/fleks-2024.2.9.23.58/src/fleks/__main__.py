""" fleks.__main__
"""

from pathlib import Path

from fleks import cli
from fleks.util import lme

LOGGER = lme.get_logger(__name__)
DEFAULT_INPUT_FILE = "/dev/stdin"


@cli.click.group(name=Path(__file__).parents[0].name)
def entry():
    """CLI tool for `fleks` library"""


if __name__ == "__main__":
    entry()
