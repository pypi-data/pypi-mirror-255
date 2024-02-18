import requests
from datetime import datetime, date
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.terminal_theme import MONOKAI


def write_project_info(project_info: dict, vuln: bool, report: bool) -> None:
    project: str = project_info["info"]["name"]
    console = Console(record=True)
    github_present = True
    project_urls: dict = project_info["info"]["project_urls"]
    if project_urls is None:
        console.print(
            "[bold red]Could not find any project URLs associated with this package. Are you sure you entered the correct package name?[/bold red]"
        )
        raise typer.Exit()
    if "Repository" in list(project_urls):
        repo_url: str = project_urls["Repository"]
    else:
        repo_url = None
        for u in list(project_urls):
            if "Source" in u:
                repo_url: str = project_urls[u]
                break
            continue
        if repo_url is None:
            temp_url: str = project_info["info"]["home_page"]
            if "github.com/" in temp_url.lower().strip() and (
                project.lower().strip() in temp_url.lower().strip()
            ):
                repo_url: str = (
                    temp_url[: temp_url.lower().strip().rindex(project.lower().strip())]
                    + project
                )
            else:
                for u in list(project_urls):
                    temp_url: str = project_urls[u]
                    if "github.com/" in temp_url and project in temp_url:
                        repo_url: str = (
                            temp_url[
                                : temp_url.lower()
                                .strip()
                                .rindex(project.lower().strip())
                            ]
                            + project
                        )
                        break
                    continue
                if repo_url is None:
                    console.print(
                        "[orange3]Could not find github repository url in PyPI data. Proceeding with only PyPI data.[/orange3]"
                    )
                    github_present = False
    if github_present:
        repo_url = repo_url.removesuffix("/")
        repo_url = repo_url.removesuffix(".git")
        with requests.Session() as s:
            github_response = s.get(
                f'https://api.github.com/repos/{repo_url.split(".com/")[-1]}'
            )
        github_data = github_response.json()
        if project_info["info"]["yanked"]:
            for r in list(project_info["releases"]).reverse():
                if not project_info["releases"][r]["yanked"]:
                    version = r
                    break
                continue
            console.print(
                f"[orange3]The latest release was yanked due to: {project_info['info']['yanked_reason']}... pulling data for latest available release {version}[/orange3]"
            )
            version = list(project_info["releases"])[-1]
        else:
            version = project_info["info"]["version"]

        with requests.Session() as s:
            pypi_version_response = s.get(
                f"https://pypi.org/pypi/{project}/{version}/json"
            )
        pypi_version_data = pypi_version_response.json()

        if "license" not in list(github_data) or github_data["license"] is None:
            license_name = project_info["info"]["license"]
        else:
            license_name = github_data["license"]["name"]

        if "homepage" not in list(github_data):
            homepage = project_info["info"]["home_page"]
        else:
            homepage = github_data["homepage"]

        if project_info["info"]["author"] is None:
            author = project_info["info"]["author_email"]
        else:
            author = project_info["info"]["author"]

        console.print(
            Panel.fit(
                f"""
:book: Author: {author}
:email: Author Contact: {project_info["info"]["author_email"]}
:computer: Language: Python
:speech_balloon: Description: {project_info["info"]['summary']}
:house: Homepage: {homepage}
:star: GitHub Stars: {github_data['stargazers_count']}
:link: Repository URL: {repo_url}
:copyright::copyright: Respositoy License: {license_name}
:vs: Latest Stable Release Version: {version}
:clock3: Latest Stable Release Time: {datetime.strptime(pypi_version_data["urls"][-1]['upload_time'], '%Y-%m-%dT%H:%M:%S')}
""",
                border_style="green",
                title=project_info["info"]["name"],
            ),
            justify="center",
        )
    else:
        if project_info["info"]["yanked"]:
            for r in list(project_info["releases"]).reverse():
                if not project_info["releases"][r]["yanked"]:
                    version = r
                    break
                continue
            console.print(
                f"[orange3]The latest release was yanked due to: {project_info['info']['yanked_reason']}... pulling data for latest available release {version}[/orange3]"
            )
            version = list(project_info["releases"])[-1]
        else:
            version = project_info["info"]["version"]

        with requests.Session() as s:
            pypi_version_response = s.get(
                f"https://pypi.org/pypi/{project}/{version}/json"
            )
        pypi_version_data = pypi_version_response.json()
        license_name = project_info["info"]["license"]
        if project_info["info"]["author"] is None:
            author = project_info["info"]["author_email"]
        else:
            author = project_info["info"]["author"]
        console.print(
            Panel.fit(
                f"""
:book: Author: {author}
:email: Author Contact: {project_info["info"]["author_email"]}
:computer: Language: Python
:speech_balloon: Description: {project_info["info"]['summary']}
:house: Homepage: {project_info["info"]['home_page']}
:star: GitHub Stars: N/A
:link: Repository URL: {repo_url}
:copyright::copyright: Respositoy License: {license_name}
:vs: Latest Stable Release Version: {version}
:clock3: Latest Stable Release Time: {datetime.strptime(pypi_version_data["urls"][-1]['upload_time'], '%Y-%m-%dT%H:%M:%S')}
""",
                border_style="green",
                title=project_info["info"]["name"],
            ),
            justify="center",
        )
    if report:
        report_path = (
            Path()
            .absolute()
            .joinpath(
                f"{date.today().strftime('%Y-%m-%d')} dexpo {project_info['name']} project report.svg"
            )
        )
        console.save_svg(report_path, theme=MONOKAI)
        console.print("Project report file was written: ", report_path)
    if vuln:
        vulns = [
            v for v in pypi_version_data["vulnerabilities"] if v["withdrawn"] is None
        ]
    num_vulns = len(vulns)
    console.print(f"Number of unwithdrawn vulnerabilites: {num_vulns}")
    if num_vulns > 0:
        table = Table(
            title=f"{pypi_version_data['info']['name']} {pypi_version_data['info']['version']} Vulnerabilities",
            show_lines=True,
        )
        table.add_column("ID", style="cyan")
        table.add_column("Summary", style="orange3")
        table.add_column("Fixed In", style="purple")
        table.add_column("Details", style="red")
        table.add_column("Link", style="blue")
        for vuln in vulns:
            fixed_in = ", ".join(vuln["fixed_in"])
            table.add_row(
                f"[bold]{vuln['id']}[/bold]",
                vuln["summary"],
                fixed_in,
                vuln["details"],
                vuln["link"],
            )
        console.print(table)
        if report:
            report_path = (
                Path()
                .absolute()
                .joinpath(
                    f"{date.today().strftime('%Y-%m-%d')} dexpo {pypi_version_data['name']} vuln report.svg"
                )
            )
            console.save_svg(report_path, theme=MONOKAI)
            console.print("Vulnerability report file was written: ", report_path)
