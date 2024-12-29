import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from kitchenai_py.client import KitchenAIWrapper

app = typer.Typer()
console = Console()

# Initialize KitchenAIWrapper
kitchen_ai = KitchenAIWrapper(host="http://localhost:8001")

file_app = typer.Typer()
embed_app = typer.Typer()

@app.command("health")
def health_check():
    """Check the health of the API."""
    result = kitchen_ai.health_check()
    if "healthy" in result:
        console.print(f"[green]{result}[/green]")
    else:
        console.print(f"[red]{result}[/red]")

@app.command("query")
def run_query(
    label: str, 
    query: str, 
    metadata: Annotated[str, typer.Option(help="add metadata.")] = "",
    stream: Annotated[bool, typer.Option(help="enable streaming")] = False
):
    """Run a query using the Query Handler."""
    result = kitchen_ai.run_query(label, query, metadata, stream)
    if isinstance(result, tuple):
        message, data = result
        console.print(f"[green]{message}[/green]")
        console.print(data)
    else:
        console.print(f"[red]{result}[/red]")

@app.command("agent")
def run_agent(label: str, query: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Run an agent using the Agent Handler."""
    result = kitchen_ai.run_agent(label, query, metadata)
    if "successfully" in result:
        console.print(f"[green]{result}[/green]")
    else:
        console.print(f"[red]{result}[/red]")

@app.command("file")
def file():
    """File operations."""
    pass

@file_app.command("create")
def create_file(file_path: str, name: str, ingest_label: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Create a file."""
    result = kitchen_ai.create_file(file_path, name, ingest_label, metadata)
    if isinstance(result, tuple):
        message, response = result
        console.print(f"[green]{message} Response: {response}[/green]")
    else:
        console.print(f"[red]{result}[/red]")

@file_app.command("get")
def get_file(file_id: int):
    """Read a file by ID."""
    result = kitchen_ai.read_file(file_id)
    if isinstance(result, tuple):
        message, file_data = result
        console.print(f"[green]{message}[/green]")
        console.print(file_data)
    else:
        console.print(f"[red]{result}[/red]")

@file_app.command("delete")
def delete_file(file_id: int):
    """Delete a file by ID."""
    result = kitchen_ai.delete_file(file_id)
    if "successfully" in result:
        console.print(f"[green]{result}[/green]")
    else:
        console.print(f"[red]{result}[/red]")

@file_app.command("list")
def list_files():
    """List all files."""
    files = kitchen_ai.list_files()
    if isinstance(files, str):
        console.print(f"[yellow]{files}[/yellow]")
        return
        
    table = Table(title="Files")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Ingest Label", style="green")
    for file in files:
        table.add_row(str(file.id), file.name, file.ingest_label or "N/A")
    console.print(table)

app.add_typer(file_app, name="file")

@app.command("embed")
def embed():
    """Embed operations."""
    pass

@embed_app.command("list")
def get_all_embeds():
    """Get all embeds."""
    embeds = kitchen_ai.get_all_embeds()
    if isinstance(embeds, str):
        console.print(f"[yellow]{embeds}[/yellow]")
        return
        
    table = Table(title="Embeds")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Text", style="magenta")
    for embed in embeds:
        table.add_row(str(embed.id), embed.text)
    console.print(table)

@embed_app.command("create")
def create_embed(text: str, ingest_label: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Create an embed."""
    result = kitchen_ai.create_embed(text, ingest_label, metadata)
    if isinstance(result, tuple):
        message, response = result
        console.print(f"[green]{message} Response: {response}[/green]")
    else:
        console.print(f"[red]{result}[/red]")

@embed_app.command("delete")
def delete_embed(embed_id: int):
    """Delete an embed by ID."""
    result = kitchen_ai.delete_embed(embed_id)
    if "successfully" in result:
        console.print(f"[green]{result}[/green]")
    else:
        console.print(f"[red]{result}[/red]")

app.add_typer(embed_app, name="embed")

@app.command("labels")
def list_labels():
    """List all custom kitchenai labels."""
    labels = kitchen_ai.list_labels()
    if isinstance(labels, str):
        console.print(f"[yellow]{labels}[/yellow]")
        return
        
    table = Table(title="Labels")
    table.add_column("Namespace", style="cyan", no_wrap=True)
    table.add_column("Query Handlers", style="magenta")
    table.add_column("Agent Handlers", style="green")
    table.add_column("Embed Handlers", style="blue")
    table.add_column("Storage Handlers", style="yellow")

    table.add_row(
        labels.namespace,
        ", ".join(labels.query_handlers),
        ", ".join(labels.agent_handlers),
        ", ".join(labels.embed_handlers),
        ", ".join(labels.storage_handlers)
    )
    console.print(table)