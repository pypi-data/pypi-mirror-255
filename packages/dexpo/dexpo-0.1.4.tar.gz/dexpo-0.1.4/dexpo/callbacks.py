import typer

from .__version__ import __version__ as dexpo_version


def version_callback(value: bool):
    if value:
        print(f"dexpo {dexpo_version}")
        raise typer.Exit()


def project_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if ctx.resilient_parsing:
        return
    return value.lower()
