from pathlib import Path

import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command(help="ProtoPie Connect bridge-app to connect signals with RemotiveBroker")
def protopie(
        config: Annotated[
            Path,
            typer.Option(
                exists=True,
                file_okay=True,
                dir_okay=False,
                writable=False,
                readable=True,
                resolve_path=True,
                help="Configuration file with signal subscriptions and mapping if needed"
            ),
        ],
        broker_url: str = typer.Option(..., help="Broker URL", envvar='REMOTIVE_BROKER_URL'),
        api_key: str = typer.Option(None, help="Cloud Broker API-KEY or access token",
                                    envvar='REMOTIVE_BROKER_API_KEY'),
        pp_connect_host: str = typer.Option("http://localhost:9981", help=""),

):
    from .protopie import protopie
    protopie.do_connect(pp_connect_host, broker_url, api_key, config)
