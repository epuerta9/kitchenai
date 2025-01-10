import logging
import os
import sys

import django
import typer
from cookiecutter.main import cookiecutter
from django.conf import settings
from rich.console import Console
from typing import Annotated
from kitchenai.bento.cli.bento import select as bento_select
import subprocess
import time
app = typer.Typer()
console = Console()


logger = logging.getLogger(__name__)


# @app.command()
# def add(module: str = typer.Argument("app.kitchen:kitchen")):
#     from django.core.management import execute_from_command_line

#     execute_from_command_line(["manage", "add_module", module])


@app.command()
def init(
    verbose: Annotated[int, typer.Option(help="verbosity level. default 0")] = 0,
    collect_static: Annotated[
        bool,
        typer.Option(
            "-s/--no-collect-static",
            help="Don't collect static assets.",
        ),
    ] = False,
    bento: Annotated[
        str, typer.Option("--bento", help="Bento box to install")
    ] = "kitchenai_rag_simple_bento",
    plugin: Annotated[
        str, typer.Option("--plugin", help="Plugin to install")
    ] = "deepeval_plugin",
    local: Annotated[
        bool, typer.Option("--local/--no-local", help="local setup.")
    ] = False,
):
    """Initialize KitchenAI with optional plugin installation."""
    django.setup()
    from django.core.management import execute_from_command_line
    from kitchenai.core.models import KitchenAIManagement
    from django.conf import settings
    import posthog
    import warnings

    posthog.capture("init", "kitchenai_init")
    cmd = ["manage", "migrate", "--verbosity", f"{verbose}"]
    warnings.filterwarnings(
        "ignore", category=Warning, module="django.contrib.staticfiles"
    )
    warnings.filterwarnings("ignore", category=Warning, module="django.contrib")

    if verbose != 1:
        with console.status("Applying migrations...", spinner="dots"):
            execute_from_command_line(cmd)

        with console.status("Setting up periodic tasks", spinner="dots"):
            execute_from_command_line(["manage", "setup_periodic_tasks"])

        # Apply migrations for the packages we just installed
        execute_from_command_line(cmd)

        if local:
            try:
                email = "admin@localhost"
                password = "admin"
                username = email.split("@")[0]

                if password == "admin":
                    os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"
                    execute_from_command_line(
                        [
                            "manage",
                            "createsuperuser",
                            "--noinput",
                            "--traceback",
                            "--email",
                            email,
                            "--username",
                            username,
                        ]
                    )
            except Exception as e:
                console.print(
                    f"[red]ERROR:[/red] Failed to create superuser. Details: {e}"
                )
                return
    else:
        execute_from_command_line(cmd)

        execute_from_command_line(["manage", "setup_periodic_tasks"])

        # apply migrations for the packages we just installed
        execute_from_command_line(cmd)

        if local:
            try:
                email = "admin@localhost"
                password = "admin"
                username = email.split("@")[0]

                if password == "admin":
                    # set it
                    os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"
                execute_from_command_line(
                    [
                        "manage",
                        "createsuperuser",
                        "--noinput",
                        "--traceback",
                        "--email",
                        email,
                        "--username",
                        username,
                    ]
                )
            except Exception as e:
                console.print(
                    f"[red]ERROR:[/red] Failed to create superuser. Details: {e}"
                )
                return

    KitchenAIManagement.objects.all().delete()
    try:
        mgmt = KitchenAIManagement.objects.create(
            version=settings.VERSION, project_name="default"
        )
    except Exception as e:
        logger.error(e)
        return


@app.command()
def qcluster() -> None:
    """Run Django-q cluster."""
    from django.core.management import execute_from_command_line

    # execute_from_command_line(["manage", "qcluster", *argv[2:]])
    execute_from_command_line(["manage", "qcluster"])


