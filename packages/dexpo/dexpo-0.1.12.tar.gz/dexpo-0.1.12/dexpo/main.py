from typing import Annotated

import typer

from .callbacks import project_callback, version_callback
from .info import get_pypi_info
from .outputs import write_project_info


app = typer.Typer()


@app.command()
def main(
    project: Annotated[
        str,
        typer.Argument(
            callback=project_callback,
            show_default=False,
            help="Project to search for (i.e. pandas).",
        ),
    ],
    vuln: Annotated[
        bool,
        typer.Option(
            help="Disable with `--no-vuln` to skip fetching vulnerability info.",
        ),
    ] = True,
    report: Annotated[
        bool,
        typer.Option(
            help="Enable to write console output to svg files in cwd.",
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            callback=version_callback,
            is_eager=True,
            help="Print the installed dexpo version and exit.",
        ),
    ] = None,
):
    """
    Print basic reports (and optionally write to SVG files with `--report` flag) about a PyPI PROJECT's reputation and vulnerabilites.
    """
    project_info = get_pypi_info(project)
    write_project_info(project_info, vuln, report)
    raise typer.Exit()
