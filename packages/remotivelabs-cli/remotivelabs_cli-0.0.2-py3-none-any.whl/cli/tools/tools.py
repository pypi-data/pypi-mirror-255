import typer

from .can.can import app as can_app

help_text = """
CLI tools unrelated to cloud or broker
"""

app = typer.Typer(help=help_text)
app.add_typer(can_app, name="can", help="CAN tools")
