import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
import json
from kitchenai_python_sdk.api_client import ApiClient
from kitchenai_python_sdk.api.default_api import DefaultApi
from kitchenai_python_sdk.configuration import Configuration
from kitchenai_python_sdk.models.embed_schema import EmbedSchema
from kitchenai_python_sdk.models.file_object_schema import FileObjectSchema
from kitchenai_python_sdk.models.query_schema import QuerySchema

app = typer.Typer()
console = Console()

# Configuration for API client
API_HOST = "http://localhost:8001"
configuration = Configuration(host=API_HOST)

file_app = typer.Typer()
embed_app = typer.Typer()

@app.command("health")
def health_check():
    """Check the health of the API."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            api_instance.kitchenai_core_api_default()
            console.print("[green]API is healthy![/green]")
        except Exception as e:
            console.print(f"[red]Failed to reach API: {e}[/red]")


@app.command("query")
def run_query(label: str, query: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Run a query using the Query Handler."""

    if metadata:
        metadata_p = json.loads(metadata)

    else:
        metadata_p = {}

    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        schema = QuerySchema(query=query, metadata=metadata_p)
        try:
            result = api_instance.kitchenai_core_api_query(label, schema)
            console.print(f"[green]Query '{label}' executed successfully![/green]")
            console.print(result)
        except Exception as e:
            console.print(f"[red]Error running query: {e}[/red]")


@app.command("agent")
def run_agent(label: str, query: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Run an agent using the Agent Handler."""

    if metadata:
        metadata_p = json.loads(metadata)

    else:
        metadata_p = {}
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        schema = QuerySchema(query=query, metadata=metadata_p)
        try:
            api_instance.kitchenai_contrib_kitchenai_sdk_kitchenai_agent_handler(label, schema)
            console.print(f"[green]Agent '{label}' executed successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error running agent: {e}[/red]")


@app.command("file")
def file():
    """File operations."""
    pass

@file_app.command("create")
def create_file(file_path: str, name: str, ingest_label: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Create a file."""
    if metadata:
        metadata_p = json.loads(metadata)
    else:
        metadata_p = {}

    with open(file_path, 'rb') as file:
        file_content = file.read()
        with ApiClient(configuration) as api_client:
            api_instance = DefaultApi(api_client)
            schema = FileObjectSchema(name=name, ingest_label=ingest_label, metadata=metadata_p)
            try:
                api_response = api_instance.kitchenai_core_api_file_upload(file=(name, file_content), data=schema)
                console.print(f"[green]File '{name}' created successfully! Response: {api_response}[/green]")
            except Exception as e:
                console.print(f"[red]Error creating file: {e}[/red]")

@file_app.command("read")
def read_file(file_id: int):
    """Read a file by ID."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            file_data = api_instance.kitchenai_core_api_file_get(file_id)
            console.print(f"[green]File ID '{file_id}' retrieved successfully![/green]")
            console.print(file_data)
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")

@file_app.command("update")
def update_file(file_id: int, name: str = None, ingest_label: str = None, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Update a file by ID."""
    if metadata:
        metadata_p = json.loads(metadata)
    else:
        metadata_p = {}

    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        schema = FileObjectSchema(name=name, ingest_label=ingest_label, metadata=metadata_p)
        try:
            api_response = api_instance.kitchenai_core_api_file_update(file_id, data=schema)
            console.print(f"[green]File ID '{file_id}' updated successfully! Response: {api_response}[/green]")
        except Exception as e:
            console.print(f"[red]Error updating file: {e}[/red]")

@file_app.command("delete")
def delete_file(file_id: int):
    """Delete a file by ID."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            api_instance.kitchenai_core_api_file_delete(file_id)
            console.print(f"[green]File ID '{file_id}' deleted successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error deleting file: {e}[/red]")

@file_app.command("list")
def list_files():
    """List all files."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            files = api_instance.kitchenai_core_api_files_get()
            if not files:
                console.print("[yellow]No files found.[/yellow]")
                return
            table = Table(title="Files")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Ingest Label", style="green")
            for file in files:
                table.add_row(str(file.id), file.name, file.ingest_label or "N/A")
            console.print(table)
        except Exception as e:
            console.print(f"[red]Error fetching files: {e}[/red]")

app.add_typer(file_app, name="file")

@app.command("embed")
def embed():
    """Embed operations."""
    pass

@embed_app.command("list")
def get_all_embeds():
    """Get all embeds."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            embeds = api_instance.kitchenai_core_api_embeds_get()
            if not embeds:
                console.print("[yellow]No embeds found.[/yellow]")
                return
            table = Table(title="Embeds")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Text", style="magenta")
            for embed in embeds:
                table.add_row(str(embed.id), embed.text)
            console.print(table)
        except Exception as e:
            console.print(f"[red]Error fetching embeds: {e}[/red]")

@embed_app.command("create")
def create_embed(text: str, ingest_label: str, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Create an embed."""
    if metadata:
        metadata_p = json.loads(metadata)
    else:
        metadata_p = {}
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        schema = EmbedSchema(text=text, ingest_label=ingest_label, metadata=metadata_p)
        try:
            response = api_instance.kitchenai_core_api_embed_create(schema)
            console.print(f"[green]Embed created successfully! Response: {response}[/green]")
        except Exception as e:
            console.print(f"[red]Error creating embed: {e}[/red]")

@embed_app.command("delete")
def delete_embed(embed_id: int):
    """Delete an embed by ID."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            api_instance.kitchenai_core_api_embed_delete(embed_id)
            console.print(f"[green]Embed ID '{embed_id}' deleted successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error deleting embed: {e}[/red]")

app.add_typer(embed_app, name="embed")

@app.command("labels")
def list_labels():
    """List all custom kitchenai labels."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            labels = api_instance.kitchenai_core_api_labels()
            if not labels:
                console.print("[yellow]No labels found.[/yellow]")
                return
            table = Table(title="Labels")
            table.add_column("Namespace", style="cyan", no_wrap=True)
            table.add_column("Query Handlers", style="magenta")
            table.add_column("Agent Handlers", style="green")
            table.add_column("Embed Tasks", style="blue")
            table.add_column("Embed Delete Tasks", style="red")
            table.add_column("Storage Tasks", style="yellow")
            table.add_column("Storage Delete Tasks", style="purple")
            table.add_column("Storage Create Hooks", style="white")
            table.add_column("Storage Delete Hooks", style="blue")

            table.add_row(
                labels.namespace,
                ", ".join(labels.query_handlers),
                ", ".join(labels.agent_handlers),
                ", ".join(labels.embed_tasks),
                ", ".join(labels.embed_delete_tasks),
                ", ".join(labels.storage_tasks),
                ", ".join(labels.storage_delete_tasks),
                ", ".join(labels.storage_create_hooks),
                ", ".join(labels.storage_delete_hooks),
            )
            console.print(table)
        except Exception as e:
            console.print(f"[red]Error fetching labels: {e}[/red]")


