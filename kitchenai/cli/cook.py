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


@app.command("notebook")
def cook_notebook():
    """convert a notebook into an app.py module"""
    import nbformat
    from nbconvert import PythonExporter
    from llama_index.llms.groq import Groq
    import django 
    from llama_index.core import PromptTemplate
    from django.template import loader


    django.setup()

    import os
    # Load the notebook
    notebook_path = "playground.ipynb"
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Export to Python script
    exporter = PythonExporter()
    (script, resources) = exporter.from_notebook_node(notebook)

    with console.status(f"[cyan]Cooking your notebook...[/cyan]", spinner="dots"):


        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise("error GROQ_API_KEY NEEDED")
        llm = Groq(model="llama3-70b-8192", api_key=api_key)
        kitchenai_few_shot = loader.get_template('build_templates/app.tmpl')
        prompt = loader.get_template('build_templates/cook.tmpl')

        few_shot_rendered = kitchenai_few_shot.render()

        prompt_rendered = prompt.render()

        cook_prompt_template = PromptTemplate(
            prompt_rendered,
        )

        prompt_with_context = cook_prompt_template.format(context_str=script, few_shot_example=few_shot_rendered)

        response = llm.complete(prompt_with_context)

        # Save as .py file
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(response.text)

    # Display the table
    console.print("[cyan]cooked into an app.py![/cyan]")


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
