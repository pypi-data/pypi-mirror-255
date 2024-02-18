from pathlib import Path

import can
import typer
from rich.console import Console
from typing_extensions import Annotated

err_console = Console(stderr=True)
console = Console()

help = """
CAN related tools
"""

app = typer.Typer(help=help)


@app.command("convert")
def convert(in_file: Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="File to convert from (.blf .asc .log)"
    )],
            out_file: Annotated[
                Path,
                typer.Argument(
                    exists=False,
                    file_okay=True,
                    dir_okay=False,
                    writable=True,
                    readable=True,
                    resolve_path=True,
                    help="File to convert to (.blf .asc .log)"
                )]):
    """
    Converts between ASC, BLF and LOG files. Make sure file suffixes match.

    remotive tools can convert \[my_file.blf|.log|.asc] \[my_file.blf|.log|.asc]
    """

    with can.LogReader(in_file, relative_timestamp=False) as reader:

        try:
            with can.Logger(out_file) as writer:
                for msg in reader:
                    writer.on_message_received(msg)
        except Exception as e:
            err_console.print(f':boom: [bold red]Failed to convert file[/bold red]: {e}')


@app.command("validate")
def validate(in_file: Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="File to validate (.blf .asc .log)")],
             print: bool = typer.Option(False, help="Print file contents to terminal")):
    """
    Validates that the input file is an ASC, BLF and LOG file

    remotive tools can validate \[my_file.blf|.log|.asc]
    """
    with can.LogReader(in_file, relative_timestamp=False) as reader:
        try:
            with can.Printer() as writer:
                for msg in reader:
                    if print:
                        writer.on_message_received(msg)
            console.print(f"Successfully verified {in_file}")
        except Exception as e:
            err_console.print(f':boom: [bold red]Failed to convert file[/bold red]: {e}')
