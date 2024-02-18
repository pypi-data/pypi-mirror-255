import json
from rich.progress import Progress, SpinnerColumn, TextColumn
from . import rest_helper as rest
import typer

app = typer.Typer()


@app.command(name="import", help="Import sample recording into project")
def do_import(recording_session: str = typer.Argument(..., help="Recording session id"),
              project: str = typer.Option(..., help="Project to import sample recording into", envvar='REMOTIVE_CLOUD_PROJECT')):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        v = progress.add_task(description=f"Importing recording, may take a few seconds...", total=100)
        rest.handle_post(url=f"/api/samples/files/recording/{recording_session}/copy",
                     body=json.dumps({'projectUid': project}))
        progress.update(v, advance=100.0)


@app.command("list")
def list():
    """
    List available sample recordings
    """

    rest.handle_get(f"/api/samples/files/recording")
