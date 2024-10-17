import typer


def main():
    typer.run(run)



def run(run: str):
    """
    Reads the kitchen config file, reads the application file and runs the KitchenAI server
    """
    typer.echo("this is a running message")
    