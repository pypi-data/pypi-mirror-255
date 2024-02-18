import requests
import typer
from rich.console import Console


def get_pypi_info(project: str) -> dict:
    console = Console()
    with requests.Session() as s:
        r = s.get(f"https://pypi.org/pypi/{project}/json")
    match r.status_code:
        case 200:
            info: dict = r.json()
            return info
        case 403:
            console.print(
                f"[bold red]403 Forbidden Error:[/bold red] The PyPI api rejected your request. If you have been making a high number of requests, please come back later. Visit https://warehouse.pypa.io/api-reference/ for more info."
            )
            raise typer.Exit()
        case 404:
            console.print(
                f"[bold red]404 Not Found Error:[/bold red] Could not find a project called [italic purple]{project}[/italic purple] on the PyPI platform."
            )
            raise typer.Exit()
        case _:
            console.print(
                "[bold red]Something went wrong:[/bold red] An unexpected error occurred while fetching the project info from the libraries.io API. See below for details.\n"
            )
            console.print(
                f"[bold orange]HTTP Status Code:[/bold orange] {r.status_code}."
            )
            console.print(f"[bold orange]HTTP Response Body:[/bold orange] {r.text}.")
            raise typer.Exit()


def get_vuln_info(project: str, version: str) -> dict | None:
    console = Console()
    with requests.Session() as s:
        r = s.get(f"https://pypi.org/pypi/{project}/{version}/json")
    match r.status_code:
        case 200:
            info: dict = r.json()
            return info
        case 404:
            return None
        case _:
            console.print(
                "[bold red]Something went wrong:[/bold red] An unexpected error occurred while fetching the vulnerability info from the pypi API. See below for details.\n"
            )
            console.print(
                f"[bold orange]HTTP Status Code:[/bold orange] {r.status_code}."
            )
            console.print(f"[bold orange]HTTP Response Body:[/bold orange] {r.text}.")
            console.print(f"Skipping vulnerability report for version {version}...")
            return None
