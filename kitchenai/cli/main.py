from django.conf import settings
from rich.console import Console

from kitchenai.notebooks.cli.notebooks import app as notebook_app
from kitchenai.core.cli.core import app
from .client.client import app as client_app
from kitchenai.bento.cli.bento import app as bento_app

console = Console()

app.add_typer(notebook_app, name="notebook")
app.add_typer(client_app, name="client")
app.add_typer(bento_app, name="bento")