from os import getenv
from datetime import datetime
from typing import Annotated

import typer
from rich import print

from .callbacks import project_callback, version_callback
from .info import get_project_info, get_vuln_info
from .outputs import write_project_info, write_vuln_info


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
    api_key: Annotated[
        str,
        typer.Option(
            show_default=False,
            help="libraries.io API key. Key must be provided or stored in env var called 'LIBRARIESIO_API_KEY'. Create an account to get your key. https://libraries.io",
        ),
    ] = getenv("LIBRARIESIO_API_KEY"),
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
    Print basic reports (and optionally write to SVG files with `--report` flag) about a pypi PROJECT's reputation and vulnerabilites.
    """
    project_info = get_project_info(project, api_key)
    if project_info["versions"][-1]["number"] != project_info["latest_release_number"]:
        if datetime.strptime(
            project_info["latest_release_published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ) >= datetime.strptime(
            project_info["versions"][-1]["published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ):
            project_version = project_info["latest_release_number"]
            project_release_time = datetime.strptime(
                project_info["latest_release_published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        else:
            project_version = project_info["versions"][-1]["number"]
            project_release_time = datetime.strptime(
                project_info["versions"][-1]["published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
    else:
        project_version = project_info["latest_release_number"]
        project_release_time = datetime.strptime(
            project_info["latest_release_published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
    write_project_info(project_info, project_version, project_release_time, report)
    if vuln:
        vuln_info = get_vuln_info(project, project_version)
        if vuln_info:
            if vuln_info["info"]["yanked"]:
                print(
                    f"[orange3]Latest version {project_version} was yanked because '{vuln_info['info']['yanked_reason']}'.[/orange3]"
                )
                print(
                    f"[orange3]Reattempting with latest stable version {project_info['latest_stable_release_number']}.[/orange3]"
                )
                yanked_vuln_info = get_vuln_info(
                    project, project_info["latest_stable_release_number"]
                )
                if yanked_vuln_info:
                    if yanked_vuln_info["info"]["yanked"]:
                        print(
                            f"[bold red]The latest stable version {project_info['latest_stable_release_number']} was also yanked because '{yanked_vuln_info['info']['yanked_reason']}'.[/bold red]"
                        )
                        print(
                            f"[bold red]Please investigate the latest releases of the {project} package for clarity.[/bold red]"
                        )
                        return
                    write_vuln_info(yanked_vuln_info, report)
                    return
                print(
                    f"[bold red]No vulnerability info was found for the latest stable version {project_info['latest_stable_release_number']}.[/bold red]"
                )
                print(
                    f"[bold red]Please investigate the latest releases of the {project} package for clarity.[/bold red]"
                )
                return
            write_vuln_info(vuln_info, report)
            return
        else:
            print(
                f"[orange3]No vulnerability info was found for the latest version {project_version}.[/orange3]"
            )
            print(
                f"[orange3]Reattempting with latest stable version {project_info['latest_stable_release_number']}.[/orange3]"
            )
            missing_vuln_info = get_vuln_info(
                project, project_info["latest_stable_release_number"]
            )
            if missing_vuln_info:
                if missing_vuln_info["info"]["yanked"]:
                    print(
                        f"[bold red]The latest stable version {project_info['latest_stable_release_number']} was yanked.[/bold red]"
                    )
                    print(
                        f"[bold red]Please investigate the latest releases of the {project} package for clarity.[/bold red]"
                    )
                    return
                write_vuln_info(missing_vuln_info, report)
                return
            else:
                print(
                    f"[bold red]No vulnerability info was found for the latest stable version {project_info['latest_stable_release_number']} either.[/bold red]"
                )
                print(
                    f"[bold red]Please investigate the latest releases of the {project} package for clarity.[/bold red]"
                )
                return
