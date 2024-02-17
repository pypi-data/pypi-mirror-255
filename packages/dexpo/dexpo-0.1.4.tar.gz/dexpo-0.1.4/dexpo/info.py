import requests
import typer
from rich import print


def get_project_info(project: str, api_key: str) -> dict:
    with requests.Session() as s:
        r = s.get(f"https://libraries.io/api/pypi/{project}?api_key={api_key}")
    match r.status_code:
        case 200:
            info: dict = r.json()
            return info
        case 403:
            print(
                f"[bold red]403 Forbidden Error:[/bold red] The provided --api-key [italic purple]{api_key}[/italic purple] was invalid. If an --api-key argument is not provided, it must be stored in an environment variable called [italic purple]LIBRARIESIO_API_KEY[/italic purple]"
            )
            raise typer.Exit()
        case 404:
            print(
                f"[bold red]404 Not Found Error:[/bold red] Could not find a project called [italic purple]{project}[/italic purple] on the PyPI platform."
            )
            raise typer.Exit()
        case _:
            print(
                "[bold red]Something went wrong:[/bold red] An unexpected error occurred while fetching the project info from the libraries.io API. See below for details.\n"
            )
            print(f"[bold orange]HTTP Status Code:[/bold orange] {r.status_code}.")
            print(f"[bold orange]HTTP Response Body:[/bold orange] {r.text}.")
            raise typer.Exit()


def get_vuln_info(project: str, version: str) -> dict | None:
    with requests.Session() as s:
        r = s.get(f"https://pypi.org/pypi/{project}/{version}/json")
    match r.status_code:
        case 200:
            info: dict = r.json()
            return info
        case 404:
            return None
        case _:
            print(
                "[bold red]Something went wrong:[/bold red] An unexpected error occurred while fetching the vulnerability info from the pypi API. See below for details.\n"
            )
            print(f"[bold orange]HTTP Status Code:[/bold orange] {r.status_code}.")
            print(f"[bold orange]HTTP Response Body:[/bold orange] {r.text}.")
            print(f"Skipping vulnerability report for version {version}...")
            return None