@app.command()
def runserver(
    module: Annotated[str, typer.Option(help="Python module to load.")] = "",
    address: Annotated[
        str, typer.Option(help="Address to run the server on.")
    ] = "0.0.0.0:8001",
    stream: Annotated[
        bool, typer.Option(help="Stream events to the event stream.")
    ] = False,
) -> None:
    """Run Django runserver. If stream is true, it will run the uvicorn server.
    If stream is false, it will run the dev runserver.
    """

    if stream:
        django.setup()
        from kitchenai.api import api
        from kitchenai.core.utils import setup
        from kitchenai.bento.models import Bento

        if module:
            setup(api, module=module)
            console.print(f"[green]Successfully loaded module:[/green] {module}")
        else:
            try:
                bento_box = Bento.objects.first()
                if not bento_box:
                    logger.error(
                        "No bento box loaded. Please run 'bento select' to select a bento box."
                    )
                    raise Exception(
                        "No bento box loaded. Please run 'bento select' to select a bento box."
                    )
                bento_box.add_to_core()
            except Exception as e:
                logger.error(f"Error loading bento box: {e}")
        sys.argv = [sys.argv[0]]
        _run_dev_uvicorn(sys.argv)
    else:
        from django.core.management import execute_from_command_line

        args = ["manage", "runserver"]
        args.append(address)
        if module:
            args.append("--module")
            args.append(module)

        execute_from_command_line(args)


@app.command()
def run(
    module: Annotated[
        str, typer.Option(help="Python module to load.")
    ] = os.environ.get("KITCHENAI_MODULE", "")
) -> None:
    """Run Django runserver."""
    sys.argv = [sys.argv[0]]
    django.setup()
    from kitchenai.api import api
    from kitchenai.core.utils import setup
    from kitchenai.bento.models import Bento
    from kitchenai.core.models import KitchenAIManagement

    console = Console()

    if module:
        setup(api, module=module)
        console.print(f"[green]Successfully loaded module:[/green] {module}")
    else:
        mgmt = KitchenAIManagement.objects.filter(name="kitchenai_management").first()
        mgmt.module_path = "bento"
        mgmt.save()
        try:
            bento_box = Bento.objects.first()
            if not bento_box:
                #check if any bento boxes are installed. Load the first one from settings.KITCHENAI["bento"]
                bento_boxes = settings.KITCHENAI["bento"] 
                if bento_boxes:
                    installed_bento_box = bento_boxes[0]["name"]
                    bento_box = Bento.objects.create(name=installed_bento_box)
                    bento_box.add_to_core()
                    console.print(f"[green]Loaded bento box:[/green] {installed_bento_box}")
                else:
                    console.print("[red]Error:[/red] No bento box loaded. Please run 'bento select' to select a bento box.")
            else:
                bento_box.add_to_core()

            bento_box = Bento.objects.first()
            bento_box.add_to_core()
        except Bento.DoesNotExist:
            console.print(
                "[red]Error:[/red] No bento box loaded. Please run 'bento select' to select a bento box."
            )
            raise Exception(
                "No bento box loaded. Please run 'bento select' to select a bento box."
            )
    _run_uvicorn(sys.argv)


