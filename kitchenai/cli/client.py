import typer
from kitchenai_python_sdk import DefaultApi, ApiClient, Configuration
from kitchenai_python_sdk.models.query_schema import QuerySchema
from kitchenai_python_sdk.models.upload_module_input import UploadModuleInput
from kitchenai_python_sdk.models.file_object_schema import FileObjectSchema
from kitchenai_python_sdk.models.embed_schema import EmbedSchema
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
import json

app = typer.Typer()
console = Console()

# Configuration for API client
API_HOST = "http://localhost:8001"
configuration = Configuration(host=API_HOST)


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
            result = api_instance.kitchenai_contrib_kitchenai_sdk_kitchenai_query_handler(label, schema)
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




@app.command("upload-file")
def upload_file(name: str, ingest_label: str = None, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
    """Upload a file."""

    if metadata:
        metadata_p = json.loads(metadata)

    else:
        metadata_p = {}
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        schema = FileObjectSchema(name=name, ingest_label=ingest_label, metadata=metadata_p)
        try:
            api_response = api_instance.kitchenai_core_api_file_upload(file=None, data=schema)
            console.print(f"[green]File '{name}' uploaded successfully! Response: {api_response}[/green]")
        except Exception as e:
            console.print(f"[red]Error uploading file: {e}[/red]")


@app.command("get-embeds")
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


@app.command("create-embed")
def create_embed(text: str, ingest_label: str = None, metadata: Annotated[str, typer.Option(help="add metadata.")] = ""):
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


@app.command("delete-embed")
def delete_embed(embed_id: int):
    """Delete an embed by ID."""
    with ApiClient(configuration) as api_client:
        api_instance = DefaultApi(api_client)
        try:
            api_instance.kitchenai_core_api_embed_delete(embed_id)
            console.print(f"[green]Embed ID '{embed_id}' deleted successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error deleting embed: {e}[/red]")


