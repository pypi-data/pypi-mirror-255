from datetime import datetime, date
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.terminal_theme import MONOKAI


def write_project_info(
    project_info: dict, latest_release: str, latest_release_time: str, report: bool
) -> None:
    out = f"""
:speech_balloon: Description: {project_info['description']}
:computer: Language: {project_info['language']}
:house: Homepage: {project_info['homepage']}
:100: Source Rank: {project_info['rank']}
:star: Stars: {project_info['stars']}
:link: Repository URL: {project_info['repository_url']}
:copyright::copyright: Respositoy License: {project_info['repository_license']}
:vs: Latest Release Version: {latest_release}
:clock3: Latest Release Time: {latest_release_time}
:vs: Latest Stable Release Version: {project_info['latest_stable_release_number']}
:clock3: Latest Stable Release Time: {datetime.strptime(project_info['latest_stable_release_published_at'], '%Y-%m-%dT%H:%M:%S.%fZ')}
:chart_with_upwards_trend: Dependents: {project_info['dependent_repos_count']}
:busts_in_silhouette: Contributions: {project_info['contributions_count']}
"""

    console = Console(record=True)
    console.print(
        Panel.fit(out, border_style="green", title=project_info["name"]),
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


def write_vuln_info(vuln_info: dict, report: bool) -> None:
    console = Console(record=True)
    vulns = [v for v in vuln_info["vulnerabilities"] if v["withdrawn"] is None]
    num_vulns = len(vulns)
    console.print(f"Number of unwithdrawn vulnerabilites: {num_vulns}")
    if num_vulns > 0:
        table = Table(
            title=f"{vuln_info['info']['name']} {vuln_info['info']['version']} Vulnerabilities",
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
                    f"{date.today().strftime('%Y-%m-%d')} dexpo {vuln_info['name']} vuln report.svg"
                )
            )
            console.save_svg(report_path, theme=MONOKAI)
            console.print("Vulnerability report file was written: ", report_path)
