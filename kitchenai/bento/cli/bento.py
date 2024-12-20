import logging
import typer
from django.conf import settings
from rich.console import Console
from rich.table import Table
from typing import Annotated
from .remote import app as remote_app

app = typer.Typer()
console = Console()

app.add_typer(remote_app, name="remote")

logger = logging.getLogger(__name__)

@app.command()
def select(package_name: Annotated[str, typer.Argument()]):
    """Select the bento box kitchenai will use"""
    bento_boxes = settings.KITCHENAI.get("bento", [])
    for bento in bento_boxes:
        if bento.get("name") == package_name:
            #add it to the selected bento box DB
            from kitchenai.bento.models import Bento
            try:
                # Try to get existing bento box
                bento_box = Bento.objects.first()
                if bento_box:
                    bento_box.name = package_name
                    bento_box.save()
                else:
                    # Create new bento box if none exists
                    bento_box = Bento.objects.create(name=package_name)
                
                # Add to core
                bento_box.add_to_core()
                console.print(f"Successfully selected bento box: {package_name}")
                
            except Exception as e:
                logger.error(f"Error selecting bento box: {e}")
                console.print(f"Error selecting bento box: {e}")
                return
            
        else:
            console.print(f"[red]Error:[/red] Bento box with name '{package_name}' not found.")

@app.command()
def list():
    """List all local KitchenAI bento boxes with their attributes."""
    bento_boxes = settings.KITCHENAI.get("bento", [])

    # Table for Selected Bento Box
    selected_table = Table(title="Selected Bento Box")
    selected_table.add_column("Name", style="cyan", no_wrap=True)
    selected_table.add_column("Updated At", style="magenta")

    try:
        from kitchenai.bento.models import Bento
        current_bento = Bento.objects.first()
        if current_bento:
            selected_table.add_row(current_bento.name, str(current_bento.updated_at))
        else:
            selected_table.add_row("ERROR:", "No bento box selected. Use 'bento select' to choose a bento box")
    except Exception as e:
        logger.error(f"Error getting selected bento box: {e}")
        selected_table.add_row("Error", "", "Could not retrieve selected bento box")

    console.print(selected_table)

    # Table for Available Bento Boxes
    if bento_boxes:
        available_table = Table(title="Available Bento Boxes")
        available_table.add_column("Name", style="cyan", no_wrap=True)
        available_table.add_column("Description", style="green")
        available_table.add_column("Tags", style="magenta")


        for bento in bento_boxes:
            name = bento.get("name", "N/A")
            # Skip the selected bento box to avoid duplication
            if current_bento and name == current_bento.name:
                continue
            available_table.add_row(
                name,
                bento.get("description", "N/A"),
                ",".join(bento.get("tags", ["N/A"]))
            )

        console.print(available_table)
    else:
        console.print("No bento boxes found.")



@app.command("pull")
def pull(name: str):
    """Pip install a specific bento and its package dependencies."""
    from dynamicPip import DynamicPip
    dynamic_pip = DynamicPip()

    # declare target package
    target_package = name

    # install
    console.print(f"[cyan]Installing bento package: [bold]{target_package}[/bold][/cyan]")
    rtn = dynamic_pip.install_package(target_package)
    if rtn == 0:
        console.print(f"[green]Successfully installed {target_package}![/green]")
    else:
        console.print(f"[red]Failed to install {target_package} (return code: {rtn})[/red]")

    console.print(f"[green]Successfully downloaded bento '{name}'![/green]")