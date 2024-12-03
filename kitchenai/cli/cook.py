from pathlib import Path

import requests
import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer()
console = Console()



API_BASE_URL = "https://raw.githubusercontent.com/epuerta9/kitchenai-community/main"

@app.command("list")
def cook_list():
    """List all available starter cookbooks."""
    response = requests.get(f"{API_BASE_URL}/cookbooks.json")
    if response.status_code != 200:
        console.print("[red]Error fetching cookbook list.[/red]")
        raise typer.Exit(code=1)

    cookbooks = response.json().get("cookbooks", [])
    if not cookbooks:
        console.print("[yellow]No cookbooks available.[/yellow]")
        return

    # Create a table for the cookbooks
    table = Table(title="Available Starter Cookbooks")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    for cookbook in cookbooks:
        table.add_row(cookbook["name"], cookbook["description"])

    # Display the table
    console.print(table)


@app.command("select")
def cook_select(name: str):
    """Download a specific starter cookbook."""
    response = requests.get(f"{API_BASE_URL}/cookbooks.json")
    if response.status_code != 200:
        console.print("[red]Error fetching cookbook list.[/red]")
        raise typer.Exit(code=1)

    cookbooks = response.json().get("cookbooks", [])
    selected_cookbook = next((c for c in cookbooks if c["name"] == name), None)

    if not selected_cookbook:
        console.print("[red]Cookbook not found.[/red]")
        raise typer.Exit(code=1)

    files_to_download = ["app.py", "requirements.txt"]
    dest_path = Path.cwd()

    # Show spinner while downloading the files
    with console.status(f"[cyan]Downloading {name} cookbook...[/cyan]", spinner="dots"):
        for file in files_to_download:
            file_url = f"{API_BASE_URL}/{selected_cookbook['path']}/{file}"
            file_response = requests.get(file_url)

            if file_response.status_code == 200:
                with open(dest_path / file, "wb") as f:
                    f.write(file_response.content)
                console.print(f"[green]Downloaded {file} successfully.[/green]")
            else:
                console.print(f"[red]Error downloading {file}.[/red]")
                raise typer.Exit(code=1)
