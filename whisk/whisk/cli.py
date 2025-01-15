import typer
import asyncio
import logging
from rich.console import Console
from typing import Optional, List, Dict, TYPE_CHECKING
from . import __version__
from .client import WhiskClient
import asyncio
import uuid
import time
import json
from faststream.nats import NatsBroker
from .kitchenai_sdk.nats_schema import QueryRequestMessage, StorageRequestMessage, EmbedRequestMessage, BroadcastRequestMessage, NatsMessageBase
from .client import WhiskClient
from faststream.exceptions import INSTALL_WATCHFILES, SetupError, ValidationError
from faststream.cli.utils.imports import import_from_string
import sys
from faststream._internal.application import Application
import os
import importlib

if TYPE_CHECKING:
    from faststream.broker.core.usecase import BrokerUsecase
    from faststream.types import AnyDict, SettingField

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
        app=kitchen
    )

    async def start():
        await client.app.run()

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        console.print("\nShutting down gracefully...")

@app.command()
def run(
    ctx: typer.Context,
    kitchen: str = typer.Argument(
        "app:kitchen",
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
        "clienta",
        "--user",
        "-u",
        help="NATS user (clienta or clientb)"
    ),
    password: str = typer.Option(
        None,
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
):
    """Run Whisk Server"""
    if reload and workers > 1:
        raise SetupError("You can't use reload option with multiprocessing")
    
    try:
        from watchfiles import run_process
    except ImportError:
        console.print("[red]Please install watchfiles for reload support: pip install watchfiles[/red]")
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
                    args=(kitchen, nats_url, f"{client_id}_{i}", user, password)
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
    target: str = typer.Option(
        ...,
        "--target",
        "-t",
        help="Target client (e.g., clienta)"
    ),
    user: str = typer.Option(
        "kitchenai_admin",
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
    rpc: bool = typer.Option(
        True,
        "--rpc",
        help="Send RPC request"
    )
):
    """Send a query to a specific client"""
    try:
        meta_dict = json.loads(metadata) if metadata else {}
        meta_dict["client"] = target
        
        message = QueryRequestMessage(
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            query=query,
            metadata=meta_dict,
            stream=stream
        )

        async def send_message():
            client = WhiskClient(
                    nats_url=nats_url,
                    client_id="whisk_cli",
                    user=user,
                    password=password
                )
            async with client.app.broker:
                console.print(f"Sending message to {target}")
                console.print(f"Content: {message.model_dump_json(indent=2)}")
                if rpc:
                    response = await client.query(message, target)
                    console.print(f"Response: {response}")
                else:
                    await client.query(message, target)
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
    target: str = typer.Option(
        ...,
        "--target",
        "-t",
        help="Target client"
    ),
    extension: Optional[str] = typer.Option(
        None,
        "--ext",
        "-e",
        help="File extension filter"
    ),
    metadata: Optional[str] = typer.Option(None, "--metadata", "-m"),
    user: str = typer.Option("kitchenai_admin"),
    password: str = typer.Option(None),
    nats_url: str = typer.Option("nats://localhost:4222")
):
    """Send a storage request"""
    try:
        meta_dict = json.loads(metadata) if metadata else {}
        meta_dict["client"] = target
        
        message = StorageRequestMessage(
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            dir=directory,
            metadata=meta_dict,
            extension=extension
        )
        
        asyncio.run(send_message(
            message=message,
            target=target,
            subject_suffix="storage",
            user=user,
            password=password,
            nats_url=nats_url
        ))
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
        
        asyncio.run(send_message(
            message=message,
            target=target,
            subject_suffix="embed",
            user=user,
            password=password,
            nats_url=nats_url
        ))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def broadcast(
    message: str = typer.Option(
        ...,
        "--message",
        "-m",
        help="Message to broadcast"
    ),
    type: str = typer.Option(
        "info",
        "--type",
        "-t",
        help="Message type (info, warning, error)"
    ),
    metadata: Optional[str] = typer.Option(None, "--metadata"),
    user: str = typer.Option("kitchenai_admin"),
    password: str = typer.Option(None),
    nats_url: str = typer.Option("nats://localhost:4222")
):
    """Send a broadcast message"""
    try:
        meta_dict = json.loads(metadata) if metadata else {}
        
        message = BroadcastRequestMessage(
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            message=message,
            type=type,
            metadata=meta_dict
        )
        
        asyncio.run(send_message(
            message=message,
            target=None,
            subject="kitchenai.broadcast.message",
            user=user,
            password=password,
            nats_url=nats_url
        ))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

async def send_message(
    message: NatsMessageBase,
    target: Optional[str],
    subject_suffix: str = "query",
    subject: Optional[str] = None,
    user: str = "kitchenai_admin",
    password: Optional[str] = None,
    nats_url: str = "nats://localhost:4222"
):
    """Generic message sender using WhiskClient"""
    from .client import WhiskClient
    
    client = WhiskClient(
        nats_url=nats_url,
        client_id="whisk_cli",
        user=user,
        password=password
    )
    
    async with client.app.broker:
        if subject is None and target is not None:
            subject = f"kitchenai.service.{target}.{subject_suffix}"
        console.print("HEREEE")
        console.print(f"Sending message to {subject}")
        console.print(f"Content: {message.model_dump_json(indent=2)}")
        
        # Use the client's broker to send the message
        await client.query(message, metadata={"client": target})
        console.print("[green]Message sent successfully![/green]")


async def query_fn(message: QueryRequestMessage, target: str, broker: NatsBroker):
    """Send a query request"""
    if message.stream:
        await broker.publish(message, f"kitchenai.service.{target}.query")
    else:
        response = await broker.request(message, f"kitchenai.service.{target}.query")
        return response
    

# def _run(
#     # NOTE: we should pass `str` due FastStream is not picklable
#     app: str,
#     extra_options: Dict[str, "SettingField"],
#     is_factory: bool,
#     log_level: int = logging.NOTSET,
#     app_level: int = logging.INFO,  # option for reloader only
# ) -> None:
#     """Runs the specified application."""
#     _, app_obj = import_from_string(app, is_factory=is_factory)
#     _run_imported_app(
#         app_obj,
#         extra_options=extra_options,
#         log_level=log_level,
#         app_level=app_level,
#     )


# def _run_imported_app(
#     app_obj: "Application",
#     extra_options: Dict[str, "SettingField"],
#     log_level: int = logging.NOTSET,
#     app_level: int = logging.INFO,  # option for reloader only
# ) -> None:
#     if not isinstance(app_obj, Application):
#         raise typer.BadParameter(
#             f'Imported object "{app_obj}" must be "Application" type.',
#         )

#     if log_level > 0:
#         set_log_level(log_level, app_obj)

#     if sys.platform not in ("win32", "cygwin", "cli"):  # pragma: no cover
#         with suppress(ImportError):
#             import uvloop

#             uvloop.install()

#     try:
#         anyio.run(
#             app_obj.run,
#             app_level,
#             extra_options,
#         )

#     except ValidationError as e:
#         ex = MissingParameter(
#             message=(
#                 "You registered extra options in your application "
#                 "`lifespan/on_startup` hook, but does not set in CLI."
#             ),
#             param=TyperOption(param_decls=[f"--{x}" for x in e.fields]),
#         )

#         try:
#             from typer import rich_utils

#             rich_utils.rich_format_error(ex)
#         except ImportError:
#             ex.show()

#         sys.exit(1)