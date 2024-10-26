import logging
import sys

import django
import typer
from django.conf import settings
from cookiecutter.main import cookiecutter
from typing_extensions import Annotated


logger = logging.getLogger(__name__)
app = typer.Typer()

@app.command()
def add(module: str = typer.Argument("app.kitchen:kitchen")):
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage", "add_module", module])

@app.command()
def init():
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage", "migrate"])
    execute_from_command_line(["manage", "init"])


@app.command()
def qcluster() -> None:
    """Run Django-q cluster."""
    from django.core.management import execute_from_command_line
    # execute_from_command_line(["manage", "qcluster", *argv[2:]])
    execute_from_command_line(["manage", "qcluster"])


@app.command()
def runserver(module: Annotated[str, typer.Option(help="Python module to load.")] = "") -> None:
    """Run Django runserver."""
    #NOTE: doing this to reset the sys.argv for gunicorn command.
    sys.argv = [sys.argv[0]]

    django.setup()
    from kitchenai.api import api
    from kitchenai.core.utils import setup

    setup(
        api,
        module=module
    )
    _run_dev_uvicorn(sys.argv)

@app.command()
def run(module: Annotated[str, typer.Option(help="Python module to load.")] = "") -> None:
    """Run Django runserver."""
    sys.argv = [sys.argv[0]]
    django.setup()
    from kitchenai.api import api
    from kitchenai.core.utils import setup

    setup(
        api,
        module=module
    )

    _run_uvicorn(sys.argv)


@app.command()
def dev(address: str ="0.0.0.0:8000", module: Annotated[str, typer.Option(help="Python module to load.")] = "" ):
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server
    """
    commands = {"server": "kitchenai runserver"}
    if module:
        commands["server"] = f"kitchenai runserver --module {module}"
    if "django_tailwind_cli" in settings.INSTALLED_APPS:
        commands["tailwind"] = "django-admin tailwind watch"
    if "tailwind" in settings.INSTALLED_APPS:
        commands["tailwind"] = "django-admin tailwind start"
    if "django_q" in settings.INSTALLED_APPS:
        commands["qcluster"] = "kitchenai qcluster"

    typer.echo(f"[INFO] starting development server on {address}")

    # call_command("migrate")
    _run_with_honcho(commands)

@app.command()
def manage() -> None:
    """Run Django's manage command."""
    from django.core.management import execute_from_command_line

    # execute_from_command_line(argv[1:])
    execute_from_command_line(["manage"])

@app.command()
def setup():
    """Run some project setup tasks"""
    django.setup()
    from django.core.management import execute_from_command_line
    import os

    execute_from_command_line(["manage", "migrate"])
    execute_from_command_line(["manage", "setup_periodic_tasks"])

    # Set environment variables for superuser credentials
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@localhost")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", email.split("@")[0])

    if password == "admin":
        #set it 
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"
    execute_from_command_line(
        ["manage", "createsuperuser", "--noinput", "--traceback", "--email", email, "--username", username]
    )

@app.command()
def build():
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server
    """
    from django.core.management import execute_from_command_line
    django.setup()

    execute_from_command_line(["manage", "build_container"])


@app.command()
def new():
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server
    """

    cookiecutter("https://github.com/epuerta9/cookiecutter-cookbook.git", output_dir=".")



def _run_with_honcho(commands: dict):
    from honcho.manager import Manager

    manager = Manager()
    for name, cmd in commands.items():
        manager.add_process(name, cmd)
    try:
        manager.loop()
    finally:
        manager.terminate()



def _run_uvicorn(argv: list) -> None:
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
        "0.0.0.0:8000",
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


def _run_dev_uvicorn(argv: list) -> None:
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
        "0.0.0.0:8000",
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
