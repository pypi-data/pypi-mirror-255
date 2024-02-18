""" shil.__main__
"""

import json as modjson
from pathlib import Path

from fleks import app, cli
from fleks.util import lme

from shil import fmt, invoke

LOGGER = lme.get_logger(__name__)
DEFAULT_INPUT_FILE = "/dev/stdin"

rich_flag = cli.click.flag("--rich", help="use rich output")
json_flag = cli.click.flag("--json", help="use JSON output")


@cli.click.group(name=Path(__file__).parents[0].name)
def entry():
    """
    CLI tool for `shil` library
    """


def report(output, json: bool = False, rich: bool = False) -> None:
    if rich:
        should_rich = hasattr(output, "__rich__") or hasattr(output, "__rich_console__")
        lme.CONSOLE.print(
            output
            if should_rich
            else app.Syntax(
                f"{output}",
                "bash",
                word_wrap=True,
            )
        )
    else:
        if hasattr(output, "json"):
            print(
                modjson.dumps(modjson.loads(output.json(exclude_none=True)), indent=2)
            )
        elif json:
            print(modjson.dumps(output, indent=2))
        else:
            print(f"{output}")


@rich_flag
@json_flag
@cli.click.argument("cmd")
@entry.command(name="invoke")
def _invoke(rich: bool = False, json: bool = False, cmd: str = "echo") -> None:
    """
    Invocation tool for (line-oriented) bash
    """
    result = invoke(
        command=cmd,
    )
    return report(
        result,
        rich=rich,
        json=json,
    )


@entry.command(name="fmt")
@json_flag
@rich_flag
@cli.click.argument("filename", default=DEFAULT_INPUT_FILE)
def _fmt(
    filename: str = DEFAULT_INPUT_FILE,
    json: bool = False,
    rich: bool = False,
) -> None:
    """
    Pretty-printer for (line-oriented) bash
    """
    if filename == "-":
        filename = DEFAULT_INPUT_FILE
    try:
        with open(filename) as fhandle:
            text = fhandle.read()
    except FileNotFoundError:
        LOGGER.warning(f"input @ {filename} is not a file; parsing as string")
        text = filename
    result = fmt(text)
    return report(result, rich=rich, json=json)


if __name__ == "__main__":
    entry()
