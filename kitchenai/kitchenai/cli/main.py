import typer
import sys
import django
import os
from importlib import import_module
import logging
from django.conf import settings

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
def runserver() -> None:
    """Run Django runserver."""
    # from django.core.management import execute_from_command_line
    #sys.argv pop to remove the command line "dev" before extending the gunicorn command
    sys.argv.pop(1)
    django.setup()
    from kitchenai.api import api
    from kitchenai.core.utils import set_app, load_config_from_db

    _setup(
        set_app, 
        load_config_from_db,
        api
    )

    _run_dev_uvicorn(sys.argv)

@app.command()
def run() -> None:
    """Run Django runserver."""
    sys.argv.pop(1)
    django.setup()
    from kitchenai.api import api
    from kitchenai.core.utils import set_app, load_config_from_db

    _setup(
        set_app, 
        load_config_from_db,
        api
    )

    _run_uvicorn(sys.argv)


@app.command()
def dev(address: str ="0.0.0.0:8000"):
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server
    """
    commands = {"server": f"kitchenai runserver"}
    if "django_tailwind_cli" in settings.INSTALLED_APPS:
        commands["tailwind"] = f"django-admin tailwind watch"
    if "tailwind" in settings.INSTALLED_APPS:
        commands["tailwind"] = f"django-admin tailwind start"
    if "django_q" in settings.INSTALLED_APPS:
        commands["qcluster"] = f"kitchenai qcluster"

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
    from django.core.management import execute_from_command_line
    from django.core.management.base import CommandError
    from contextlib import suppress

    execute_from_command_line(["manage", "migrate"])
    execute_from_command_line(["manage", "setup_periodic_tasks"])

    with suppress(CommandError):
        execute_from_command_line(
            ["manage", "createsuperuser", "--noinput", "--traceback"]
        )


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


def _setup(set_app, load_config_from_db, api):
    # # Load configuration from the database
    config = load_config_from_db()

    if not config:
        logger.error('No configuration found. Please run "kitchenai init" first.')
        return
    
    # Update INSTALLED_APPS and import modules
    # self.update_installed_apps(config.get('installed_apps', []))
    set_app(config.get("app"))
    # self.import_modules(config.get('module_paths', {}))
    if settings.KITCHENAI_APP:

        # Determine the user's project root directory (assumes the command is run from the user's project root)
        project_root = os.getcwd()

        # Add the user's project root directory to the Python path
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        module_path, instance_name = settings.KITCHENAI_APP.split(':')

        try:
            module_path, instance_name = settings.KITCHENAI_APP.split(':')
            module = import_module(module_path)
            instance = getattr(module, instance_name)
            
            logger.info(f'Imported {instance_name} from {module_path}')
        except (ImportError, AttributeError) as e:
            logger.error(f"Error loading module: {e}")

    api.add_router("/core", instance)