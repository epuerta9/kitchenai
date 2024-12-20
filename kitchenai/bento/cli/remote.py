
import typer
from django.conf import settings
from rich.console import Console
from rich.table import Table
from typing import Annotated
import requests
app = typer.Typer()
console = Console()



API_BASE_URL = "https://raw.githubusercontent.com/epuerta9/kitchenai/main"

@app.command("list")
def list():
    """List all available starter cookbooks."""
    response = requests.get(f"{API_BASE_URL}/bentos.json")
    if response.status_code != 200:
        console.print("[red]Error fetching cookbook list.[/red]")
        raise typer.Exit(code=1)

    bentos = response.json().get("bentos", [])
    if not bentos:
        console.print("[yellow]No Bentos available.[/yellow]")
        return

    # Create a table for the cookbooks
    table = Table(title="Available Starter Cookbooks")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Package Name", style="magenta")

    for bento in bentos:
        table.add_row(bento["name"], bento["description"], bento["package_name"])

    # Display the table
    console.print(table)



@app.command("copy")
def copy(
    source: Annotated[str, typer.Argument(help="Source bento name")],
    destination: Annotated[str, typer.Argument(help="Destination directory path")]
):
    """Copy a bento box files from remote repository to local directory"""
    import os
    import shutil
    from pathlib import Path
    import requests

    # Get bentos list
    response = requests.get(f"{API_BASE_URL}/bentos.json")
    if response.status_code != 200:
        console.print("[red]Error fetching bentos list.[/red]")
        raise typer.Exit(1)

    bentos = response.json().get("bentos", [])
    bento = next((b for b in bentos if b["name"] == source), None)

    if not bento:
        console.print(f"[red]Bento '{source}' not found[/red]")
        raise typer.Exit(1)

    # Create destination directory if it doesn't exist
    dest_path = Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)

    # Get repository contents
    repo_path = bento["path"]
    repo_url = f"https://api.github.com/repos/{repo_path}/contents"
    
    def download_files(url, local_path):
        response = requests.get(url)
        if response.status_code != 200:
            console.print(f"[red]Error accessing repository content at {url}[/red]")
            return

        contents = response.json()
        for item in contents:
            item_path = Path(local_path) / item["name"]
            
            if item["type"] == "dir":
                item_path.mkdir(exist_ok=True)
                download_files(item["url"], item_path)
            else:
                # Download file content
                file_response = requests.get(item["download_url"])
                if file_response.status_code == 200:
                    item_path.write_bytes(file_response.content)
                    console.print(f"[green]Downloaded: {item_path}[/green]")
                else:
                    console.print(f"[red]Failed to download: {item_path}[/red]")

    try:
        download_files(repo_url, dest_path)
        console.print(f"[green]Successfully copied bento '{source}' to '{destination}'[/green]")
    except Exception as e:
        console.print(f"[red]Error copying files: {str(e)}[/red]")
        raise typer.Exit(1)
