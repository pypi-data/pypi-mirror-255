""" fleks.cli.options:

    Common options for CLI
"""

import os

from fleks.cli import click
from fleks.util import lme

LOGGER = lme.get_logger(__name__)

strict = click.flag(
    "--strict",
    help=("if true, runs in strict mode"),
)
script = click.option("--script", default=None, help=("script to use"))
file = click.option("--file", "-f", default="", help=("file to read as input"))
stdout = click.flag("--stdout", help=("whether to write to stdout."))
name = click.option("--name", default="", help=("name to use"))
output = click.option(
    "--output",
    "-o",
    help="when set, output will be written to this file",
    default="/dev/stdout",
)
output = click.option(
    "--output", "-o", default="", help=("output file to write.  (optional)")
)
output_file = click.option(
    "--output",
    "-o",
    metavar="output_file",
    default="",
    help=("output file to write.  (optional)"),
)
output_dir = click.option(
    "--output-dir", default="docs/cli", help=("output directory (optional)")
)
plan = click.flag(
    "--plan",
    "-p",
    "should_plan",
    help="plan only; no action",
)
ignore_missing = click.flag(
    "--ignore-missing",
    help="ignore missing docstrings (only updates empty or out-dated ones)",
)
ignore_private = click.flag(
    "--ignore-private",
    help='ignore names that start with "_")',
)

org_name = click.option(
    "--org-name", "-o", default="", help="defaults to {github.org_name}"
)

inplace = in_place = click.flag(
    "--in-place",
    help=("if true, writes to {file}.{ext} (dropping any other extensions)"),
)

should_print = click.flag(
    "--print",
    "should_print",
    help="if set, displays result on stdout even when `--output <file>` is passed",
)

includes = click.option(
    "--include",
    "includes",
    default=[],
    help=("path to use for template-root / includes"),
    multiple=True,
    # type=list,
    # cls=click.OptionEatAll,
)

ctx = click.option("--ctx", default="", help=("context to use"))
header = click.option(
    "--header", default="", help=("header to prepend output with. (optional)")
)
stdout = click.flag("--stdout", help=("whether to write to stdout."))
format = format_json = click.option(
    "--format", "-m", default="json", help=("output format to write")
)
format_markdown = click.option(
    "--format", "-m", default="markdown", help=("output format to write")
)
format = click.option("--format", "-m", default="json", help=("output format to write"))
package = click.option("--package", "-p", default=os.environ.get("PY_PKG", ""))
file_setupcfg = click.option(
    "--file", "-f", default="setup.cfg", help=("file to grab entrypoints from")
)
module = click.option(
    "--module",
    "-m",
    default="",
    help=("module to grab click-cli from. " "(must be used with `name`)"),
)
