from typing import Any, Optional, IO, Iterator
from argh import ArghParser
from argh.dispatching import dispatch as _dispatch
import io

from scale_egp.cli.formatter import AVAILABLE_FORMATTERS, Formatter
from importlib.metadata import version


# based on argh.dispatching._process_command_output
def get_patched_process_command_output(formatter: Formatter):
    def patched_process_command_output(
        lines: Iterator[Any], output_file: Optional[IO], raw_output: bool
    ) -> Optional[str]:
        out_io: IO

        if output_file is None:
            # user wants a string; we create an internal temporary file-like object
            # and will return its contents as a string
            out_io = io.StringIO()
        else:
            # normally this is stdout; can be any file
            out_io = output_file

        formatter.format(out_io, lines, raw_output)

        if output_file is None:
            # user wanted a string; return contents of our temporary file-like obj
            out_io.seek(0)
            return out_io.read()

        return None

    return patched_process_command_output


def get_parser() -> ArghParser:
    return ArghParser(
        description=f"scale-egp - CLI for Scale EGP (version {version('scale-egp')})\nFor more information on EGP, please visit: https://scale-egp.readme.io/",
    )


def dispatch(parser: ArghParser, args: Any) -> Optional[str]:
    from mock import patch

    formatter = AVAILABLE_FORMATTERS[args.format](args)

    with patch(
        "argh.dispatching._process_command_output",
        side_effect=get_patched_process_command_output(formatter),
    ):
        return _dispatch(parser=parser, add_help_command=True)
