from importlib.metadata import version
import typer
# from .tools.tools import app as tools_app
from rich import print
from trogon import Trogon
from typer.main import get_group

from .broker.brokers import app as broker_app
from .cloud.cloud_cli import app as cloud_app
from .connect.connect import app as connect_app

app = typer.Typer(rich_markup_mode="rich", help="""
Welcome to RemotiveLabs CLI - Simplify and automate tasks for cloud resources and brokers

For documentation - https://docs.remotivelabs.com
""")


def version_callback(value: bool):
    if value:
        my_version = version('remotivelabs-cli')
        typer.echo(my_version)
        raise typer.Exit()


def test_callback(value: int):
    if value:
        print(value)
        raise typer.Exit()
    # if value:
    #    typer.echo(f"Awesome CLI Version: 0.0.22a")
    #    raise typer.Exit()


@app.callback()
def main(
        version: bool = typer.Option(None, callback=version_callback, is_eager=False, help="Print current version"),
):
    # Do other global stuff, handle other global options here
    # print(f"version {version}")
    return


@app.command()
def tui(ctx: typer.Context):
    """
        Explore remotive-cli and generate commands with this textual user interface application
    """

    Trogon(get_group(app), click_context=ctx).run()


app.add_typer(broker_app, name="broker", help="Manage a single broker - local or cloud")
app.add_typer(cloud_app, name="cloud", help="Manage resources in RemotiveCloud", )
app.add_typer(connect_app, name="connect", help="Integrations with other systems")
# app.add_typer(tools_app, name="tools")
