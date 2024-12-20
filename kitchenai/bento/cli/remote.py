
import typer
from django.conf import settings
from rich.console import Console
from rich.table import Table
from typing import Annotated
import os
import requests
app = typer.Typer()
console = Console()



API_BASE_URL = "https://raw.githubusercontent.com/epuerta9/kitchenai/main"

@app.command("list")
def list():
    """List all available remote bentos."""
    response = requests.get(f"{API_BASE_URL}/bentos.json")
    if response.status_code != 200:
        console.print("[red]Error fetching cookbook list.[/red]")
        raise typer.Exit(code=1)

    bentos = response.json().get("bentos", [])
    if not bentos:
        console.print("[yellow]No Bentos available.[/yellow]")
        return

    # Create a table for the cookbooks
    table = Table(title="Remote Bento Boxes")
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

    repo_url = "https://github.com/epuerta9/kitchenai"
    repo_path = "bento-community/kitchenai-bento-llama-index-starter"
    
    download_github_folder(repo_url, repo_path, destination)
    


def download_file(url, dest_path):
    """
    Downloads a file from the given URL to the destination path.

    :param url: URL of the file to download
    :param dest_path: Local destination path
    """
    print(f"Downloading {url} to {dest_path}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print(f"Failed to download file: {url} - {response.status_code}")
def download_github_folder(repo_url, folder_path, dest_dir):
    """
    Downloads the contents of a specific folder from a GitHub repository.

    :param repo_url: Base URL of the GitHub repo (e.g., https://github.com/username/repo)
    :param folder_path: Path to the folder in the repo (e.g., bento-community/kitchenai-bento-llama-index-starter)
    :param dest_dir: Local destination directory to save the contents
    """
    # Extract repo owner and name from the URL
    repo_parts = repo_url.rstrip("/").split("/")
    owner, repo = repo_parts[-2], repo_parts[-1]
    branch = "main"  # Change if the default branch is not 'main'

    # GitHub API URL to fetch contents of the folder
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_path}?ref={branch}"

    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch folder contents: {response.status_code} - {response.text}")
        return

    # Parse the JSON response
    folder_contents = response.json()
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for item in folder_contents:
        item_name = item["name"]
        item_path = os.path.join(dest_dir, item_name)
        if item["type"] == "file":
            # Download the file
            download_file(item["download_url"], item_path)
        elif item["type"] == "dir":
            # Recursively download the subdirectory
            download_github_folder(repo_url, f"{folder_path}/{item_name}", item_path)
