import typer
import asyncio
from rich.console import Console
from typing import Optional, List
from . import __version__
from .client import WhiskClient
import asyncio
import uuid
import time
import json
from faststream.nats import NatsBroker
from .kitchenai_sdk.nats_schema import QueryRequestMessage, StorageRequestMessage, EmbedRequestMessage
from .client import WhiskClient
from faststream.exceptions import SetupError
import sys
import os
import importlib
from .kitchenai_sdk.nats_schema import QueryResponseMessage

app = typer.Typer(
    name="whisk",
    help="KitchenAI Whisk - Task Management",
)
console = Console()

def version_callback(value: bool):
    if value:
        console.print(f"KitchenAI Whisk v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """KitchenAI Whisk - Task Management"""
    pass

def run_app(path: str, nats_url: str, client_id: str, user: str, password: str):
    # Split the path into module and attribute
    module_path, attr = path.split(":")
    
    # Import the module and get the kitchen attribute
    kitchen_module = importlib.import_module(module_path)
    # Clear module from cache to allow reloading
    if module_path in sys.modules:
        importlib.reload(kitchen_module)
    kitchen = getattr(kitchen_module, attr)

    client = WhiskClient(
        nats_url=nats_url, 
        client_id=client_id,
        user=user,
        password=password,
        kitchen=kitchen
    )
    
    async def start():
        await client.run()

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        console.print("\nShutting down gracefully...")

@app.command()
def run(
    ctx: typer.Context,
    kitchen: str = typer.Argument(
        "whisk.examples.app:kitchen",
        help="App to run"
    ),
    nats_url: str = typer.Option(
        "nats://localhost:4222",
        "--nats-url",
        "-n",
        help="NATS server URL"
    ),
    client_id: str = typer.Option(
        "whisk_client",
        "--client-id",
        "-c",
        help="Client ID"
    ),
    user: str = typer.Option(
        "playground",
        "--user",
        "-u",
        help="NATS user (clienta or clientb)"
    ),
    password: str = typer.Option(
        "kitchenai_playground",
        "--password",
        "-p",
        help="NATS password from environment (CLIENTA_PASSWORD or CLIENTB_PASSWORD)"
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        is_flag=True,
        help="Restart app at directory files changes.",
    ),
    workers: int = typer.Option(
        1,
        show_default=False,
        help="Run [workers] applications with process spawning.",
        envvar="FASTSTREAM_WORKERS",
    ),
    watch_extensions: List[str] = typer.Option(
        (),
        "--extension",
        "--ext",
        "--reload-extension",
        "--reload-ext",
        help="List of file extensions to watch by.",
    ),
    example: bool = typer.Option(
        False,
        "--example",
        is_flag=True,
        help="Run example app"
    )
):
    """Run Whisk Server"""
    if reload and workers > 1:
        raise SetupError("You can't use reload option with multiprocessing")
    
    try:
        from watchfiles import run_process
    except ImportError:
        console.print("[red]Please install watchfiles for reload support: pip install watchfiles[/red]")
        raise typer.Exit(1)
    
    if not example and kitchen.startswith("whisk.examples."):
        console.print("[red]Please use the --example flag to run example apps[/red]")
        raise typer.Exit(1)
    
 

    # Add current directory to Python path
    sys.path.append(os.getcwd())
    
    if reload:
        watch_extensions = watch_extensions or [".py"]
        console.print(f"[green]Running with reload (watching {', '.join(watch_extensions)} files)[/green]")
        run_process(
            ".",
            target=run_app,
            args=(kitchen, nats_url, client_id, user, password),
            watch_filter=lambda change, filename: any(filename.endswith(ext) for ext in watch_extensions)
        )
    else:
        if workers > 1:
            import multiprocessing
            console.print(f"[green]Starting {workers} workers[/green]")
            processes = []
            for i in range(workers):
                p = multiprocessing.Process(
                    target=run_app,
                    args=(kitchen, nats_url, f"{client_id}", user, password)
                )
                p.start()
                processes.append(p)
            
            try:
                for p in processes:
                    p.join()
            except KeyboardInterrupt:
                console.print("\n[yellow]Shutting down workers...[/yellow]")
                for p in processes:
                    p.terminate()
        else:
            run_app(kitchen, nats_url, client_id, user, password)





@app.command()
def query(
    query: str = typer.Option(
        ...,
        "--query",
        "-q",
        help="Query to send"
    ),
    user: str = typer.Option(
        "kitchenai",
        "--user",
        "-u",
        help="NATS user"
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="NATS password"
    ),
    metadata: Optional[str] = typer.Option(
        None,
        "--metadata",
        "-m",
        help="Metadata as JSON string"
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        help="Enable streaming response"
    ),
    nats_url: str = typer.Option(
        "nats://localhost:4222",
        "--nats-url",
        "-n",
        help="NATS server URL"
    ),
    stream_id: Optional[str] = typer.Option(
        None,
        "--stream-id",
        "-s",
        help="Stream ID"
    ),
    client_id: Optional[str] = typer.Option(
        "whisk_cli",
        "--client-id",
        "-c",
        help="Client ID"
    ),
    label: Optional[str] = typer.Option(
        "query",
        "--label",
        "-l",
        help="Label for the query"
    )
):
    """Send a query to a specific client"""
    try:
        meta_dict = json.loads(metadata) if metadata else {}
        meta_dict["label"] = label
        meta_dict["client_id"] = client_id
        if stream:
            #default label for stream
            label = "stream"

        message = QueryRequestMessage(
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            query=query,
            metadata=meta_dict,
            stream=stream,
            label=label,
            client_id=client_id
        )

        async def send_message():
            client = WhiskClient(
                    nats_url=nats_url,
                    client_id="kitchenai",
                    user=user,
                    password=password
                )
            async with client.app.broker:
                if message.stream:
                    async for chunk in client.query_stream(message):
                        response = QueryResponseMessage.model_validate_json(chunk)
                        if response.error:
                            console.print(f"[red]{response.error}[/red]")
                        else:
                            console.print(response.model_dump_json(indent=2))
                else:
                    response = await client.query(message)
                    console.print(response.decoded_body)
                console.print("[green]Message sent successfully![/green]")
        
        asyncio.run(send_message())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def storage(
    directory: str = typer.Option(
        ...,
        "--dir",
        "-d",
        help="Directory to process"
    ),
    client_id: Optional[str] = typer.Option(
        "whisk_cli",
        "--client-id",
        "-c",
        help="Client ID"
    ),
    extension: Optional[str] = typer.Option(
        None,
        "--ext",
        "-e",
        help="File extension filter"
    ),

    metadata: Optional[str] = typer.Option(None, "--metadata", "-m"),
    user: str = typer.Option(
        "kitchenai",
        "--user",
        "-u",
        help="NATS user"
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="NATS password"
    ),
    nats_url: str = typer.Option(
        "nats://localhost:4222",
        "--nats-url",
        "-n",
        help="NATS server URL"
    ),
    id: Optional[int] = typer.Option(
        1,
        "--id",
        "-i",
        help="ID of the file"
    )
):
    """Send a storage request"""
    try:
        meta_dict = json.loads(metadata) if metadata else {}
        meta_dict["client"] = client_id 
        
        async def process_file():
            client = WhiskClient(
                nats_url=nats_url,
                client_id="whisk_client",
                user=user,
                password=password
            )
            
            async with client.app.broker:
                # Read file content
                with open(directory, 'rb') as f:
                    file_data = f.read()
                
                message = StorageRequestMessage(
                    request_id=str(uuid.uuid4()),
                    name=os.path.basename(directory),
                    id=id,
                    timestamp=time.time(),
                    metadata=meta_dict,
                    extension=extension,
                    client_id=client_id,
                    label="storage"
                )
                
                console.print(f"Processing file: {directory}")
                await client.store(message, file_data)
                console.print("[green]File sent for processing![/green]")

        asyncio.run(process_file())

    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {directory}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def embed(
    text: str = typer.Option(
        ...,
        "--text",
        "-t",
        help="Text to embed"
    ),
    target: str = typer.Option(
        ...,
        "--target",
        help="Target client"
    ),
    metadata: Optional[str] = typer.Option(None, "--metadata", "-m"),
    user: str = typer.Option("kitchenai_admin"),
    password: str = typer.Option(None),
    nats_url: str = typer.Option("nats://localhost:4222")
):
    """Send an embedding request"""
    try:
        meta_dict = json.loads(metadata) if metadata else {}
        meta_dict["client"] = target
        
        message = EmbedRequestMessage(
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            text=text,
            metadata=meta_dict
        )
        
        # asyncio.run(send_message(
        #     message=message,
        #     target=target,
        #     subject_suffix="embed",
        #     user=user,
        #     password=password,
        #     nats_url=nats_url
        # ))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