@app.command()
def dev(
    address: str = "0.0.0.0:8001",
    module: Annotated[str, typer.Option(help="Python module to load.")] = "",
    tailwind: Annotated[bool, typer.Option(help="Tailwind servers.")] = False,
    jupyter: Annotated[bool, typer.Option(help="Jupyter Notebook servers.")] = False,
    stream: Annotated[
        bool, typer.Option(help="Stream events to the event stream.")
    ] = False,
):
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server
    """
    import posthog
    import django
    import uuid

    django.setup()
    commands = {"server": "python kitchenai/ runserver"}

    posthog.capture("init", "kitchenai_dev")

    if module:
        commands["server"] = f"python kitchenai/ runserver --module {module}"
    if stream:
        commands["server"] = commands["server"] + " --stream"

    if jupyter:
        # user is running jupyter alongside kitchenai
        from kitchenai.core.models import KitchenAIManagement

        mgmt = KitchenAIManagement.objects.filter(name="kitchenai_management").first()
        notebook_id = uuid.uuid4()
        mgmt.jupyter_token = notebook_id
        mgmt.save()

        commands["jupyter"] = (
            f"jupyter lab --NotebookApp.token='{notebook_id}' --port=8888"
        )

    if tailwind:
        if "django_tailwind_cli" in settings.INSTALLED_APPS:
            commands["tailwind"] = "django-admin tailwind watch"
        if "tailwind" in settings.INSTALLED_APPS:
            commands["tailwind"] = "django-admin tailwind start"
    if "django_q" in settings.INSTALLED_APPS:
        commands["qcluster"] = "python kitchenai/ qcluster"

    typer.echo(f"[INFO] starting development server on {address}")

    # call_command("migrate")
    _run_with_honcho(commands)


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
        # set it
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"
    execute_from_command_line(
        [
            "manage",
            "createsuperuser",
            "--noinput",
            "--traceback",
            "--email",
            email,
            "--username",
            username,
        ]
    )


@app.command()
def build(
    dir: str,
    module: str,
    admin: Annotated[
        bool, typer.Option("--admin/--no-admin", help="Admin status (default is True)")
    ] = False,
):
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server.
    """
    django.setup()
    from django.template import loader
    import pathlib
    import subprocess
    from rich.text import Text

    base_dir = pathlib.Path(dir)

    # Flip the admin flag because we want it to default to True unless the flag is passed
    admin = not admin

    module_name = module.split(":")[0]

    # Save the configuration to the database
    template_name = "build_templates/Dockerfile.tmpl"

    # Check if requirements.txt and module file exist in the directory
    requirements_file = base_dir / "requirements.txt"
    module_path = base_dir / f"{module_name}.py"

    if not requirements_file.exists() or not module_path.exists():
        console.print(
            "[bold red]Error:[/bold red] Both requirements.txt and the module file must exist in the specified directory."
        )
        raise typer.Exit(code=1)

    # Context data to pass into the template
    context = {"module": module, "admin": admin}

    try:
        # Load and render the template with the context data
        template = loader.get_template(template_name)
        rendered_content = template.render(context)

        # Write the rendered Dockerfile to the specified directory
        dockerfile_path = base_dir / "Dockerfile"
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(rendered_content)

        console.print(
            Text(f"Dockerfile successfully created at {dockerfile_path}", style="green")
        )

    except Exception as e:
        console.print(
            f"[bold red]Error rendering template:[/bold red] {e}", style="bold red"
        )
        raise typer.Exit(code=1)

    # Build the Docker image using the Dockerfile
    try:
        console.print("[cyan]Building Docker image...[/cyan]")
        # Run the Docker build command
        process = subprocess.Popen(
            ["docker", "build", "-t", "kitchenai-app", dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Stream output line by line
        for stdout_line in iter(process.stdout.readline, ""):
            console.print(stdout_line.strip())

        process.stdout.close()
        return_code = process.wait()

        # Check if the Docker build was successful
        if return_code == 0:
            console.print("[green]Docker image built successfully![/green]")
        else:
            # Capture and print stderr output in case of an error
            for stderr_line in iter(process.stderr.readline, ""):
                console.print(f"[bold red]{stderr_line.strip()}[/bold red]")
            console.print("[bold red]Docker build failed.[/bold red]")
            raise typer.Exit(code=1)

    except FileNotFoundError:
        console.print(
            "[bold red]Docker is not installed or not available in your PATH.[/bold red]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error during Docker build:[/bold red] {e}")
        raise typer.Exit(code=1)

    except FileNotFoundError:
        console.print(
            "[bold red]Docker is not installed or not available in your PATH.[/bold red]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error during Docker build:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def new():
    """
    A new kitchenai bento,app, or plugin project
    """

    cookiecutter("https://github.com/epuerta9/cookiecutter-bento.git", output_dir=".")


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
        "0.0.0.0:8001",
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
        "0.0.0.0:8001",
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


def _install_package(package_name: str) -> tuple[bool, str]:
    """
    Try to install a package using available package managers in order of preference:
    1. UV (fastest)
    2. Poetry (project-based)
    3. Hatch (project-based)
    4. Pip (fallback)

    Returns:
        tuple[bool, str]: (success, package_manager_used)
    """
    # Try UV first (fastest)
    try:
        subprocess.check_call(["uv", "pip", "install", package_name])
        return True, "uv"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try Poetry
    try:
        subprocess.check_call(["poetry", "add", package_name])
        return True, "poetry"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try Hatch
    try:
        subprocess.check_call(["hatch", "add", package_name])
        return True, "hatch"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback to pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True, "pip"
    except subprocess.CalledProcessError:
        return False, ""
