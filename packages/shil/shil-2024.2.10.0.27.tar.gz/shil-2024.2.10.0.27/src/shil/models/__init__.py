""" shil.models
"""

import os
import json
import typing
import textwrap
import subprocess

import pydantic
from fleks.util import lme

from shil import console
from shil.parser import shfmt

from .base import BaseModel

LOGGER = lme.get_logger(__name__)

Field = pydantic.Field


class Invocation(BaseModel):
    command: typing.Optional[str] = Field(
        help="Command to run",
        required=True,
    )
    stdin: typing.Optional[str] = Field(default=None, help="stdin to send to command")
    strict: bool = Field(
        default=False,
        help="Fail if command fails",
    )
    shell: typing.Optional[bool] = Field(
        help="Fail if command fails",
    )
    interactive: bool = Field(
        default=False,
        help="Interactive mode",
    )
    large_output: bool = Field(
        default=False, help="Flag for indicating that output is huge"
    )
    command_logger: typing.Optional[typing.Any] = Field(
        default=None,
        help="",
    )
    output_logger: typing.Optional[typing.Any] = Field(
        default=None,
        help="",
    )
    output_indent: int = Field(
        default=0,
        help="",
    )
    environment: dict = Field(
        default={},
        help="",
    )
    # log_stdin: bool = Field(default=True)
    system: bool = Field(
        help='Execute command in "system" mode',
        default=False,
    )
    load_json: bool = Field(
        help="Load JSON from output",
        default=False,
    )

    # @property
    # def system(self):
    #     """ """
    #     tmp = self.__dict__.get("system", False)
    #     if tmp:
    #         if self.stdin or self.interactive:
    #             err = f"{self} `system` cannot be used with `stdin`/`interactive`"
    #             LOGGER.critical(err)
    #             raise ValueError(err)

    def __rich_console__(self, _console, options):  # noqa
        """
        https://rich.readthedocs.io/en/stable/protocol.html
        """
        fmt = shfmt(self.command)
        extras = [
            f"[yellow]{attr}=1" if getattr(self, attr, None) else ""
            for attr in "system stdin interactive strict".split()
        ]
        extras = " ".join(extras)
        yield self.command

        indicator = "⌛ "
        yield console.Panel(
            f"[bold gold3]$ [dim italic pale_green3]{fmt}",
            title=(indicator + f"{self.__class__.__name__} {extras}"),
            title_align="left",
            style=console.Style(bgcolor="grey19"),
            subtitle=console.Text("not executed yet", style="yellow"),
        )
        # assert not self.stdin and not self.interactive

    def __call__(self):
        """ """
        if self.command_logger:
            tmp = [
                f"{attr}={getattr(self,attr)}" if getattr(self, attr, None) else ""
                for attr in "system strict".split()
            ]
            tmp = " ".join(tmp).strip() if tmp else ""
            tmp = f"({tmp})" if tmp else ""
            msg = f"Running command: {tmp}\n  {self.command}\n"
            self.command_logger(msg)
        result = InvocationResult(**self.dict())

        if self.system:
            # FIXME: record `pid` and support `environment`

            # # proc = subprocess.call(
            # proc = subprocess.run(
            #     self.command,
            #     shell=True,
            #     # capture_output=True,
            # )
            # proc = subprocess.check_output(
            #     self.command,
            #     shell=True,)
            # result.update(
            #     stderr=proc.stderr.decode("utf-8"),
            #     stdout=proc.stdout.decode("utf-8"),
            # )
            error = os.system(self.command)

            # import sys
            # proc = subprocess.Popen(
            #     self.command,
            #     # stdout=sys.stdout,
            #     stdout=subprocess.PIPE
            #     )
            # stdout=""
            # for c in iter(lambda: proc.stdout.read(1), b""):
            #     sys.stdout.buffer.write(c)
            #     stdout+=c
            # error = proc.returncode > 0
            result.update(
                failed=bool(error),
                failure=bool(error),
                success=not bool(error),
                succeeded=not bool(error),
                # stdout=proc.stdout.decode("utf-8"),
                stdout="<os.system>",
                stdin="<os.system>",
            )
            self.output_logger and self.output_logger(result.stdout)
            if self.strict and error:
                raise SystemExit(error)
            return result

        exec_kwargs = dict(
            shell=True,
            env={**{k: v for k, v in os.environ.items()}, **self.environment},
        )
        if self.stdin:
            self.command_logger and self.command_logger(
                f"Command will receive pipe:\n{self.stdin}"
            )
            exec_kwargs.update(
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            LOGGER.critical([self.command, exec_kwargs])
            tmp = subprocess.run(
                self.command.split(),
                shell=self.shell,
                input=self.stdin.encode("utf-8"),
                capture_output=True,
            )
            result.update(
                pid=getattr(tmp, "pid", -1),
                stdout=tmp.stdout.decode("utf-8"),
                stderr=tmp.stderr,
                return_code=tmp.returncode,
                failed=tmp.returncode != 0,
            )
            result.update(
                failure=result.failed,
                succeeded=not result.failure,
                success=not result.failure,
            )
            return result
        else:
            if not self.interactive:
                exec_kwargs.update(
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            exec_cmd = subprocess.Popen(self.command, **exec_kwargs)
            exec_cmd.wait()
        if exec_cmd.stdout:
            result.update(
                stdout=(
                    "<LargeOutput>"
                    if self.large_output
                    else exec_cmd.stdout.read().decode("utf-8")
                )
            )
            exec_cmd.stdout.close()
        else:
            exec_cmd.stdout = "<Interactive>"
            result.update(stdout="<Interactive>")
        if exec_cmd.stderr:
            result.update(stderr=exec_cmd.stderr.read().decode("utf-8"))
            exec_cmd.stderr.close()
        result.pid = exec_cmd.pid
        result.failed = exec_cmd.returncode > 0
        result.succeeded = not result.failed
        result.success = result.succeeded
        result.failure = result.failed
        result.data = None
        if self.load_json:
            if result.failed:
                err = f"Command @ {self.command} did not succeed; cannot return JSON from failure!"
                LOGGER.critical(err)
                LOGGER.critical(result.stderr)
                raise RuntimeError(err)
            try:
                result.data = json.loads(result.stdout)
            except (json.decoder.JSONDecodeError,) as exc:
                result.data = dict(error=str(exc))

        if self.strict and not result.succeeded:
            LOGGER.critical(f"Invocation failed and strict={self.strict}")
            LOGGER.critical(f"\n{result.stdout}")
            LOGGER.critical(f"\n{result.stderr}")
            raise RuntimeError()
        if self.output_logger:
            if self.output_indent:
                result = textwrap.indent(result.stdout, " " * self.output_indent)
            msg = f"Command result:\n{result}"
            self.output_logger(msg)
        return result


class InvocationResult(Invocation):
    data: typing.Optional[typing.Dict] = Field(
        default=None, help="Data loaded from JSON on stdout"
    )
    failed: bool = Field(default=None, help="")
    failure: bool = Field(default=None, help="")
    succeeded: bool = Field(default=None, help="")
    success: bool = Field(default=None, help="")
    stdout: str = Field(default=None, help="")
    stderr: str = Field(default=None, help="")
    return_code: int = Field(default=-1, help="")
    pid: int = Field(default=-1, help="")

    def __rich_console__(self, _console, options):  # noqa
        """
        https://rich.readthedocs.io/en/stable/protocol.html
        """

        def status_string():
            if self.succeeded is None:
                return "??"
            else:
                return "[cyan] [green]succeeded" if self.succeeded else "[red]failed"

        fmt = shfmt(self.command)
        output_style = "[bold pale_green3]" if self.succeeded else "[red3]"
        indicator = "🟢 " if self.succeeded else "🟡 "
        yield console.Panel(
            f"[bold gold3]$ [dim]{fmt.strip()}  [red]→ \n{output_style} [dim italic pale_green3]{self.stdout}",
            title=(
                indicator
                + f"{self.__class__.__name__} from pid {self.pid} {status_string()}"
            ),
            style=console.Style(bgcolor="grey19"),
            title_align="left",
            subtitle=(
                console.Text("✔", style="green")
                if self.success
                else console.Text("❌", style="red")
            ),
        )
