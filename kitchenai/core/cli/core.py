import logging
import sys

import django
import typer
from rich.console import Console
from typing import Annotated

app = typer.Typer()
console = Console()


logger = logging.getLogger(__name__)


@app.command()
def init(
    verbose: Annotated[int, typer.Option(help="verbosity level. default 0")] = 0,
):
    """Initialize KitchenAI with optional plugin installation."""
    django.setup()
    from django.core.management import execute_from_command_line
    from kitchenai.core.models import KitchenAIManagement
    from django.conf import settings
    from django.apps import apps
    import posthog
    import warnings

    posthog.capture("init", "kitchenai_init")
    cmd = ["manage", "migrate", "--verbosity", f"{verbose}"]
    warnings.filterwarnings(
        "ignore", category=Warning, module="django.contrib.staticfiles"
    )
    warnings.filterwarnings("ignore", category=Warning, module="django.contrib")
    console.print(f"[green]KitchenAI version: {settings.VERSION}[/green]")

    with console.status("Applying migrations...", spinner="dots"):
        execute_from_command_line(cmd)

    with console.status("Setting up periodic tasks", spinner="dots"):
        execute_from_command_line(["manage", "setup_periodic_tasks"])

    KitchenAIManagement.objects.all().delete()
    try:
        mgmt = KitchenAIManagement.objects.create(version=settings.VERSION)
    except Exception as e:
        logger.error(e)
    if settings.KITCHENAI_LICENSE == "oss":
        try:
            Organization = apps.get_model(settings.AUTH_ORGANIZATION_MODEL)
            if not Organization.objects.exists():
                org = Organization.objects.create(
                    name=Organization.DEFAULT_NAME,
                    slug="default-organization",
                    allow_signups=True,
                )
                logger.info(f"Created default organization: {org.name}")
            else:
                logger.info("Default organization already exists")
        except Exception as e:
            logger.error(f"Failed to create default organization: {str(e)}")


@app.command()
def qcluster() -> None:
    """Run Django-q cluster."""
    from django.core.management import execute_from_command_line

    # execute_from_command_line(["manage", "qcluster", *argv[2:]])
    execute_from_command_line(["manage", "qcluster"])


@app.command()
def runserver(
    address: Annotated[
        str, typer.Option(help="Address to run the server on.")
    ] = "0.0.0.0:8001",
) -> None:
    """Run Django runserver."""

    from django.core.management import execute_from_command_line

    args = ["manage", "runserver"]
    args.append(address)
    execute_from_command_line(args)


@app.command()
def run(
    lite: Annotated[bool, typer.Option(help="Lite version of ASGI server")] = False,
    address: Annotated[
        str, typer.Option(help="Address to run the server on.")
    ] = "0.0.0.0:8001",
) -> None:
    """Run Django runserver."""
    sys.argv = [sys.argv[0]]
    django.setup()

    if lite:
        _run_dev_uvicorn(sys.argv, address)
    else:
        _run_uvicorn(sys.argv, address)


@app.command()
def manage(
    args: list[str] = typer.Argument(None, help="Arguments for Django's manage.py")
) -> None:
    """
    Run Django's manage command with additional arguments.
    """
    from django.core.management import execute_from_command_line

    # Build the argument list for Django
    if args is None:
        sys.argv = ["manage"]
    else:
        sys.argv = ["manage"] + args

    execute_from_command_line(sys.argv)


def _run_uvicorn(argv: list, address: str = "0.0.0.0:8001") -> None:
    """
    Run gunicorn + uvicorn workers server.
    https://docs.gunicorn.org/en/stable/settings.html
    https://adamj.eu/tech/2021/12/29/set-up-a-gunicorn-configuration-file-and-test-it/
    """

    import multiprocessing
    from gunicorn.app import wsgiapp  # for gunicorn

    workers = multiprocessing.cpu_count() * 2 + 1
    gunicorn_args = [
        "kitchenai.asgi:application",  # Replace WSGI with ASGI app
        "--bind",
        address,
        # "unix:/run/kitchenai_demo.gunicorn.sock",  # Use this if you're using a socket file
        "--max-requests",
        "1000",
        "--max-requests-jitter",
        "50",
        "--workers",
        str(workers),
        "--worker-class",
        "uvicorn.workers.UvicornWorker",  # Use Uvicorn worker for ASGI
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
    ]
    argv.extend(gunicorn_args)

    wsgiapp.run()


def _run_dev_uvicorn(argv: list, address: str = "0.0.0.0:8001") -> None:
    """
    Run gunicorn + uvicorn workers server.
    https://docs.gunicorn.org/en/stable/settings.html
    https://adamj.eu/tech/2021/12/29/set-up-a-gunicorn-configuration-file-and-test-it/
    """
    from gunicorn.app import wsgiapp  # for gunicorn

    workers = 2
    gunicorn_args = [
        "kitchenai.asgi:application",  # Replace WSGI with ASGI app
        "--bind",
        address,
        # "unix:/run/kitchenai_demo.gunicorn.sock",  # Use this if you're using a socket file
        "--max-requests",
        "1000",
        "--max-requests-jitter",
        "50",
        "--workers",
        str(workers),
        "--worker-class",
        "uvicorn.workers.UvicornWorker",  # Use Uvicorn worker for ASGI
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
    ]
    argv.extend(gunicorn_args)

    wsgiapp.run()

